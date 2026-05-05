#!/usr/bin/env bash
# Lumin app v0.0.6 — Anonymous JWT auth (zero-config).
#
# Replaces the manual bearer-token field with auto-authentication on
# first launch.  The app posts to /api/auth/anonymous, gets a JWT,
# stores it encrypted in flutter_secure_storage, and silently refreshes
# before expiry.  When the server's JWT secret is rotated every existing
# token becomes invalid; the app catches the next 401 and re-mints
# transparently — no APK rebuild, no token visible to the user, ever.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v006.sh
#   bash lumin-v006.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

echo "→ Updating Lumin app to v0.0.6 (auto-auth — zero manual token)…"

mkdir -p lib/data lib/features/settings/pages

# pubspec.yaml ----------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.6+6

environment:
  sdk: ">=3.4.0 <4.0.0"
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
  http: ^1.2.0
  shared_preferences: ^2.3.0
  flutter_secure_storage: ^9.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
EOF_PUBSPEC

# ── lib/data/auth_service.dart ──────────────────────────────────────────
cat > lib/data/auth_service.dart <<'EOF_AUTH_SERVICE'
/// Auth service — anonymous JWT lifecycle.
///
/// First launch: posts to ``/api/auth/anonymous`` and stores the JWT in
/// flutter_secure_storage (encrypted at-rest).  Subsequent calls reuse
/// the cached token until it's within the refresh window or has expired.
///
/// On a 401 from any API call, ``handleUnauthorized()`` clears the cached
/// JWT and forces the next request to re-mint anonymously.  This makes
/// server-side secret rotation invisible to the user — they see at most
/// a 200ms blip on one request.
import 'dart:async';
import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthError implements Exception {
  AuthError(this.message);
  final String message;
  @override
  String toString() => 'AuthError: $message';
}

/// Refresh the JWT this many seconds *before* expiry to avoid a race
/// where the token was valid when sent but expired by the time the
/// server validates it.
const int _kRefreshLeadSeconds = 86400;

class _CachedToken {
  _CachedToken({required this.token, required this.expiresAt});
  final String token;
  final DateTime expiresAt;

  bool get isExpired => DateTime.now().isAfter(expiresAt);
  bool get needsRefresh =>
      DateTime.now().isAfter(expiresAt.subtract(const Duration(seconds: _kRefreshLeadSeconds)));

  Map<String, dynamic> toJson() => {
        'token': token,
        'expiresAt': expiresAt.toIso8601String(),
      };

  static _CachedToken fromJson(Map<String, dynamic> j) => _CachedToken(
        token: j['token'] as String,
        expiresAt: DateTime.parse(j['expiresAt'] as String),
      );
}

class AuthService {
  AuthService({
    required this.baseUrl,
    FlutterSecureStorage? storage,
    http.Client? client,
  })  : _storage = storage ?? const FlutterSecureStorage(),
        _client = client ?? http.Client();

  final String baseUrl;
  final FlutterSecureStorage _storage;
  final http.Client _client;

  static const _kStorageKey = 'lumin.auth.jwt';

  // In-memory cache so we don't hit secure storage on every request.
  // Reset on signOut() and after handleUnauthorized().
  _CachedToken? _cached;

  /// Returns a JWT suitable for use in an Authorization: Bearer header.
  /// Mints, refreshes, or reuses the cached token transparently.
  Future<String> getValidToken() async {
    // 1. In-memory cache
    if (_cached != null && !_cached!.isExpired && !_cached!.needsRefresh) {
      return _cached!.token;
    }

    // 2. Disk-backed cache
    if (_cached == null) {
      _cached = await _loadFromStorage();
    }

    // 3. Refresh window — try to extend without re-minting
    if (_cached != null && !_cached!.isExpired && _cached!.needsRefresh) {
      try {
        await _refresh(_cached!.token);
        return _cached!.token;
      } catch (_) {
        // Refresh failed — fall through to anonymous mint
      }
    }

    // 4. Cached token still valid?
    if (_cached != null && !_cached!.isExpired) {
      return _cached!.token;
    }

    // 5. Mint a fresh anonymous token
    await _mintAnonymous();
    return _cached!.token;
  }

  /// Called by the API client when a request returns 401.  Drops the
  /// cached token so the next ``getValidToken`` re-mints from scratch.
  /// The caller should then retry the original request once.
  Future<void> handleUnauthorized() async {
    _cached = null;
    await _storage.delete(key: _kStorageKey);
  }

  /// Hard reset — used by Settings → "Reset connection".
  Future<void> signOut() async {
    await handleUnauthorized();
  }

  // ---- internals --------------------------------------------------------

  Future<_CachedToken?> _loadFromStorage() async {
    try {
      final raw = await _storage.read(key: _kStorageKey);
      if (raw == null) return null;
      return _CachedToken.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      // Corrupt entry — wipe so next mint starts clean.
      await _storage.delete(key: _kStorageKey);
      return null;
    }
  }

  Future<void> _persist(_CachedToken t) async {
    _cached = t;
    await _storage.write(key: _kStorageKey, value: jsonEncode(t.toJson()));
  }

  Future<void> _mintAnonymous() async {
    final uri = Uri.parse('${_trimSlash(baseUrl)}/api/auth/anonymous');
    final resp = await _client
        .post(uri, headers: const {'Accept': 'application/json'})
        .timeout(const Duration(seconds: 8));
    if (resp.statusCode != 200) {
      throw AuthError(
        'mint failed (${resp.statusCode}): ${_decodeDetail(resp.body)}',
      );
    }
    await _persist(_parseTokenResponse(resp.body));
  }

  Future<void> _refresh(String token) async {
    final uri = Uri.parse('${_trimSlash(baseUrl)}/api/auth/refresh');
    final resp = await _client
        .post(
          uri,
          headers: const {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({'token': token}),
        )
        .timeout(const Duration(seconds: 8));
    if (resp.statusCode != 200) {
      throw AuthError(
        'refresh failed (${resp.statusCode}): ${_decodeDetail(resp.body)}',
      );
    }
    await _persist(_parseTokenResponse(resp.body));
  }

  _CachedToken _parseTokenResponse(String body) {
    final j = jsonDecode(body) as Map<String, dynamic>;
    final token = j['token'] as String;
    final expSeconds = (j['exp_seconds'] as num).toInt();
    return _CachedToken(
      token: token,
      // Subtract 30s to give us margin against clock skew between
      // device and server.
      expiresAt: DateTime.now().add(Duration(seconds: expSeconds - 30)),
    );
  }

  static String _trimSlash(String s) =>
      s.endsWith('/') ? s.substring(0, s.length - 1) : s;

  static String _decodeDetail(String body) {
    if (body.isEmpty) return 'empty body';
    try {
      final j = jsonDecode(body);
      if (j is Map && j['detail'] != null) return '${j['detail']}';
    } catch (_) {}
    return body;
  }

  void dispose() => _client.close();
}
EOF_AUTH_SERVICE

# ── lib/data/api_client.dart ──────────────────────────────────────────
cat > lib/data/api_client.dart <<'EOF_API_CLIENT'
/// Thin HTTP client for the 360 Crypto Eye API.
///
/// Pulls a JWT from ``AuthService`` for every request.  On a 401 the
/// client clears the cached token, re-mints anonymously, and retries
/// the original request once — making server-side secret rotation
/// invisible to the user.
import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'auth_service.dart';

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
    required this.auth,
    this.timeout = const Duration(seconds: 8),
    this.maxRetries = 2,
    http.Client? httpClient,
  }) : _http = httpClient ?? http.Client();

  final String baseUrl;
  final AuthService auth;
  final Duration timeout;
  final int maxRetries;

  final http.Client _http;

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

  Future<Map<String, String>> _headers() async {
    final token = await auth.getValidToken();
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    return _request(() async {
      final h = await _headers();
      return _http.get(_uri(path, query), headers: h);
    });
  }

  Future<dynamic> post(String path, {Object? body}) async {
    final encoded = body == null ? null : jsonEncode(body);
    return _request(() async {
      final h = await _headers();
      return _http.post(_uri(path), headers: h, body: encoded);
    });
  }

  Future<dynamic> _request(Future<http.Response> Function() send) async {
    int attempt = 0;
    bool authRetried = false;
    Object? lastError;
    while (attempt <= maxRetries) {
      try {
        final resp = await send().timeout(timeout);

        // 401 → token rotated server-side; drop ours, re-mint, retry once.
        if (resp.statusCode == 401 && !authRetried) {
          authRetried = true;
          await auth.handleUnauthorized();
          continue; // doesn't increment attempt — auth retry is "free"
        }

        // 5xx → transient, retry with back-off.
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

  void dispose() => _http.close();
}
EOF_API_CLIENT

# ── lib/data/app_config.dart ──────────────────────────────────────────
cat > lib/data/app_config.dart <<'EOF_APP_CONFIG'
/// App-wide config + repository provider.
///
/// Two knobs only:
///   * dataSource — 'mock' (offline) or 'live' (HTTP backend)
///   * apiBaseUrl — e.g. https://api.luminapp.org
///
/// No bearer token field — the app authenticates anonymously on first
/// launch via ``/api/auth/anonymous`` and silently refreshes/re-mints
/// thereafter.  Server-side secret rotations are invisible to the user.
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';
import 'auth_service.dart';
import 'repository.dart';

enum DataSource { mock, live }

class AppConfig {
  AppConfig({
    required this.dataSource,
    required this.apiBaseUrl,
  });

  final DataSource dataSource;
  final String apiBaseUrl;

  AppConfig copyWith({
    DataSource? dataSource,
    String? apiBaseUrl,
  }) =>
      AppConfig(
        dataSource: dataSource ?? this.dataSource,
        apiBaseUrl: apiBaseUrl ?? this.apiBaseUrl,
      );

  static const _kSource = 'lumin.dataSource';
  static const _kBaseUrl = 'lumin.apiBaseUrl';

  static const defaultBaseUrl = 'https://api.luminapp.org';

  static Future<AppConfig> load() async {
    final p = await SharedPreferences.getInstance();
    final raw = p.getString(_kSource) ?? 'live';
    return AppConfig(
      dataSource: raw == 'mock' ? DataSource.mock : DataSource.live,
      apiBaseUrl: p.getString(_kBaseUrl) ?? defaultBaseUrl,
    );
  }

  Future<void> save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_kSource, dataSource == DataSource.live ? 'live' : 'mock');
    await p.setString(_kBaseUrl, apiBaseUrl);
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
  AuthService? _auth;

  AppConfig get config => _config;
  LuminRepository get repo => _repo;
  AuthService? get auth => _auth;

  Future<void> update(AppConfig next) async {
    setState(() {
      _config = next;
      _repo = _buildRepo(next);
    });
    await next.save();
  }

  /// Hard reset — wipes the on-device JWT.  Next API call will mint
  /// fresh anonymously.
  Future<void> resetConnection() async {
    await _auth?.signOut();
  }

  LuminRepository _buildRepo(AppConfig c) {
    if (c.dataSource == DataSource.live && c.apiBaseUrl.isNotEmpty) {
      _auth = AuthService(baseUrl: c.apiBaseUrl);
      return HttpRepository(LuminApiClient(
        baseUrl: c.apiBaseUrl,
        auth: _auth!,
      ));
    }
    _auth = null;
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
      oldWidget.state._config.apiBaseUrl != state._config.apiBaseUrl;
}
EOF_APP_CONFIG

# ── lib/features/settings/pages/api_keys_settings_page.dart ──────────────────────────────────────────
cat > lib/features/settings/pages/api_keys_settings_page.dart <<'EOF_API_KEYS'
/// API keys + backend connection.
///
/// Backend connection is now zero-config: the app authenticates anonymously
/// on first launch and silently refreshes thereafter.  This page only
/// exposes Mock/Live toggle, base URL (rarely changed), connection status,
/// and a "Reset connection" button that wipes the on-device JWT (mostly a
/// debugging aid — the next API call re-mints automatically anyway).
///
/// Binance API keys are unchanged — separate concern, not Lumin auth.
import 'package:flutter/material.dart';

import '../../../data/api_client.dart';
import '../../../data/app_config.dart';
import '../../../data/auth_service.dart';
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

  // Lumin backend — only base URL is user-editable.
  late final TextEditingController _baseUrlCtl;
  bool _liveMode = true;

  String? _testResult;
  bool _testing = false;

  @override
  void initState() {
    super.initState();
    final cfg = AppConfigScope.of(context).config;
    _baseUrlCtl = TextEditingController(text: cfg.apiBaseUrl);
    _liveMode = cfg.dataSource == DataSource.live;
  }

  @override
  void dispose() {
    _binanceKeyCtl.dispose();
    _binanceSecretCtl.dispose();
    _baseUrlCtl.dispose();
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
          _resetCard(),
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
  // Lumin backend (Mock/Live + base URL only — auth is automatic)
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
                            ? 'Auto-authenticated. No setup needed.'
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

  Widget _resetCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            const Icon(Icons.refresh, color: LuminColors.textMuted, size: 18),
            const SizedBox(width: LuminSpacing.md),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Reset connection',
                    style: TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Wipes the cached auth token. Next request re-authenticates.',
                    style: TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            TextButton(
              onPressed: _liveMode ? _resetConnection : null,
              child: const Text('Reset'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _runTest() async {
    final url = _baseUrlCtl.text.trim();
    if (url.isEmpty) {
      setState(() => _testResult = 'ERR: enter a base URL');
      return;
    }
    setState(() {
      _testing = true;
      _testResult = null;
    });
    final auth = AuthService(baseUrl: url);
    final client = LuminApiClient(baseUrl: url, auth: auth);
    try {
      final pulse = await client.get('/api/pulse');
      if (pulse is! Map) {
        if (!mounted) return;
        setState(() {
          _testing = false;
          _testResult = 'ERR: unexpected /api/pulse response';
        });
        return;
      }
      if (!mounted) return;
      setState(() {
        _testing = false;
        _testResult =
            'OK — auto-authenticated. Engine ${pulse['status']}, regime ${pulse['regime']}.';
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
    } finally {
      client.dispose();
      auth.dispose();
    }
  }

  Future<void> _resetConnection() async {
    await AppConfigScope.of(context).resetConnection();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Connection reset. Next request will re-authenticate.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  // ------------------------------------------------------------------
  // Binance (unchanged — session-only)
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
    );
    await scope.update(next);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_API_KEYS

echo "  ✓ auth_service + api_client + app_config + API keys settings"

echo "→ Bumping version → 0.0.6+6 — done"
echo "→ Stage + commit + push (then GitHub Actions builds APK)"

git add lib/ pubspec.yaml
git commit -m "feat(auth): v0.0.6 — anonymous JWT auto-auth, no manual token

First launch posts to /api/auth/anonymous, gets a JWT, stores encrypted
in flutter_secure_storage.  Subsequent calls reuse + silently refresh.
On 401 (server rotated secret) the client wipes its cache and re-mints
transparently — no token visible to the user, ever."

echo "✓ v0.0.6 ready.  'git push' to trigger APK build."
