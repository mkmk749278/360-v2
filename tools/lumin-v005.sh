#!/usr/bin/env bash
# Lumin app v0.0.5 — Backend wiring.
#
# Adds the repository pattern so every page can switch between built-in
# mock data and the live FastAPI backend at runtime.  Pages stay on
# mocks for now; the user-visible win is a real "Test connection"
# button in API keys settings that hits the engine's /api/health and
# /api/pulse to verify the backend before swapping over.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v005.sh
#   bash lumin-v005.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

echo "→ Updating Lumin app to v0.0.5 (backend wiring + repository pattern)…"

mkdir -p lib/data lib/features/settings/pages

# pubspec.yaml ----------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.5+5

environment:
  sdk: ">=3.4.0 <4.0.0"
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
  http: ^1.2.0
  shared_preferences: ^2.3.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
EOF_PUBSPEC

# ── lib/data/api_client.dart ──────────────────────────────────────────
cat > lib/data/api_client.dart <<'EOF_API_CLIENT'
/// Thin HTTP client for the 360 Crypto Eye API.
///
/// Stateless and reusable — give it a base URL + optional bearer token and
/// it'll dispatch GET / POST with sane defaults: 8-second timeout, 2 retries
/// on transient errors with exponential back-off, JSON decoding, ``ApiError``
/// wrapping for callers.
import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

class ApiError implements Exception {
  ApiError(this.statusCode, this.message);
  final int statusCode;
  final String message;

  @override
  String toString() => 'ApiError($statusCode): $message';
}

class LuminApiClient {
  LuminApiClient({
    required this.baseUrl,
    this.authToken,
    this.timeout = const Duration(seconds: 8),
    this.maxRetries = 2,
  });

  final String baseUrl;
  final String? authToken;
  final Duration timeout;
  final int maxRetries;

  Map<String, String> get _headers {
    final h = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    };
    final token = authToken;
    if (token != null && token.isNotEmpty) {
      h['Authorization'] = 'Bearer $token';
    }
    return h;
  }

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    final base = baseUrl.endsWith('/')
        ? baseUrl.substring(0, baseUrl.length - 1)
        : baseUrl;
    final pathPart = path.startsWith('/') ? path : '/$path';
    final raw = '$base$pathPart';
    final parsed = Uri.parse(raw);
    if (query == null || query.isEmpty) return parsed;
    final qp = <String, String>{};
    query.forEach((k, v) {
      if (v != null) qp[k] = '$v';
    });
    return parsed.replace(queryParameters: {
      ...parsed.queryParameters,
      ...qp,
    });
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    return _request(() => http.get(_uri(path, query), headers: _headers));
  }

  Future<dynamic> post(String path, {Object? body}) async {
    final encoded = body == null ? null : jsonEncode(body);
    return _request(
      () => http.post(_uri(path), headers: _headers, body: encoded),
    );
  }

  Future<dynamic> _request(Future<http.Response> Function() send) async {
    int attempt = 0;
    Object? lastError;
    while (attempt <= maxRetries) {
      try {
        final resp = await send().timeout(timeout);
        // Retry on 5xx — keep auth + payload errors loud.
        if (resp.statusCode >= 500 && attempt < maxRetries) {
          attempt += 1;
          await Future<void>.delayed(_backoff(attempt));
          continue;
        }
        if (resp.statusCode >= 400) {
          throw ApiError(resp.statusCode, _decodeError(resp.body));
        }
        if (resp.body.isEmpty) return null;
        return jsonDecode(resp.body);
      } on TimeoutException catch (e) {
        lastError = e;
      } on SocketException catch (e) {
        lastError = e;
      } on http.ClientException catch (e) {
        lastError = e;
      }
      attempt += 1;
      if (attempt > maxRetries) break;
      await Future<void>.delayed(_backoff(attempt));
    }
    throw ApiError(0, 'connection failed: $lastError');
  }

  Duration _backoff(int attempt) =>
      Duration(milliseconds: 200 * (1 << (attempt - 1).clamp(0, 4)));

  String _decodeError(String body) {
    if (body.isEmpty) return 'empty body';
    try {
      final j = jsonDecode(body);
      if (j is Map && j['detail'] != null) return '${j['detail']}';
    } catch (_) {}
    return body;
  }
}
EOF_API_CLIENT

# ── lib/data/repository.dart ──────────────────────────────────────────
cat > lib/data/repository.dart <<'EOF_REPOSITORY'
/// Repository abstraction — the single seam between UI and data source.
///
/// Pages call ``LuminRepository`` methods.  The concrete implementation
/// (``MockRepository`` for offline/preview, ``HttpRepository`` for live
/// engine) is chosen at app startup based on user preference.  Adding a
/// new data source (websocket, on-device cache, …) means writing a new
/// implementation; no page has to change.
import 'package:flutter/material.dart';

import '../shared/tokens.dart';
import 'api_client.dart';
import 'mock_data.dart';

class AutoModeStatus {
  const AutoModeStatus({
    required this.mode,
    required this.openPositions,
    required this.dailyPnlUsd,
    required this.dailyLossPct,
    required this.dailyKillTripped,
    required this.manualPaused,
    required this.currentEquityUsd,
    this.simulatedPnlUsd,
  });

  final String mode;
  final int openPositions;
  final double dailyPnlUsd;
  final double dailyLossPct;
  final bool dailyKillTripped;
  final bool manualPaused;
  final double currentEquityUsd;
  final double? simulatedPnlUsd;

  factory AutoModeStatus.fromJson(Map<String, dynamic> j) => AutoModeStatus(
        mode: j['mode'] as String,
        openPositions: (j['open_positions'] as num?)?.toInt() ?? 0,
        dailyPnlUsd: (j['daily_pnl_usd'] as num?)?.toDouble() ?? 0.0,
        dailyLossPct: (j['daily_loss_pct'] as num?)?.toDouble() ?? 0.0,
        dailyKillTripped: j['daily_kill_tripped'] as bool? ?? false,
        manualPaused: j['manual_paused'] as bool? ?? false,
        currentEquityUsd:
            (j['current_equity_usd'] as num?)?.toDouble() ?? 0.0,
        simulatedPnlUsd: (j['simulated_pnl_usd'] as num?)?.toDouble(),
      );
}

class AgentStat {
  const AgentStat({
    required this.evaluator,
    required this.setupClass,
    required this.displayName,
    required this.enabled,
    required this.attempts,
    required this.generated,
    required this.noSignal,
  });
  final String evaluator;
  final String setupClass;
  final String displayName;
  final bool enabled;
  final int attempts;
  final int generated;
  final int noSignal;

  factory AgentStat.fromJson(Map<String, dynamic> j) => AgentStat(
        evaluator: j['evaluator'] as String? ?? '',
        setupClass: j['setup_class'] as String? ?? '',
        displayName: j['display_name'] as String? ?? '',
        enabled: j['enabled'] as bool? ?? true,
        attempts: (j['attempts'] as num?)?.toInt() ?? 0,
        generated: (j['generated'] as num?)?.toInt() ?? 0,
        noSignal: (j['no_signal'] as num?)?.toInt() ?? 0,
      );
}

abstract class LuminRepository {
  /// True when the underlying source is the live engine (vs. mocks).
  bool get isLive;

  Future<MockEngineSnapshot> fetchPulse();
  Future<List<MockSignal>> fetchSignals({String status = 'all', int limit = 50});
  Future<List<MockPosition>> fetchPositions();
  Future<List<MockActivityEvent>> fetchActivity({int limit = 50});
  Future<AutoModeStatus> fetchAutoMode();
  Future<AutoModeStatus> setAutoMode(String mode);
  Future<List<AgentStat>> fetchAgents();
  Future<bool> healthCheck();
}

// ---------------------------------------------------------------------------
// MockRepository — wraps the constants in ``mock_data.dart``.
// ---------------------------------------------------------------------------

class MockRepository implements LuminRepository {
  const MockRepository();

  @override
  bool get isLive => false;

  @override
  Future<MockEngineSnapshot> fetchPulse() async => mockEngine;

  @override
  Future<List<MockSignal>> fetchSignals(
      {String status = 'all', int limit = 50}) async {
    final all = mockSignals;
    Iterable<MockSignal> filtered;
    switch (status) {
      case 'open':
        filtered = all.where((s) => s.status == 'ACTIVE');
        break;
      case 'closed':
        filtered = all.where((s) => s.status != 'ACTIVE');
        break;
      default:
        filtered = all;
    }
    return filtered.take(limit).toList();
  }

  @override
  Future<List<MockPosition>> fetchPositions() async => mockPositions;

  @override
  Future<List<MockActivityEvent>> fetchActivity({int limit = 50}) async =>
      mockActivity.take(limit).toList();

  @override
  Future<AutoModeStatus> fetchAutoMode() async => const AutoModeStatus(
        mode: 'paper',
        openPositions: 1,
        dailyPnlUsd: 12.84,
        dailyLossPct: 0.0,
        dailyKillTripped: false,
        manualPaused: false,
        currentEquityUsd: 1012.84,
        simulatedPnlUsd: 12.84,
      );

  @override
  Future<AutoModeStatus> setAutoMode(String mode) async =>
      // Mock can't actually switch — return a status with the requested mode
      // so the UI feedback feels right.
      AutoModeStatus(
        mode: mode,
        openPositions: 0,
        dailyPnlUsd: 0.0,
        dailyLossPct: 0.0,
        dailyKillTripped: false,
        manualPaused: false,
        currentEquityUsd: 1000.0,
      );

  @override
  Future<List<AgentStat>> fetchAgents() async {
    // Synthesise from mockSignals' setup_class distribution so the Agents
    // tab still renders something sensible offline.
    final names = <String, String>{
      'SR_FLIP_RETEST': 'The Architect',
      'LIQUIDITY_SWEEP_REVERSAL': 'The Counter-Puncher',
      'FAILED_AUCTION_RECLAIM': 'The Reclaimer',
      'QUIET_COMPRESSION_BREAK': 'The Coil Hunter',
      'VOLUME_SURGE_BREAKOUT': 'The Tracker',
      'BREAKDOWN_SHORT': 'The Crusher',
      'FUNDING_EXTREME_SIGNAL': 'The Contrarian',
      'WHALE_MOMENTUM': 'The Whale Hunter',
      'LIQUIDATION_REVERSAL': 'The Cascade Catcher',
      'CONTINUATION_LIQUIDITY_SWEEP': 'The Continuation Specialist',
      'DIVERGENCE_CONTINUATION': 'The Divergence Reader',
      'TREND_PULLBACK_EMA': 'The Pullback Sniper',
      'POST_DISPLACEMENT_CONTINUATION': 'The Aftermath Trader',
      'OPENING_RANGE_BREAKOUT': 'The Range Breaker',
    };
    return names.entries
        .map((e) => AgentStat(
              evaluator: e.key,
              setupClass: e.key,
              displayName: e.value,
              enabled: true,
              attempts: 0,
              generated: 0,
              noSignal: 0,
            ))
        .toList();
  }

  @override
  Future<bool> healthCheck() async => true;
}

// ---------------------------------------------------------------------------
// HttpRepository — talks to FastAPI backend.
// ---------------------------------------------------------------------------

class HttpRepository implements LuminRepository {
  HttpRepository(this.client);

  final LuminApiClient client;

  @override
  bool get isLive => true;

  @override
  Future<MockEngineSnapshot> fetchPulse() async {
    final j = (await client.get('/api/pulse')) as Map<String, dynamic>;
    return MockEngineSnapshot(
      status: j['status'] as String? ?? 'Healthy',
      regime: j['regime'] as String? ?? 'RANGING',
      regimePctTrending:
          (j['regime_pct_trending'] as num?)?.toDouble() ?? 0.0,
      todayPnlUsd: (j['today_pnl_usd'] as num?)?.toDouble() ?? 0.0,
      todayPnlPct: (j['today_pnl_pct'] as num?)?.toDouble() ?? 0.0,
      dailyLossBudgetUsd:
          (j['daily_loss_budget_usd'] as num?)?.toDouble() ?? 0.0,
      dailyLossUsedUsd:
          (j['daily_loss_used_usd'] as num?)?.toDouble() ?? 0.0,
      openPositions: (j['open_positions'] as num?)?.toInt() ?? 0,
      signalsToday: (j['signals_today'] as num?)?.toInt() ?? 0,
      uptime: _formatUptime((j['uptime_seconds'] as num?)?.toDouble() ?? 0.0),
    );
  }

  @override
  Future<List<MockSignal>> fetchSignals(
      {String status = 'all', int limit = 50}) async {
    final j = (await client
        .get('/api/signals', query: {'status': status, 'limit': limit})) as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_signalFromJson).toList();
  }

  @override
  Future<List<MockPosition>> fetchPositions() async {
    final j = (await client.get('/api/positions')) as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_positionFromJson).toList();
  }

  @override
  Future<List<MockActivityEvent>> fetchActivity({int limit = 50}) async {
    final j = (await client.get('/api/activity', query: {'limit': limit}))
        as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_activityFromJson).toList();
  }

  @override
  Future<AutoModeStatus> fetchAutoMode() async {
    final j = (await client.get('/api/auto-mode')) as Map<String, dynamic>;
    return AutoModeStatus.fromJson(j);
  }

  @override
  Future<AutoModeStatus> setAutoMode(String mode) async {
    await client.post('/api/auto-mode', body: {'mode': mode});
    // Re-fetch so the UI sees the post-change risk-gate state in one shot.
    return fetchAutoMode();
  }

  @override
  Future<List<AgentStat>> fetchAgents() async {
    final j = (await client.get('/api/agents')) as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(AgentStat.fromJson).toList();
  }

  @override
  Future<bool> healthCheck() async {
    try {
      final j = await client.get('/api/health');
      return j is Map && j['ok'] == true;
    } catch (_) {
      return false;
    }
  }

  // ---- json → mock-class adapters --------------------------------------

  MockSignal _signalFromJson(Map<String, dynamic> j) => MockSignal(
        id: j['signal_id'] as String? ?? '',
        symbol: j['symbol'] as String? ?? '',
        direction: j['direction'] as String? ?? 'LONG',
        setupName: (j['setup_class'] as String? ?? '').replaceAll('_', ' '),
        agentName: j['agent_name'] as String? ?? '',
        entry: (j['entry'] as num?)?.toDouble() ?? 0.0,
        sl: (j['stop_loss'] as num?)?.toDouble() ?? 0.0,
        tp1: (j['tp1'] as num?)?.toDouble() ?? 0.0,
        tp2: (j['tp2'] as num?)?.toDouble() ?? 0.0,
        tp3: (j['tp3'] as num?)?.toDouble() ?? 0.0,
        confidence: (j['confidence'] as num?)?.toDouble() ?? 0.0,
        tier: j['quality_tier'] as String? ?? 'B',
        status: j['status'] as String? ?? 'ACTIVE',
        pnlPct: (j['pnl_pct'] as num?)?.toDouble() ?? 0.0,
        minutesAgo: (j['minutes_ago'] as num?)?.toInt() ?? 0,
      );

  MockPosition _positionFromJson(Map<String, dynamic> j) => MockPosition(
        symbol: j['symbol'] as String? ?? '',
        direction: j['direction'] as String? ?? 'LONG',
        entry: (j['entry'] as num?)?.toDouble() ?? 0.0,
        currentPrice: (j['current_price'] as num?)?.toDouble() ?? 0.0,
        qty: (j['qty'] as num?)?.toDouble() ?? 0.0,
        pnlUsd: (j['pnl_usd'] as num?)?.toDouble() ?? 0.0,
        pnlPct: (j['pnl_pct'] as num?)?.toDouble() ?? 0.0,
        minutesOpen: (j['minutes_open'] as num?)?.toInt() ?? 0,
      );

  MockActivityEvent _activityFromJson(Map<String, dynamic> j) {
    final kind = j['kind'] as String? ?? 'OPEN';
    return MockActivityEvent(
      kind: kind,
      title: j['title'] as String? ?? '',
      subtitle: j['subtitle'] as String? ?? '',
      minutesAgo: (j['minutes_ago'] as num?)?.toInt() ?? 0,
      color: _colorForKind(kind),
    );
  }

  /// Brand-token mapping for activity event glyphs.  Mirrors the colours
  /// used by ``mock_data.dart`` so the live feed renders identically to
  /// the offline preview.
  static Color _colorForKind(String kind) {
    switch (kind) {
      case 'OPEN':
        return LuminColors.accent;
      case 'PRE_TP':
        return LuminColors.warn;
      case 'TP1':
      case 'TP2':
      case 'TP3':
        return LuminColors.success;
      case 'SL':
        return LuminColors.loss;
      case 'INVAL':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  static String _formatUptime(double seconds) {
    if (seconds <= 0) return '0s';
    final d = seconds ~/ 86400;
    final h = (seconds % 86400) ~/ 3600;
    if (d > 0) return '${d}d ${h}h';
    final m = (seconds % 3600) ~/ 60;
    return h > 0 ? '${h}h ${m}m' : '${m}m';
  }

}
EOF_REPOSITORY

# ── lib/data/app_config.dart ──────────────────────────────────────────
cat > lib/data/app_config.dart <<'EOF_APP_CONFIG'
/// App-wide config + repository provider.
///
/// Holds three knobs:
///   * dataSource — 'mock' (offline) or 'live' (HTTP backend)
///   * apiBaseUrl — e.g. https://api.luminapp.org
///   * apiAuthToken — Bearer token for the live API
///
/// Persisted via ``shared_preferences`` so the user's selection survives
/// app restarts.  Exposed to the widget tree through ``AppConfigScope``;
/// every page reads its repository via ``AppConfigScope.of(context).repo``.
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';
import 'repository.dart';

enum DataSource { mock, live }

class AppConfig {
  AppConfig({
    required this.dataSource,
    required this.apiBaseUrl,
    required this.apiAuthToken,
  });

  final DataSource dataSource;
  final String apiBaseUrl;
  final String apiAuthToken;

  AppConfig copyWith({
    DataSource? dataSource,
    String? apiBaseUrl,
    String? apiAuthToken,
  }) =>
      AppConfig(
        dataSource: dataSource ?? this.dataSource,
        apiBaseUrl: apiBaseUrl ?? this.apiBaseUrl,
        apiAuthToken: apiAuthToken ?? this.apiAuthToken,
      );

  static const _kSource = 'lumin.dataSource';
  static const _kBaseUrl = 'lumin.apiBaseUrl';
  static const _kToken = 'lumin.apiAuthToken';

  static const defaultBaseUrl = 'https://api.luminapp.org';

  static Future<AppConfig> load() async {
    final p = await SharedPreferences.getInstance();
    final raw = p.getString(_kSource) ?? 'mock';
    return AppConfig(
      dataSource: raw == 'live' ? DataSource.live : DataSource.mock,
      apiBaseUrl: p.getString(_kBaseUrl) ?? defaultBaseUrl,
      apiAuthToken: p.getString(_kToken) ?? '',
    );
  }

  Future<void> save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_kSource, dataSource == DataSource.live ? 'live' : 'mock');
    await p.setString(_kBaseUrl, apiBaseUrl);
    await p.setString(_kToken, apiAuthToken);
  }
}

/// Inherited widget exposing the active ``AppConfig`` + ``LuminRepository``.
/// Wrap the app in ``AppConfigScope`` once at boot; every descendant calls
/// ``AppConfigScope.of(context)`` to read the current config or push an
/// updated copy.  Updating triggers a rebuild of the whole subtree so
/// FutureBuilder-driven pages refetch automatically.
class AppConfigScope extends StatefulWidget {
  const AppConfigScope({super.key, required this.initial, required this.child});

  final AppConfig initial;
  final Widget child;

  static _AppConfigScopeState of(BuildContext context) {
    final inh = context.dependOnInheritedWidgetOfExactType<_InheritedConfig>();
    assert(inh != null, 'AppConfigScope missing in widget tree');
    return inh!._state;
  }

  @override
  State<AppConfigScope> createState() => _AppConfigScopeState();
}

class _AppConfigScopeState extends State<AppConfigScope> {
  late AppConfig _config = widget.initial;
  late LuminRepository _repo = _buildRepo(_config);

  AppConfig get config => _config;
  LuminRepository get repo => _repo;

  Future<void> update(AppConfig next) async {
    setState(() {
      _config = next;
      _repo = _buildRepo(next);
    });
    await next.save();
  }

  LuminRepository _buildRepo(AppConfig c) {
    if (c.dataSource == DataSource.live && c.apiBaseUrl.isNotEmpty) {
      return HttpRepository(LuminApiClient(
        baseUrl: c.apiBaseUrl,
        authToken: c.apiAuthToken,
      ));
    }
    return const MockRepository();
  }

  @override
  Widget build(BuildContext context) {
    return _InheritedConfig(state: this, child: widget.child);
  }
}

class _InheritedConfig extends InheritedWidget {
  const _InheritedConfig({required this.state, required super.child});
  final _AppConfigScopeState state;

  _AppConfigScopeState get _state => state;

  @override
  bool updateShouldNotify(_InheritedConfig oldWidget) =>
      oldWidget.state._config.dataSource != state._config.dataSource ||
      oldWidget.state._config.apiBaseUrl != state._config.apiBaseUrl ||
      oldWidget.state._config.apiAuthToken != state._config.apiAuthToken;
}
EOF_APP_CONFIG

# ── lib/main.dart ──────────────────────────────────────────
cat > lib/main.dart <<'EOF_MAIN'
/// Lumin app entry — boots the AppConfigScope before MaterialApp.
///
/// We load the persisted ``AppConfig`` once at startup so the repository
/// is ready before the first page renders.  No splash flicker: the load
/// is a single shared_preferences read, well under the first frame.
import 'package:flutter/material.dart';

import 'app/nav_shell.dart';
import 'data/app_config.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cfg = await AppConfig.load();
  runApp(LuminApp(initialConfig: cfg));
}

class LuminApp extends StatelessWidget {
  const LuminApp({super.key, required this.initialConfig});

  final AppConfig initialConfig;

  @override
  Widget build(BuildContext context) {
    return AppConfigScope(
      initial: initialConfig,
      child: MaterialApp(
        title: 'Lumin',
        debugShowCheckedModeBanner: false,
        theme: buildLuminTheme(),
        home: const NavShell(),
      ),
    );
  }
}
EOF_MAIN

# ── lib/features/settings/pages/api_keys_settings_page.dart ──────────────────────────────────────────
cat > lib/features/settings/pages/api_keys_settings_page.dart <<'EOF_API_KEYS'
/// API keys + backend connection.
///
/// v0.0.5 expansion: in addition to Binance API keys, this page now controls
/// the data source the entire app talks to.  Toggle Mock ↔ Live, set the
/// FastAPI base URL, paste the bearer token issued by `setup-vps-api.sh`,
/// and tap "Test connection" to verify before saving.
import 'package:flutter/material.dart';

import '../../../data/api_client.dart';
import '../../../data/app_config.dart';
import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class ApiKeysSettingsPage extends StatefulWidget {
  const ApiKeysSettingsPage({super.key});

  @override
  State<ApiKeysSettingsPage> createState() => _ApiKeysSettingsPageState();
}

class _ApiKeysSettingsPageState extends State<ApiKeysSettingsPage> {
  // Binance creds — session-only until backend wires up encrypted storage.
  final _binanceKeyCtl = TextEditingController();
  final _binanceSecretCtl = TextEditingController();
  bool _showBinanceSecret = false;
  bool _testnet = false;

  // Lumin backend.
  late final TextEditingController _baseUrlCtl;
  late final TextEditingController _tokenCtl;
  bool _showToken = false;
  bool _liveMode = false;

  String? _testResult;
  bool _testing = false;

  @override
  void initState() {
    super.initState();
    final cfg = AppConfigScope.of(context).config;
    _baseUrlCtl = TextEditingController(text: cfg.apiBaseUrl);
    _tokenCtl = TextEditingController(text: cfg.apiAuthToken);
    _liveMode = cfg.dataSource == DataSource.live;
  }

  @override
  void dispose() {
    _binanceKeyCtl.dispose();
    _binanceSecretCtl.dispose();
    _baseUrlCtl.dispose();
    _tokenCtl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API keys'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _backendCard(),
          const SizedBox(height: LuminSpacing.md),
          _testCard(),
          const SizedBox(height: LuminSpacing.md),
          _binanceCard(),
          const SizedBox(height: LuminSpacing.md),
          _envCard(),
          const SizedBox(height: LuminSpacing.md),
          _safetyCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  // ------------------------------------------------------------------
  // Lumin backend (data source toggle + base URL + token)
  // ------------------------------------------------------------------

  Widget _backendCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'LUMIN BACKEND',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _liveMode ? 'Live engine' : 'Mock data',
                        style: const TextStyle(
                          color: LuminColors.textPrimary,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        _liveMode
                            ? 'Calls FastAPI backend at the URL below'
                            : 'Reads built-in sample data — works offline',
                        style: const TextStyle(
                          color: LuminColors.textSecondary,
                          fontSize: 11,
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
                Switch(
                  value: _liveMode,
                  activeColor: LuminColors.accent,
                  onChanged: (v) => setState(() => _liveMode = v),
                ),
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('Base URL'),
            TextField(
              controller: _baseUrlCtl,
              enabled: _liveMode,
              autocorrect: false,
              keyboardType: TextInputType.url,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('https://api.luminapp.org'),
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('Bearer token'),
            TextField(
              controller: _tokenCtl,
              enabled: _liveMode,
              obscureText: !_showToken,
              autocorrect: false,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('Paste token from setup-vps-api.sh').copyWith(
                suffixIcon: IconButton(
                  icon: Icon(
                    _showToken ? Icons.visibility_off : Icons.visibility,
                    color: LuminColors.textMuted,
                    size: 18,
                  ),
                  onPressed: () => setState(() => _showToken = !_showToken),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _testCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: double.infinity,
              child: Material(
                color: Colors.transparent,
                borderRadius: BorderRadius.circular(LuminRadii.md),
                child: InkWell(
                  borderRadius: BorderRadius.circular(LuminRadii.md),
                  onTap: _testing || !_liveMode ? null : _runTest,
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
                    decoration: BoxDecoration(
                      color: _liveMode
                          ? LuminColors.accent.withOpacity(0.12)
                          : LuminColors.bgElevated,
                      borderRadius: BorderRadius.circular(LuminRadii.md),
                      border: Border.all(
                        color: _liveMode
                            ? LuminColors.accent.withOpacity(0.30)
                            : LuminColors.cardBorder,
                      ),
                    ),
                    alignment: Alignment.center,
                    child: _testing
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: LuminColors.accent,
                            ),
                          )
                        : Text(
                            _liveMode ? 'Test connection' : 'Enable Live to test',
                            style: TextStyle(
                              color: _liveMode
                                  ? LuminColors.accent
                                  : LuminColors.textMuted,
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
              ),
            ),
            if (_testResult != null) ...[
              const SizedBox(height: LuminSpacing.md),
              Text(
                _testResult!,
                style: TextStyle(
                  color: _testResult!.startsWith('OK')
                      ? LuminColors.success
                      : LuminColors.loss,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _runTest() async {
    final url = _baseUrlCtl.text.trim();
    final token = _tokenCtl.text.trim();
    if (url.isEmpty) {
      setState(() => _testResult = 'ERR: enter a base URL');
      return;
    }
    setState(() {
      _testing = true;
      _testResult = null;
    });
    final client = LuminApiClient(baseUrl: url, authToken: token);
    try {
      // Health is unauthenticated — confirms basic reachability.
      final health = await client.get('/api/health');
      if (health is! Map || health['ok'] != true) {
        if (!mounted) return;
        setState(() {
          _testing = false;
          _testResult = 'ERR: unexpected /api/health response';
        });
        return;
      }
      // Pulse requires auth — confirms the bearer token works.
      if (token.isNotEmpty) {
        await client.get('/api/pulse');
      }
      if (!mounted) return;
      setState(() {
        _testing = false;
        _testResult = token.isEmpty
            ? 'OK — health 200 (no auth tested; paste a token to verify)'
            : 'OK — health 200, pulse 200 (auth works)';
      });
    } on ApiError catch (e) {
      if (!mounted) return;
      setState(() {
        _testing = false;
        _testResult = 'ERR: ${e.message}';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _testing = false;
        _testResult = 'ERR: $e';
      });
    }
  }

  // ------------------------------------------------------------------
  // Binance (unchanged from v0.0.4 — session-only)
  // ------------------------------------------------------------------

  Widget _binanceCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'BINANCE FUTURES',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('API key'),
            TextField(
              controller: _binanceKeyCtl,
              autocorrect: false,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('Paste API key'),
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('API secret'),
            TextField(
              controller: _binanceSecretCtl,
              obscureText: !_showBinanceSecret,
              autocorrect: false,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('Paste API secret').copyWith(
                suffixIcon: IconButton(
                  icon: Icon(
                    _showBinanceSecret ? Icons.visibility_off : Icons.visibility,
                    color: LuminColors.textMuted,
                    size: 18,
                  ),
                  onPressed: () =>
                      setState(() => _showBinanceSecret = !_showBinanceSecret),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _envCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            const Icon(Icons.cloud_outlined, color: LuminColors.accent, size: 18),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _testnet ? 'Testnet' : 'Mainnet',
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _testnet
                        ? 'fapi-testnet.binance.com — fake balance, real APIs'
                        : 'fapi.binance.com — real money, real fills',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            Switch(
              value: _testnet,
              activeColor: LuminColors.warn,
              onChanged: (v) => setState(() => _testnet = v),
            ),
          ],
        ),
      ),
    );
  }

  Widget _safetyCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.md),
        decoration: BoxDecoration(
          color: LuminColors.warn.withOpacity(0.08),
          borderRadius: BorderRadius.circular(LuminRadii.md),
          border: Border.all(color: LuminColors.warn.withOpacity(0.25)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Row(
              children: [
                Icon(Icons.lock_outline, color: LuminColors.warn, size: 16),
                SizedBox(width: LuminSpacing.sm),
                Text(
                  'Required permissions',
                  style: TextStyle(
                    color: LuminColors.warn,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            SizedBox(height: LuminSpacing.sm),
            Text(
              '• Enable Reading\n'
              '• Enable Futures\n'
              '• DO NOT enable Withdrawals\n'
              '• Restrict to your IP if possible',
              style: TextStyle(
                color: LuminColors.warn,
                fontSize: 11,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ------------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------------

  Widget _label(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.xs),
      child: Text(
        text,
        style: const TextStyle(
          color: LuminColors.textSecondary,
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(
        color: LuminColors.textMuted,
        fontSize: 13,
      ),
      filled: true,
      fillColor: LuminColors.bgElevated,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: LuminSpacing.md,
        vertical: LuminSpacing.sm,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        borderSide: const BorderSide(color: LuminColors.cardBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        borderSide: const BorderSide(color: LuminColors.accent),
      ),
      disabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        borderSide: const BorderSide(color: LuminColors.cardBorder),
      ),
    );
  }

  Future<void> _save() async {
    final scope = AppConfigScope.of(context);
    final next = scope.config.copyWith(
      dataSource: _liveMode ? DataSource.live : DataSource.mock,
      apiBaseUrl: _baseUrlCtl.text.trim(),
      apiAuthToken: _tokenCtl.text.trim(),
    );
    await scope.update(next);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _liveMode
              ? 'Saved — app now reads from $_baseUrlText'
              : 'Saved — app now uses mock data',
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  String get _baseUrlText {
    final v = _baseUrlCtl.text.trim();
    return v.isEmpty ? 'mock' : v;
  }
}
EOF_API_KEYS

echo "  ✓ data layer (api_client, repository, app_config) + main + API keys settings"

echo "→ Bumping version → 0.0.5+5 — done"
echo "→ Stage + commit + push (then GitHub Actions builds APK)"

git add lib/ pubspec.yaml
git commit -m "feat(backend): v0.0.5 — repository pattern + live test connection

Adds the seam between UI and data source.  Pages still consume mocks
for now; v0.0.6 will swap them to FutureBuilder against the live API.

  - LuminApiClient — http with timeout, retries, bearer auth
  - LuminRepository (Mock + Http) — single seam, factory in app_config
  - AppConfigScope — InheritedWidget exposing the active repo
  - API keys settings — base URL, bearer token, real Test connection
    that hits /api/health and /api/pulse on the configured backend

Default data source: Mock.  Switch to Live once setup-vps-api.sh has
been run on the VPS and you have a base URL + bearer token in hand."

echo "✓ v0.0.5 ready.  'git push' to trigger APK build."
