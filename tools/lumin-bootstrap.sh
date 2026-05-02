#!/usr/bin/env bash
# Lumin app bootstrap — one-shot installer
# Run from inside the cloned lumin-app repo:
#   git clone https://github.com/mkmk749278/lumin-app.git
#   cd lumin-app
#   bash install-in-termux.sh
set -euo pipefail

if [ ! -d ".git" ]; then
  echo "ERROR: not in a git repo. Run: git clone https://github.com/mkmk749278/lumin-app.git && cd lumin-app && bash install-in-termux.sh"
  exit 1
fi

echo "→ Bootstrapping Lumin app files…"

# README.md ---------------------------------------------------------------
cat > README.md <<'EOF_README'
# Lumin

**AI Crypto Trading — Powered by 360 Crypto Eye**

Native Android app for the 360 Crypto Eye scalping signal engine. View live signals, configure auto-trade, switch between Live and Demo execution, and manage your Binance Futures account from your phone.

> **Lumin** is the consumer brand. **360 Crypto Eye** is the engine + signal-source brand. The Telegram channel and engine are unchanged.

---

## Status

🚧 **Bootstrap phase.** First Hello-Lumin APK builds via GitHub Actions. Real features land progressively — see the [engine repo's ACTIVE_CONTEXT.md](https://github.com/mkmk749278/360-v2/blob/main/ACTIVE_CONTEXT.md) for the live roadmap.

---

## Build

APK is built automatically by GitHub Actions on every push to `main`. Artifacts are downloadable from the [Actions tab](../../actions). Tagged releases publish a signed APK to [Releases](../../releases).

## Install on your phone

1. Go to the latest [Release](../../releases/latest)
2. Download `lumin-*.apk`
3. Allow "Install unknown apps" for your browser when prompted
4. Tap the APK to install

The app self-updates on launch — once installed, future versions arrive in-app.

---

## License

Proprietary — © 360 Crypto Eye. All rights reserved.
EOF_README

# .gitignore --------------------------------------------------------------
cat > .gitignore <<'EOF_GITIGNORE'
# Flutter / Dart
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
build/
.metadata
**/generated_plugin_registrant.*

# IDE
.idea/
*.iml
.vscode/

# Android
android/.gradle/
android/local.properties
android/key.properties
android/app/key.properties
android/app/release-keystore.jks
*.jks
*.keystore
local.properties

# iOS
ios/Pods/
ios/.symlinks/
ios/Flutter/Flutter.framework
ios/Flutter/Flutter.podspec
ios/Runner/GeneratedPluginRegistrant.*

# OS
.DS_Store
Thumbs.db

# Secrets — NEVER commit
*.env
.env
*.secret

# Termux scratch
*.tar.gz
EOF_GITIGNORE

# pubspec.yaml ------------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.1+1

environment:
  sdk: ">=3.4.0 <4.0.0"
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
EOF_PUBSPEC

# lib/main.dart -----------------------------------------------------------
mkdir -p lib
cat > lib/main.dart <<'EOF_MAIN'
/// Lumin — AI Crypto Trading
///
/// Bootstrap entry point.
import 'package:flutter/material.dart';

void main() {
  runApp(const LuminApp());
}

class LuminApp extends StatelessWidget {
  const LuminApp({super.key});

  static const Color _bgDeep = Color(0xFF0A0E1A);
  static const Color _bgCard = Color(0xFF0F1729);
  static const Color _accent = Color(0xFF7BD3F7);
  static const Color _textPrimary = Color(0xFFF8FAFC);
  static const Color _textSecondary = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lumin',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: _bgDeep,
        colorScheme: const ColorScheme.dark(
          primary: _accent,
          secondary: _accent,
          surface: _bgCard,
          onPrimary: _bgDeep,
          onSecondary: _bgDeep,
          onSurface: _textPrimary,
        ),
        textTheme: const TextTheme(
          displayLarge: TextStyle(color: _textPrimary, fontWeight: FontWeight.w300),
          displayMedium: TextStyle(color: _textPrimary, fontWeight: FontWeight.w300),
          headlineLarge: TextStyle(color: _textPrimary, fontWeight: FontWeight.w400),
          bodyLarge: TextStyle(color: _textPrimary),
          bodyMedium: TextStyle(color: _textSecondary),
          labelLarge: TextStyle(color: _textPrimary),
        ),
      ),
      home: const SplashPage(),
    );
  }
}

class SplashPage extends StatelessWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.bolt_outlined,
                size: 96,
                color: LuminApp._accent,
              ),
              const SizedBox(height: 24),
              Text(
                'Lumin',
                style: Theme.of(context).textTheme.displayMedium?.copyWith(
                      fontSize: 56,
                      letterSpacing: 4,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'AI Crypto Trading',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      letterSpacing: 2,
                      color: LuminApp._accent,
                    ),
              ),
              const SizedBox(height: 64),
              Text(
                'Powered by 360 Crypto Eye',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: LuminApp._bgCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LuminApp._accent.withOpacity(0.2)),
                ),
                child: const Text(
                  'v0.0.1 — bootstrap',
                  style: TextStyle(
                    color: LuminApp._textSecondary,
                    fontSize: 11,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
EOF_MAIN

# .github/workflows/build-apk.yml -----------------------------------------
mkdir -p .github/workflows
cat > .github/workflows/build-apk.yml <<'EOF_WORKFLOW'
name: Build APK

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [created]
  workflow_dispatch:

concurrency:
  group: build-apk-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build signed APK
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          distribution: zulu
          java-version: "17"

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          channel: stable
          cache: true

      - name: Flutter version
        run: flutter --version

      - name: Generate platform scaffolding (idempotent)
        run: |
          if [ ! -d "android" ]; then
            echo "First build — generating Android scaffolding"
            flutter create -t app --org=org.luminapp --platforms=android --project-name=lumin .
          else
            echo "android/ exists — skipping scaffolding"
          fi

      - name: Get dependencies
        run: flutter pub get

      - name: Decode keystore (release only)
        if: env.ANDROID_KEYSTORE_B64 != ''
        env:
          ANDROID_KEYSTORE_B64: ${{ secrets.ANDROID_KEYSTORE_B64 }}
        run: |
          mkdir -p android/app
          echo "$ANDROID_KEYSTORE_B64" | base64 -d > android/app/release-keystore.jks
          echo "storeFile=release-keystore.jks" > android/key.properties
          echo "storePassword=${{ secrets.ANDROID_KEYSTORE_PASSWORD }}" >> android/key.properties
          echo "keyAlias=${{ secrets.ANDROID_KEY_ALIAS }}" >> android/key.properties
          echo "keyPassword=${{ secrets.ANDROID_KEY_PASSWORD }}" >> android/key.properties

      - name: Build release APK
        run: |
          flutter build apk --release \
            --build-name=${{ github.ref_name }} \
            --build-number=${{ github.run_number }}

      - name: Rename APK with run number
        run: |
          cd build/app/outputs/flutter-apk
          mv app-release.apk lumin-${{ github.run_number }}.apk
          ls -la

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: lumin-apk-${{ github.run_number }}
          path: build/app/outputs/flutter-apk/lumin-*.apk
          retention-days: 30

      - name: Attach APK to GitHub Release
        if: github.event_name == 'release'
        uses: softprops/action-gh-release@v2
        with:
          files: build/app/outputs/flutter-apk/lumin-*.apk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF_WORKFLOW

# docs/keystore-setup.md --------------------------------------------------
mkdir -p docs
cat > docs/keystore-setup.md <<'EOF_KEYSTORE'
# Keystore Setup — One-Time

This is the **one-time** step that lets GitHub Actions sign release APKs. Done once on Termux on your phone, four secrets pasted into GitHub, then forgotten forever.

> **Skip for first build.** The pipeline ships unsigned debug APKs by default, which install fine for personal testing. You only need the keystore once you're publishing to alpha users or to Play Store.

## 1. Generate the keystore (Termux)

Install OpenJDK in Termux if not already:

```
pkg install openjdk-21
```

Generate the keystore:

```
keytool -genkey -v \
  -keystore lumin-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias lumin
```

Answer the prompts (use the same password for keystore + key when asked).

## 2. Encode keystore as base64

```
base64 lumin-release.jks > lumin-keystore.b64
cat lumin-keystore.b64
```

Copy the entire output.

## 3. Add four GitHub Secrets

Go to https://github.com/mkmk749278/lumin-app/settings/secrets/actions and add:

| Name | Value |
|---|---|
| ANDROID_KEYSTORE_B64 | (paste the base64 string) |
| ANDROID_KEYSTORE_PASSWORD | (your password) |
| ANDROID_KEY_ALIAS | lumin |
| ANDROID_KEY_PASSWORD | (same as keystore password) |

## 4. Backup the keystore

**Save lumin-release.jks to multiple places** — Google Drive, USB, Telegram saved messages. If you lose it, you can never sign updates with the same identity.
EOF_KEYSTORE

echo "→ Files created:"
find . -type f -not -path "./.git/*" -not -name "install-in-termux.sh" | sort

echo
echo "→ Staging + committing…"
git add README.md .gitignore pubspec.yaml lib/ .github/ docs/
git -c user.email="$(git config user.email || echo bot@lumin.local)" \
    -c user.name="$(git config user.name || echo Lumin Bootstrap)" \
    commit -m "feat: initial bootstrap

- Flutter app skeleton with Lumin brand theme (dark + cyan accent)
- Hello Lumin splash with 'Powered by 360 Crypto Eye' attribution
- GitHub Actions APK build pipeline (unsigned by default, signed when keystore secrets set)
- Idempotent platform scaffolding via flutter create
- Keystore setup docs in docs/keystore-setup.md

First push triggers CI. APK downloadable from Actions tab artifacts."

echo
echo "→ Done. Now push:"
echo
echo "  git push -u origin main"
echo
echo "GitHub Actions will run on push. Watch: https://github.com/mkmk749278/lumin-app/actions"
echo "First APK will be in Actions → latest run → Artifacts → lumin-apk-*"
