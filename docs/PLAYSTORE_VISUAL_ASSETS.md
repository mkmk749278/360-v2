# Play Console — visual assets guide

**Last updated:** 2026-05-20
**Use this for:** building the icon, feature graphic, and 4 phone screenshots for the v1 Play Console submission, using free tools only (Canva free tier + Android phone screenshot tool).

Companion to [`PLAYSTORE_LISTING_COPY.md`](./PLAYSTORE_LISTING_COPY.md) — that doc covers all the text fields; this one covers the images.

---

## Required assets — Play Console mandatory fields

| Asset | Size | Format | Max size | Required? |
|---|---|---|---|---|
| App icon | 512 × 512 px | 32-bit PNG (with alpha) | 1 MB | ✅ Yes |
| Feature graphic | 1024 × 500 px | JPG or 24-bit PNG (no alpha) | 1 MB | ✅ Yes |
| Phone screenshots | min 320 px, max 3840 px | PNG or JPG, 16:9 or 9:16 ratio | 8 MB each | ✅ Min 2, max 8 |
| Tablet screenshots | — | — | — | ⚪ Optional, skip for v1 |
| Promo video | YouTube URL | — | — | ⚪ Optional, skip for v1 |

**For v1:** ship 4 phone screenshots only. Tablet + promo video can be added in a future Play Console update without re-review.

---

## 1. App icon (512 × 512)

### Design constraints (from Play Console policy)

- **Foreground must not extend to the edges** — Play Console applies its own circular / squircle mask on different Android versions
- **Safe zone:** keep all important visual content within the centre 80% of the canvas (a circle of ~410 px diameter centred on 512 × 512)
- **No screenshots-of-the-app inside the icon** — Play rejects icons that contain UI mockups
- **No "Recommended" / "Top" / "#1" badges** — Play rejects these as deceptive
- **Solid background recommended** — radial gradients are fine; transparent PNG can produce ugly masks on some devices

### Recommended design — Canva path

The app already uses these brand tokens (from `lib/shared/tokens.dart`):

| Element | Hex |
|---|---|
| Background deep | `#0A0E1A` |
| Background card | `#0F1729` |
| Accent (cyan) | `#7BD3F7` |
| Text primary | `#F8FAFC` |

**Canva steps (30 minutes):**

1. Canva → "Create a design" → "Custom size" → **512 × 512 px**
2. Set background colour to `#0A0E1A` (use "Background colour" in left sidebar)
3. Add a **circle** element, fill `#7BD3F7`, position roughly upper-right at ~70% size of canvas — gives a "moon" / "spotlight" vibe consistent with the "Lumin" name (light)
4. Add a **bold sans-serif letter "L"** in `#F8FAFC` (white), centred, font size ~280 px — Inter, Outfit, or Space Grotesk all work. Position so the L sits over the bottom-left curve of the cyan circle.
5. (Optional) add a thin `#7BD3F7` ring around the canvas edge at 10 px inset for visual polish
6. Export as **PNG, transparent: OFF, 32-bit not required** — but Canva exports 32-bit PNGs by default which is fine

**That's it.** Minimum-viable icon that's policy-compliant, brand-consistent, and reads at small sizes (Play Store recommended icon is sometimes 48 × 48 on certain devices — the "L" must remain legible). Total time ~15 min.

### What NOT to put on the icon

- Trading-chart imagery (Cornix, Bitsgap have these → fine — but it's not necessary and adds review-time scrutiny)
- Specific symbols (₿, Ξ) — keeps the icon symbol-agnostic; matches the "75 pairs" reality
- Profit / chart-up imagery (₹↑ / 📈 etc.) — reviewers flag these as promotional

---

## 2. Feature graphic (1024 × 500)

This is the banner that appears at the top of your Play Store listing page. **No app screenshots in it** — Play wants this to communicate the value prop, not duplicate the screenshot strip below.

### Recommended design — Canva path

1. Canva → "Create a design" → "Custom size" → **1024 × 500 px**
2. Background: same `#0A0E1A` deep
3. Optional subtle gradient: linear gradient from `#0A0E1A` (left) to `#0F1729` (right)
4. Left half (~50% of width): the app name + tagline stack
   - **Lumin** — `#F8FAFC`, bold, font size ~96 px
   - Tagline below: **Crypto Futures Signals + Binance Automation** — `#94A3B8`, font size ~32 px
5. Right half: a stylised cyan "L" mark matching the icon (or a chart-ish geometric line, but keep it abstract — no actual price chart, no green / red candles)
6. Optional small risk note at the bottom: **18+ • Not financial advice** — `#64748B`, font size ~20 px
7. Export as **PNG, transparent: OFF**

Total time ~15 min.

### What NOT to put on the feature graphic

- Specific yield figures ("+47% in 30 days" — banned)
- Specific leverage figures ("Up to 125× leverage" — banned)
- Logos of partner companies / exchanges (Binance has its own brand guidelines — using their logo here without permission is a separate violation)
- App screenshots (Play wants the feature graphic to be supplementary to the screenshot strip, not redundant)

---

## 3. Phone screenshots (4 of them)

### Goal — communicate the product in 4 frames

Treat the screenshot strip as a 4-slide deck where each slide makes one specific claim. The reviewer's eye spends ~2 seconds per screenshot before deciding to scroll or tap.

### Recommended 4-frame sequence

| # | Surface | Claim it communicates |
|---|---|---|
| **1** | Trade tab — Signals feed with recent dispatches visible | "Real-time crypto trading signals streamed to you" |
| **2** | Trade tab — Recent Activity card with mixed PLACED / REJECTED entries | "See every order placement with plain-English status" |
| **3** | Settings → Auto-trade page — sliders visible (notional, leverage cap) + region gate visible | "You control position size, leverage, region" |
| **4** | Settings → Server-side auto-trade — connect form with the prominent-disclosure card visible | "Trade-only API key, IP-whitelisted, withdraws disabled" |

These 4 communicate the full value prop:
1. **Signal delivery** (what the app does)
2. **Transparency** (Recent Activity card — what's happening on your behalf)
3. **Control** (per-user knobs)
4. **Security** (key restrictions, prominent disclosure)

### How to capture them

**On your Android phone:**

1. Install the latest signed AAB or APK (via Closed Testing track once submitted, OR sideload the APK from CI artifacts)
2. Open the app → complete sign-in
3. Make sure the screen looks "active" — for screenshot #1, scroll the signals feed so a couple of real signal cards are visible. For #2, the Recent Activity card should have at least one PLACED and one REJECTED entry — set your notional to $50 (small wallet) and let Binance reject a couple in normal usage to populate this naturally
4. Take a native screenshot (volume-down + power on most Android devices)
5. Find the screenshot in your gallery
6. The Play Console accepts these directly — no editing needed if your phone is OLED or AMOLED at standard density (most modern phones produce 1080 × 2400 or 1440 × 3200 which is well within Play limits)

### Optional polish — Canva mockup frame

If the raw screenshots feel too "plain", Canva has free "Mockup → Phone" templates that wrap your screenshot in a phone-bezel frame. **This is optional** — most modern Play Store listings show raw screenshots; the bezel-frame style is more 2019-era. Skip if uncertain.

### What NOT to capture

- A blank empty-state screen ("No signals yet")
- The first-run consent gate (Play reviewers see it once + don't want it as a marketing image)
- Any screen with hard-coded dollar amounts or yield numbers
- Any screen with actual user phone numbers / Binance credentials visible (redact if necessary before uploading)
- A debug / dev banner / "Mock data" warning visible — Play rejects these as deceptive

---

## 4. Quick-start sequence (90 min total)

If you want to ship the Closed Testing submission today, follow this order:

1. **Phone screenshots first (20 min)** — install the AAB/APK on your phone, populate the Trade-tab views with realistic data, capture 4 screenshots. This is the highest-time-budget item and can't be parallelised; do it first while the app's running.
2. **Icon (15 min)** — Canva 512×512 per §1 above. Export PNG.
3. **Feature graphic (15 min)** — Canva 1024×500 per §2. Export PNG.
4. **Play Console upload (30 min)** — open Play Console → new app → paste from [`PLAYSTORE_LISTING_COPY.md`](./PLAYSTORE_LISTING_COPY.md) into each field → upload the 6 image files (1 icon + 1 feature graphic + 4 screenshots) → upload AAB to Closed Testing → submit.
5. **Tester URL (10 min)** — Play Console generates a Closed Testing opt-in URL after submission. Copy it. DM 12+ Telegram subscribers with a one-line "Tap this URL on Android, then download Lumin from the Play Store" message.

The 14-day continuous-opt-in clock starts when the 12th tester opts in. After that you can promote to Production.

---

## 5. Future Play Console updates (post-v1)

After Closed Testing is approved, you can edit the listing without re-review for most fields:

- **No review required** for: description text edits, screenshot swaps, icon updates, feature-graphic updates, support-email change, category re-tag
- **Re-review required** for: country additions, target-audience changes, Data Safety form changes, new AAB upload

So once v1 lands, iterating on the screenshots / icon / copy is cheap. Get the bones right, polish later.
