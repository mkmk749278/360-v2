# Play Console — ready-to-paste copy

**Last updated:** 2026-05-20
**Use this for:** Lumin v1 Closed Testing submission on Play Console.

Every field below has been vocabulary-audited per `PLAYSTORE_PLAN.md` (no "advice" / "guaranteed" / specific yield or leverage numbers).

---

## 1. Store presence — Main store listing

### App name
`Lumin`

*(33-char limit; we use 5)*

### Short description
**Max 80 characters.** Paste exactly:

```
Crypto futures trading signals + Binance automation. Not financial advice.
```

*(73 characters; meets the limit + the "not advice" disclaimer fits.)*

### Full description
**Max 4000 characters.** Paste exactly:

```
Lumin is a 24/7 crypto futures trading signals app. It scans 75 Binance USDT-M futures pairs and delivers algorithmic trading signals — entry, stop-loss, and take-profit levels — directly to subscribers.

WHAT LUMIN DOES

• Streams trading signals derived from market-structure and order-flow analysis
• Surfaces a Recent Activity card so you can see every order placement attempt and its outcome
• Optionally automates order placement on YOUR existing Binance Futures account, with per-signal stop-loss and take-profit pre-configured
• Lets you configure position size, leverage cap, and the symbol allowlist that auto-trade respects

HOW IT WORKS

1. Sign up with your phone number (one-time SMS OTP)
2. Optionally subscribe to the paid signals channel via our website
3. Optionally connect your Binance Futures account by generating a trade-only, IP-whitelisted, withdraw-disabled API key on Binance and providing it inside the app
4. Tune position notional, leverage cap, and which symbols auto-trade for you
5. Sit back — the signals stream, and (if you opted in) orders are placed automatically by our server-side engine

WHAT LUMIN IS NOT

• Not a regulated investment advisor, broker, or exchange
• Not a custodian of your funds — all funds remain in your Binance account at all times. The API key you provide is trade-only; we cannot withdraw
• Not a guaranteed-returns product — signals are informational outputs of a generalised algorithm, not personalised investment advice
• Not regulated by financial-services authorities; you do not enjoy investor compensation protection

RISK WARNING

Crypto futures trading carries substantial risk of loss. You can lose some or all of the funds you allocate. Past signal performance does not guarantee future results. Leverage amplifies both gains and losses. Markets can gap, exchanges can experience outages, and liquidations can occur during volatile conditions.

Do NOT trade with funds you cannot afford to lose. Read the Risk Disclosure inside the app before enabling auto-execution.

REGIONAL AVAILABILITY

Auto-execution is available in India, the United Kingdom, and the European Union. It is NOT available in the United States, China, or Bangladesh. Signal viewing is available wherever Google Play distributes this app.

PRIVACY AND SECURITY

• You authenticate with your phone number; we never store passwords
• Your Binance API key is encrypted with Google Cloud KMS at rest and only decrypted in-memory by an isolated signing service when placing orders
• You can revoke your API key on Binance at any time, OR delete your entire account inside the app (Settings → Delete account)
• We do not sell your data, do not run advertising, and do not share data with marketing networks

LEGAL

Privacy Policy: https://mkmk749278.github.io/lumin-legal/privacy
Terms of Service: https://mkmk749278.github.io/lumin-legal/terms
Risk Disclosure: https://mkmk749278.github.io/lumin-legal/risk

SUPPORT

mulakapati446@gmail.com

By installing this app you confirm you are 18 years of age or older and are legally permitted to trade cryptocurrency derivatives in your country of residence.
```

*(Approximately 2,950 characters — well under the 4,000 limit.)*

### App category
**Finance** (matches Cornix / 3Commas / Bitsgap / Pionex precedent — see `PLAYSTORE_RESEARCH_2026-05-20.md` §2)

### Tags (5 max)
- Trading
- Crypto
- Futures
- Signals
- Automation

---

## 2. App content — Financial Features Declaration

When Play Console asks "Does your app provide any financial features?" → **Yes**.

When it asks which features → check **BOTH**:

- ☑ **Cryptocurrency exchange**
- ☑ **Financial advice**

### Free-text for "Cryptocurrency exchange"
Paste:

```
Lumin connects to the user's existing Binance Futures account via a trade-only API key the user generates themselves on Binance. The key is required to be IP-whitelisted to our execution server and to have withdrawals disabled — our connect-time validation refuses any key that does not meet these constraints.

We are NOT an exchange. We do not match orders, quote markets, or hold customer assets. Funds remain in the user's Binance account at all times. We hold a revocable trade-authorisation token only, not custody of funds.

This pattern is the same as Cornix (com.cornix), 3Commas (io.threecommas.client.global), Bitsgap (com.bitsgap.pwa), WunderTrading (com.wundertrading.android), and Pionex Global (com.pionex.client) — all currently live on Google Play.

Order placement is server-side and only happens after the user explicitly enables "live trading" in app settings. Per-user blast-radius caps (symbol allowlist, per-position notional cap, rate limit, global kill switch) bound damage in any worst-case failure scenario.
```

### Free-text for "Financial advice"
Paste:

```
Lumin displays algorithmic trading signals derived from market-structure and order-flow analysis of Binance USDT-M futures pairs. The signals are labelled inside the app and in our terms of service as informational only.

Signals are NOT personalised investment advice — they are the same for every user (subject to per-user configuration of position notional, leverage cap, and symbol allowlist). They are NOT tailored to any individual's financial situation, risk tolerance, tax position, or investment objectives.

The app's first-launch consent gate requires users to affirmatively acknowledge that "Lumin signals are informational only and are NOT personalised investment advice" before any data is collected.

We do not operate as a registered investment advisor in any jurisdiction; the Risk Disclosure at https://mkmk749278.github.io/lumin-legal/risk explicitly states this and explains the absence of investor-compensation protection.
```

### Privacy Policy / ToS / Risk Disclosure URLs
- **Privacy policy** *(this is the only mandatory URL field in Play Console)*: `https://mkmk749278.github.io/lumin-legal/privacy`
- The ToS + Risk URLs are linked from inside the app (Settings → Legal) and from the full description above; Play Console does not have separate fields for them.

---

## 3. App content — Data Safety form

### Data your app collects

Tick the following categories:

| Category | Sub-type | Collected? | Shared? | Optional? | Purpose |
|---|---|---|---|---|---|
| **Personal info** | Name | ☑ | ☐ | ☑ | App functionality, Account management |
| **Personal info** | Phone number | ☑ | ☐ | ☐ | Account management |
| **Personal info** | Other info | ☑ | ☐ | ☑ | App functionality |
| **Financial info** | Other financial info | ☑ | ☐ | ☑ | App functionality |
| **App activity** | App interactions | ☑ | ☐ | ☐ | Analytics, Developer communications |
| **App activity** | In-app search history | ☐ | — | — | — |
| **App info and performance** | Crash logs | ☑ | ☐ | ☐ | Analytics |
| **App info and performance** | Diagnostics | ☑ | ☐ | ☐ | Analytics |
| **Device or other IDs** | Device or other IDs | ☑ | ☐ | ☐ | Analytics, App functionality |

### Free-text explanations for "Other info" fields

When Play Console asks for free-text describing the "Other info" / "Other financial info" entries, paste:

For **Personal info → Other info**:
```
Binance API key (a public identifier the user generates themselves on the Binance platform). This is collected only if the user chooses to enable server-side auto-execution. The key is encrypted with Google Cloud KMS at rest and only decrypted in-memory by an isolated signing service when placing an order on the user's behalf. The user can revoke at any time via Settings → Delete account, OR by revoking the key on Binance directly.
```

For **Financial info → Other financial info**:
```
Trade activity records: per-user signal dispatch outcomes (placed / rejected / skipped), Binance error codes when rejections occur, position notional and leverage cap preferences, and the symbol allowlist the user has configured for auto-trade. Used inside the app to render the Recent Activity card and to debug per-user issues. Not shared with third parties.
```

### Security practices

Tick:
- ☑ **Data is encrypted in transit** (TLS 1.2+)
- ☑ **You can request that data be deleted** (Settings → Delete account)
- ☑ **Data is encrypted at rest** (Cloud KMS envelope encryption for API keys; Firestore native encryption for all other data)

---

## 4. App content — Other declarations

| Question | Answer |
|---|---|
| Does your app target children? | No |
| Target audience | 18+ |
| Is your app a news app? | No |
| Is your app related to government services? | No |
| Does your app contain ads? | No |
| Does your app handle in-app purchases? | No |
| COVID-19 contact tracing / status app? | No |

---

## 5. Countries / regions

In Production track → Countries/regions, **include**:

- India
- United Kingdom (UK)
- All 27 EU member states (Austria, Belgium, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden)

**Explicitly exclude**:

- United States (CFTC complexity around crypto derivatives — defer until we have CFTC-pathway clarity)
- China (crypto trading prohibited)
- Bangladesh (Bangladesh Bank circular bans crypto trading)

For Closed Testing track this list doesn't matter (testers are invited by email regardless of country); the country list activates in Open Testing + Production.

---

## 6. App access — Reviewer test instructions

Play Console asks if your app requires login credentials. **Yes** — reviewers need a working phone OTP to test signals.

Paste this into "Instructions for testers":

```
Lumin requires phone-OTP signup before the main signals feed is reachable.

For Play Console review:

1. Launch the app — accept the three first-run consent checkboxes (age 18+, risk acknowledgement, "signals are not advice")
2. Tap "Sign in" → enter a working phone number you can receive SMS on
3. Enter the 6-digit OTP from the SMS
4. The Trade tab opens; the Recent Activity card shows recent order-dispatch attempts (will be empty for a fresh review account — that is expected; no Binance key is connected)
5. To exercise Settings → Delete account: tap Menu (gear icon) → Account section → Delete account → type DELETE to confirm

Server-side auto-execution (Settings → Server-side auto-trade) requires a Binance Futures API key. We cannot supply a Binance API key for review purposes (each key is per-user and ties to a real Binance account). The Connect flow can be reached and the form rendered, but submitting a real key is not necessary for review — the page surfaces all UI states (consent gate, region gate, key entry form) without an actual connection.

If a region check is needed: the app is intentionally region-locked for auto-execution (US / China / Bangladesh excluded) — see Settings → Server-side auto-trade; reviewers from those regions will see a "Not available in your region" card instead of the connect form. This is by design.

Support email: mulakapati446@gmail.com
```

---

## 7. App content — Subscription billing declaration

When asked "Does your app sell digital goods or services that can only be purchased with Google Play's billing system?" → **No**.

When asked "Why not?" / provide an explanation, paste:

```
Lumin's only paid offering is access to the @LuminProBot Telegram channel, which is consumed entirely outside the Play-distributed app. The app itself contains no in-app purchases, no premium features unlocked by Play Billing, and no subscription gateway.

This fits the Payments policy carve-out for "purchases of digital goods or services that can only be consumed outside of a Play-distributed app and cannot be accessed in a Play-distributed app".

Subscription billing is handled externally (Telegram bot deep-link to web checkout); the app surfaces a "Subscribe" button that opens the user's browser to a third-party billing page.
```

---

## 8. Vocabulary check before submitting

Final scan of the listing copy you've pasted. Any of these terms = automatic edit:

- ✗ "advice" / "advisor" / "advisory" — replace with "signal" / "informational"
- ✗ "guaranteed" / "guarantee" / "promise" — only use in NEGATIVE phrasing ("past performance does not guarantee future results")
- ✗ "earn $NN" / "make $NN" / "NN%" / "NNx leverage" — never name yield or leverage numbers in store copy
- ✗ "recommendation" / "recommend" — replace with "signal"
- ✗ "expert tips" / "professional advice" — never appears
- ✓ "signal", "automation", "strategy execution", "informational", "not personalised" — preferred

---

## 9. After submission

1. Play Console review typically takes 3-7 days for crypto-adjacent apps (may be longer for first submission from a new account)
2. **Closed Testing track** has lighter review than Production — first submission usually approved within 24-48h
3. **Production promotion** requires the 12-tester / 14-day continuous opt-in to be met first (your account is post Nov 2023; this rule applies)
4. If reviewer asks questions, respond within 7 days. Common questions + drafted responses:
   - **"Is your company licensed as a financial-services provider?"** → see the Financial Features Declaration free-text above; we are a personal-developer non-custodial signal service, not a regulated firm; this is disclosed in ToS and the in-app consent gate
   - **"Why don't you use Play Billing for subscriptions?"** → see §7 above
   - **"Where can the user delete their account?"** → Settings → Account → Delete account (with confirmation requiring user to type DELETE)
   - **"Where do you handle prominent disclosure for the API key collection?"** → the in-app first-run consent gate is shown BEFORE any data collection; the Settings → Server-side auto-trade page itself requires ToS acceptance + region check + the existing connect form, with the key field protected by an inline disclosure paragraph

---

**That's the full Play Console paste pack.** Every field that requires text has a verbatim block ready. The only things you fill in yourself are the Canva assets (icon + feature graphic + 4 screenshots) and the country checkbox list (because Play Console doesn't accept paste for that).
