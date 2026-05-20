# Lumin on Google Play — Policy & Path Research

**Date:** 2026-05-20
**Scope:** Can we publish the Lumin Android app (crypto futures scalping signals + opt-in server-side auto-execution on user's Binance Futures account) to the Google Play Store? What does the path look like?
**Methodology:** WebSearch + WebFetch on official Google Play Console Help URLs, India FIU-IND publications, and competitor Play Store listings. Authoritative pages on `support.google.com/googleplay/...` and `play.google.com/store/apps/...` reject direct fetch (HTTP 403), so claims are anchored to URLs plus search-snippet quotation. **Where the snippet itself is the only source, I flag the claim as "snippet-only".**

---

## TL;DR

- **Publishing is possible**, with realistic risk. Crypto trading-bot / signal apps that route orders to **third-party exchanges via user-supplied API keys** are *not* the primary target of Google Play's October 2025 Cryptocurrency Exchanges and Software Wallets policy (that policy targets *custodial* exchanges/wallets in 15 named jurisdictions — and **India is not on the list**). Cornix, 3Commas, Bitsgap, WunderTrading, Coinrule, and Pionex are all live on Play Store.
- **However**, four things will be scrutinised on review: (1) the **Financial features declaration** (mandatory for any app with financial features), (2) **prominent disclosure + consent** for collecting the Binance API key, (3) **risk disclaimers** in the listing + first-run UI, and (4) **Play Billing** treatment for the paid Telegram subscription.
- **Play Billing for the subscription is almost certainly NOT required** — the digital content (Telegram channel) is consumed entirely outside the Play-distributed app. We should still document this carefully.
- **India regulator path:** the **FIU-IND VASP registration** question is the more serious unknown — our trade-execution service arguably falls under "instruments enabling control over virtual digital assets" in the FATF-aligned PMLA definition. This is a separate compliance track from Play Store, but Google may flag it during review since India is our developer home market.
- **Realistic timeline:** ~6–10 weeks from "decision to ship" to a production listing, assuming first-attempt reviewer back-and-forth and no pivot needed. Closed Testing can be live in 1–2 weeks.

---

## Section 1 — Play Store policy landscape (current as of May 2026)

### 1.1 Financial Services policy
**URL:** https://support.google.com/googleplay/android-developer/answer/9876821 (Financial Services policy)
**URL:** https://support.google.com/googleplay/android-developer/answer/13849271 (Financial features declaration)

Per the Play Console Help summary cited by Google itself: *"Google Play does not allow apps that expose users to deceptive or harmful financial products and services [...] defined as those related to the management or investment of money and cryptocurrencies, including personalized advice."* — quoted from the policy via search snippet (snippet-only verbatim; page itself returns 403 to non-browser fetchers).

> *"If your app contains or promotes financial products and services, you must comply with state and local regulations for any region or country that your app targets — for example, include specific disclosures required by local law. Any app that contains any financial features must complete the Financial features declaration form within Play Console."* (snippet-only)

**Fit with Lumin:** We will be classified as having financial features — specifically the **Cryptocurrency exchange** sub-category (because we initiate orders on the user's exchange) and **Financial advice** sub-category (because we surface signals). Per https://support.google.com/googleplay/android-developer/answer/13849271 the declaration enumerates: cryptocurrency wallet, cryptocurrency exchange, tokenized digital asset (NFT) sales/trading/awards, stock trading and portfolio management, crowdfunding and chit funds, support services, credit monitoring and reporting, **financial advice**, insurance, and other.

We are an **edge case** — not a true custodial exchange, but more than just an information service. Expect to declare **both** "cryptocurrency exchange" (with a textual explanation that orders execute on user's third-party Binance account via user-issued API key) **and** "financial advice" (with a textual disclaimer that signals are not investment advice).

### 1.2 Cryptocurrency Exchanges & Software Wallets policy
**URL:** https://support.google.com/googleplay/android-developer/answer/16329703 (current canonical policy)
**Effective:** October 29, 2025.
**Supporting analysis:** https://www.ainvest.com/news/google-play-enforces-15-market-crypto-wallet-licensing-rules-october-29-2025-2508/, https://www.ccn.com/education/crypto/google-play-crypto-wallet-licensing-us-eu-rules-explained/, https://manimama.eu/what-will-google-play-s-updated-policy-for-crypto-apps-look-like-an-overview-of-the-changes/

The 15 jurisdictions where Google requires *crypto-asset licensing* before listing/updating a crypto exchange or custodial wallet app: **Bahrain, Canada, Hong Kong, Indonesia, Israel, Japan, Philippines, South Africa, South Korea, Switzerland, Thailand, UAE, UK, US, and the EU (all 27 member states as one bloc)** — per ainvest.com and ccn.com (the official page is 403 to fetch).

**India is NOT on the list.** Per ccn.com summary: *"If your targeted location is not on the list, you may continue to publish cryptocurrency exchanges and software wallets. However, due to the rapidly evolving regulatory landscape worldwide, developers are expected to obtain any additional licensure requirements per local laws. Google Play may also request further information regarding compliance in given jurisdictions."*

**Crucial scope clarification:** *"Non-custodial wallets — apps where users control their own private keys — are excluded from the licensing requirements"* (https://www.fxstreet.com/cryptocurrencies/news/google-clarifies-non-custodial-wallets-not-part-of-recent-ban-on-unlicensed-crypto-exchanges-and-wallets-202508132319). Lumin holds **no user funds** and holds **no private keys**; it holds an exchange-issued API key. Our model is closer to the trading-bot pattern (Cornix, 3Commas, Bitsgap, Pionex outside USA, WunderTrading, Coinrule) — all of which are currently live on Play Store. There is no clause we can find that *expressly* names "trading bot" or "signal service" as in-scope.

**Ambiguity:** the policy says *"crypto-asset exchange"* in scope. An app that programmatically executes orders on a third-party exchange could plausibly be argued as "facilitating exchange." The developer-community thread https://support.google.com/googleplay/android-developer/thread/380480270/clarification-on-play-store-policy-for-automated-trading-liquidity-management-apps-crypto-related shows a developer explicitly asking Google for this clarification — useful evidence the line is fuzzy and Google answers case-by-case. **We should expect reviewer questions and have a clear written answer ready.**

**Futures specifically:** the policy and its supporting docs make **no distinction between spot and derivatives**. This is meaningful — it means there is no explicit ban on a Futures-routing app, but also no safe harbour.

### 1.3 Restricted Financial Products policy
**URL (Ads, not Play):** https://support.google.com/adspolicy/answer/15188218 (Complex Speculative Financial Products)
**URL (Ads, not Play):** https://support.google.com/adspolicy/answer/2464998 (Financial products and services)

These are **Google Ads** policies, not Play Store policies — they govern whether we can *buy ads* for the app, not whether we can list it. Per the Ads policy: *"Due to the inherent complexities and risks involved in trading complex speculative financial products like Contracts for Difference (CFD), financial spread betting, rolling spot forex (often referred to as 'Forex' or 'FX'), and related forms of speculative products, Google only allows advertisements in select locations and only if [...] the advertiser is a licensed provider or aggregator"* (snippet-only).

**Binary options are banned outright** from Google Ads and from Play (https://www.leaprate.com/binary-options/platform/google-play-bans-binary-options-trading-apps/). We do not offer binary options.

**Crypto Futures with leverage** are not explicitly named in the Restricted Financial Products list. They are speculative, and our marketing copy must avoid language that resembles binary options ("guaranteed wins", "all-or-nothing"). The principal Play Store risk is **deceptive behaviour** if returns are promised. Mitigation: explicit "no guarantee" language in store description + first-run modal.

### 1.4 Payments policy / Google Play Billing
**URL:** https://support.google.com/googleplay/android-developer/answer/10281818 (Payments policy)

Critical clause from the policy (via search snippet):

> *"Purchases that are not supported by Google Play's billing system include purchases or rentals of physical goods [...] and purchases of physical services [...] Additionally, purchases of digital goods or services that can only be consumed outside of a Play-distributed app and cannot be accessed in a Play-distributed app do not require Google Play's billing system. Examples include ringtones usable on the device but not in the app; web-only content never consumed in the app; and apps that manage cloud service platforms but don't provide access to that cloud storage in-app."*

And:

> *"Examples of 1:1 online paid services that do not require the use of Google Play's billing system include education or hobby classes [...] health coaching [...] and specialist advisory services (such as financial guidance)."*

**Our subscription unlocks Telegram channel access.** That content is delivered via Telegram, a separate app — never *in* our Play-distributed app. This squarely fits the "digital goods or services that can only be consumed outside of a Play-distributed app" exception. **Play Billing is not required for the Telegram subscription.** The "1:1 specialist advisory services" carve-out is a secondary supporting argument.

**Risk:** if we ever surface the signal stream *inside* the app behind a paywall, that paywalled in-app content **does** trigger Play Billing requirements. The safe design: in-app signals stream is **free** (already what we plan), auto-trade is **free** but gated to API-connected users, and the Telegram channel + signal-history-export remains the paid product, sold off-Play.

**Alternative billing in India:** for any in-app digital purchase we ever do add, https://support.google.com/googleplay/android-developer/answer/13306652 confirms India developers can elect alternative billing with a 4% service-fee reduction (so net ~26% / ~11% instead of 30% / 15%). https://support.google.com/googleplay/android-developer/answer/13821247 (user-choice billing) is the formal program.

### 1.5 User Data policy + Data Safety form
**URL:** https://support.google.com/googleplay/android-developer/answer/10144311 (User Data policy)
**URL:** https://support.google.com/googleplay/android-developer/answer/10787469 (Data Safety section)
**URL:** https://support.google.com/googleplay/android-developer/answer/11150561 (Prominent disclosure best practices)

The Data Safety form taxonomy includes 14 categories; *"Financial Information"* with sub-types *"User payment info"*, *"Purchase history"*, *"Credit score"*, *"Other financial info"* (snippet: *"user salary or debts"*).

**Binance API key** is not a category that maps cleanly. It's not "credentials to a financial account" in Google's defined taxonomy (which targets login credentials). Closest fits:
- **Personal info → Other info** — declare the API key here with a written explanation in the privacy policy
- **Financial info → Other financial info** — defensible because the key authorises financial actions

We should declare it under **both** (form allows multi-select). The privacy policy must spell out:
1. We collect a *trade-only*, *IP-whitelisted*, *withdraw-disabled* API key.
2. It is stored KMS-encrypted on our VPS.
3. It is used exclusively to place orders matching dispatched signals on the user's Binance account.
4. User can revoke at any time from app + from Binance.

**Prominent disclosure + runtime consent**: per https://support.google.com/googleplay/android-developer/answer/11150561, the disclosure *"must accompany and immediately precede a request for user consent [...] You may not access or collect any personal and sensitive data until the user consents."* Translation: before we read the API key the user types/pastes, we must show a screen explaining what it is, why we need it, how it's stored, and require an affirmative tap. We cannot put this only in the description or in the privacy policy.

### 1.6 Permissions
With Lumin we likely need only `INTERNET` (and `POST_NOTIFICATIONS` on Android 13+ for signal alerts). **No dangerous permissions, no background-location, no SMS, no contacts.** This is a strong position — minimal permissions reduces review friction substantially.

`POST_NOTIFICATIONS` requires runtime consent on Android 13+; that's standard and not policy-flagged.

### 1.7 Target Audience policy
**URL:** https://support.google.com/googleplay/android-developer/answer/9899234 (Target Audience and Content)

Crypto trading apps in the IARC questionnaire receive ratings of **PEGI 12 / ESRB Teen** typically, sometimes **17+/Mature** depending on how the developer answers questions about "simulated gambling" and "real money transactions." Pionex shows **"Rated for 3+"** in PEGI (snippet) — they chose to answer that the trading feature is not "simulated gambling" and that "real money transactions" outside the app aren't ratings-relevant.

**Recommendation for Lumin:** answer the IARC questionnaire honestly; expect **PEGI 12 / ESRB Teen** at most because we're not gambling. Add a **first-run age confirmation** ("I am 18 or older") gate at the app level — this is *not* required by the rating but **is** prudent for India (where trading apps generally expect 18+) and signals to reviewers that we treat the product as adult.

### 1.8 Spam / Repetitive content
N/A (our app is a single, distinct utility). Skipping.

### 1.9 Country/region availability
The Cryptocurrency Exchanges & Software Wallets policy gates *country availability* not just app approval. Per https://support.google.com/googleplay/android-developer/answer/16329703 (snippet): *"If you don't have the required registration or licensing information for certain locations, remove them from your app's targeting countries/regions."*

**Practical implication for Lumin:** since we are non-custodial AND the policy excludes non-custodial, the *country-gating* requirement should not apply to us. But to minimise review friction we should **proactively exclude obviously hostile jurisdictions**: China, Bangladesh (crypto-trading banned), and (defensively) the **US** at launch — because US derivatives regulation (CFTC) is genuinely thorny and not worth the risk for a Phase 1 product.

**Recommended launch geo set:** India, UK, EU (no US, no China). Expand once Production is stable.

---

## Section 2 — How competitors do it

All competitors below were verified live on Google Play as of May 2026. The data-safety + permissions sections of each listing are not directly fetch-able (403), so I record what is recoverable via AppBrain mirrors, Aptoide mirrors, and search snippets.

| Competitor | App ID | URL | Status |
|---|---|---|---|
| **Cornix** | `com.cornix` | https://play.google.com/store/apps/details?id=com.cornix | Live, ~63k installs lifetime, Finance category, dev "Cornix 10 LTD" (Israel) |
| **3Commas** | `io.threecommas.client.global` | https://play.google.com/store/apps/details?id=io.threecommas.client.global | Live, allows in-app subscription on Android (off iOS) |
| **Bitsgap** | `com.bitsgap.pwa` | https://play.google.com/store/apps/details?id=com.bitsgap.pwa | Live, ~800k traders cited in copy, 16+ CEX/DEX integrations |
| **Pionex (global)** | `com.pionex.client` | https://play.google.com/store/apps/details?id=com.pionex.client | Live, 1M+ installs, *says "doesn't collect or share any user data"* in Data Safety (notable; possibly under-declared) |
| **Pionex US** | `com.pionex.us.client` | https://play.google.com/store/apps/details?id=com.pionex.us.client | Separate listing for US — Pionex has FinCEN MSB license |
| **WunderTrading** | `com.wundertrading.android` | https://play.google.com/store/apps/details?id=com.wundertrading.android | Live, 4.4 stars / 196 reviews, signals + bots |
| **Wunderbit (legacy listing)** | `eu.wunderbit.trading_web` | https://play.google.com/store/apps/details?id=eu.wunderbit.trading_web | Live, 5k+ installs, dev "Infinite Software SIA" (Latvia) |
| **Coinrule** | `com.coinrule.crypto_app_currency_..._coinrule` | (long ID) https://play.google.com/store/apps/details?id=com.coinrule.crypto_app_currency_stocks_shares_defi_trading_investing_auto_trade_bot_automated_coinrule | Live, but **explicitly states in description "The app is the monitoring version; to build rules please go on the web app"** — they bifurcated to avoid in-app bot configuration |

### Observed patterns

1. **Category:** All list under **Finance** (not Tools, not Business).
2. **Content rating:** Mostly **Everyone / 3+ / Teen** (Pionex confirms 3+). None go Mature 17+. They argue this is a utility, not gambling.
3. **Data Safety:** Wide variance. Pionex under-declares ("doesn't collect or share any user data") — that's risky and ill-advised for us; we should over-declare to be safe. Cornix and 3Commas have privacy policies that disclose API-key collection on the web side.
4. **In-app subscription model:**
   - **3Commas** uses **Google Play Billing on Android for subscriptions** (per their help center).
   - **Coinrule, Bitsgap, Cornix, WunderTrading** all push subscription to **website** — this is the dominant pattern. They use the app as a "monitor + control" surface and sell paid plans off-Play.
   - **Pionex** monetises via trading fees on its own exchange, not subscriptions, so the question doesn't apply directly.
5. **Disclaimers in description:** Cornix Terms of Use (https://cornix.io/terms/) explicitly: *"Services are not, nor should they be considered as, the provision of investment advice, portfolio management, financial advice, cryptocurrency exchange or custody or any other financial service. [...] The Services pose a high risk of financial loss [...] not regulated by financial or investor protection laws."* This exact pattern is what Lumin should mirror.
6. **Regional restrictions:** Pionex maintains a separate US-targeted listing (com.pionex.us.client) gated behind MSB license. Indicates **separate listings per regulated jurisdiction is a viable pattern**.
7. **Permissions:** All competitors request roughly `INTERNET` + `POST_NOTIFICATIONS` + `READ_NETWORK_STATE`. No exotic permissions. We can match this.
8. **Auto-trading positioning:** Universally framed as **"automation"**, **"bots"**, **"strategy execution"** — never as "guaranteed profits" or "advice". Cornix description: *"trading automation"*. Bitsgap: *"trade smarter 24/7 with automation"*. Coinrule: *"set up rules for buying and selling based on your desired conditions"*. **Lumin should adopt the same vocabulary.**

### Apps NOT on Play Store
I did not find any *signal-only / auto-execution* competitor that has been **delisted** post-2025 policy. Cornix, 3Commas, Bitsgap, Pionex, WunderTrading, and Coinrule all survived the October 2025 cut. This is the strongest possible evidence that the path is open.

---

## Section 3 — Specific risk areas for Lumin

### 3.1 Server-side execution of Futures orders vs. read-only portfolio tracking
**Materially different from a policy POV?** **Yes, but not in a blocking way.**

A read-only portfolio app (Delta-style) is a pure information utility. Lumin actively *places* trades. The closest direct analogue is **3Commas / Cornix / Bitsgap** — all use the exact same pattern (user-issued API key, server-side execution, no custody of funds). All three are live on Play. The pattern is *de facto* accepted.

**Reviewer-facing question we should pre-answer in the Financial features declaration free-text:**
> *"Lumin connects to the user's existing Binance Futures account via an API key the user generates themselves. The key is restricted to trade-only (withdraw disabled) and IP-whitelisted to our VPS. We never custody user funds; we hold a revocable trade-authorisation token. Order placement is automated only after the user explicitly enables 'live trading' in app settings."*

### 3.2 Leveraged trading exposure
Leverage is set **on Binance**, by the user, on the Binance side. Lumin reads the user's chosen leverage and respects it; we do not enable leverage. From a Play Store policy POV this is **the same situation as Cornix/Bitsgap** — which are live.

**Risk:** if our marketing copy says "10× returns" or "earn X% per week using 25× leverage" we trigger deceptive-behaviour and potentially restricted-products review. Mitigation: **never name a specific leverage multiplier or yield target in the store listing or app copy.** Frame as: *"Automates execution of signals on your Binance Futures account. You set the leverage, position size, and risk limits."*

### 3.3 India-specific issues — RBI / SEBI / FIU
**Reference:** https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/india/, https://fiuindia.gov.in/pdfs/downloads/VDA08012026.pdf (FIU AML/CFT Guidelines for VDAs, 8 Jan 2026)

- **RBI:** does not directly licence VDA service providers. No RBI registration required for our pattern.
- **SEBI:** does not regulate crypto VDA. Out of scope.
- **FIU-IND:** the binding regulator. Per the Ministry of Finance March 2023 notification, "VDA Service Providers" are reporting entities under PMLA. The four named activities include *"safekeeping or administration of virtual digital assets or instruments enabling control over virtual digital assets"* (https://www.legal500.com/developments/thought-leadership/the-requirement-of-fiu-ind-registration-and-its-ramifications-for-the-virtual-digital-asset-industry/).

  **Lumin's status under this clause is contested.** Holding a user's API key arguably is an *"instrument enabling control over virtual digital assets"* — we can move (trade, not withdraw) the user's assets. A conservative legal reading says we **should register with FIU-IND** as a Reporting Entity. A liberal reading says: the assets remain in the user's Binance account, not ours; we facilitate but do not control. Cornix (Israel), 3Commas, Bitsgap (Estonia/EU) have not registered with FIU-IND and continue to serve Indian users — so far without FIU enforcement against signal/bot services specifically. FIU has, however, issued show-cause notices to **offshore exchanges** (Binance, KuCoin, etc.) for non-registration (https://www.pib.gov.in/PressReleasePage.aspx?PRID=1991372).

  **Recommendation:** consult an Indian crypto-VDA lawyer before Production. For Closed Testing and Open Testing, this is not a Play Store blocker (Google does not check FIU registration for India — India is not on the 15-jurisdiction list). For full Production it is a **business-side compliance risk** independent of Google.

- **GST:** subscription revenue from Indian residents is GST-applicable at 18%. Off-Play side-business issue, not Play Store gate.

### 3.4 Subscription model + billing
**Conclusion (from 1.4 above):** Play Billing is **not required** for the Telegram-channel subscription because the content lives entirely outside the app. We should:

1. **Not** offer in-app subscription purchase (no Play Billing integration in v1).
2. The app shows a "Subscribe" button that opens our website in the device browser. This is the **"external content links"** path, which Google clarified as allowed for *content consumed outside the app*.
3. The app remains free to install and free to use in "signals-display-only" mode.
4. Auto-execution is a *capability* gated on the user having an active subscription, verified by our backend against the user's account — not a Play-Billing-purchased item.

**Watch-out:** the moment we paywall an in-app feature, we owe Play Billing. So keep the in-app surface free; sell only the off-Play product.

### 3.5 "Advice" vs. "Signal" vs. "Recommendation"
- **"Signal"** is the safest term in 2026 (matches Cornix, 3Commas, signal-marketplace vernacular). Google's Financial features declaration has a separate "financial advice" sub-category, suggesting "signal" reads as distinct from "advice".
- **"Recommendation"** is closer to "advice" and harder to defend — avoid.
- **"Advice"** in Lumin copy triggers the financial-advice sub-category in the declaration and arguably brings personalised-advice scrutiny (Google explicitly mentions "personalized advice" in the no-deceptive-financial-products clause).
- **"Trade idea"** and **"strategy execution"** are also safe.

**Recommendation:** standardise on **"signal"** + **"strategy execution"** + **"trade automation"**. Never use **"advice"**, **"recommendation"**, **"guidance"**, **"expert tips"**.

---

## Section 4 — Publish-readiness checklist

### Store listing artefacts (Play Console requirements)
- [ ] **App icon**: 512×512 PNG, 32-bit, max 1 MB
- [ ] **Feature graphic**: 1024×500 JPG/PNG, max 1 MB
- [ ] **Phone screenshots**: 2–8 screenshots, min 320 px, max 3840 px, 16:9 or 9:16 ratio
- [ ] **(Optional) 7-inch tablet screenshots** + **10-inch tablet screenshots**
- [ ] **(Optional) Promo video**: YouTube URL
- [ ] **Short description**: ≤ 80 characters
- [ ] **Full description**: ≤ 4000 characters — must include risk disclaimer block
- [ ] **App category**: Finance
- [ ] **App tags**: 5 max from controlled vocabulary
- [ ] **Content rating questionnaire (IARC)** — declare no gambling, no simulated wagering, no user-generated content; expect Teen / PEGI 12

### In-app surfaces (legally required)
- [ ] **Privacy policy URL** — hosted on stable HTTPS, must mention API-key collection, KMS encryption, retention, deletion request channel. Linked from Play Console + in-app Settings.
- [ ] **Terms of Service URL** — Cornix-style risk language: "not financial advice, high risk of loss, no protection by financial regulators."
- [ ] **Support email or web form** — required by Play Console.
- [ ] **Risk disclosure document** — separate from ToS; must say "you may lose all funds" + "past performance does not guarantee future results."
- [ ] **First-run risk modal** (in app): "By tapping Continue you confirm (a) you are 18+, (b) you understand crypto futures trading involves substantial risk of loss, (c) Lumin signals are not financial advice." Affirmative button required.
- [ ] **Prominent disclosure screen** before API-key entry: explains what we collect, why, where it's stored, how to revoke. (Required by https://support.google.com/googleplay/android-developer/answer/11150561.)

### Account / verification (https://support.google.com/googleplay/android-developer/answer/15633622 — India)
- [ ] **Google Play Console account**: $25 one-time fee. **Personal account** (you, individual) needs Indian government-issued photo ID + proof of address. **No D-U-N-S needed** for personal accounts.
- [ ] **Organization account** would need D-U-N-S but personal is fine for Lumin v1.
- [ ] **Payment profile** (only needed if we ever use Play Billing — not v1).
- [ ] **Tax info form** in Play Console (Indian PAN).
- [ ] **Note**: Personal accounts created after Nov 13, 2023 are subject to the **12-testers-for-14-days** rule before Production (see Section 5).

### App-code requirements
- [ ] Age confirmation gate at first launch (18+)
- [ ] First-run risk modal (above)
- [ ] Prominent disclosure before reading the API key field
- [ ] In-app "Delete my account & API key" button (Play Store **requires** in-app account deletion per https://support.google.com/googleplay/android-developer/answer/13327111)
- [ ] Settings link to ToS, Privacy Policy, Risk Disclosure
- [ ] Region check on startup; if region is in the exclude-list (US, China, Bangladesh at launch), refuse to enable trading (signals-display-only mode)
- [ ] Server-side enforcement that "live trading" can only be enabled on subscriber accounts
- [ ] No "guaranteed return / 10× / X% per week" language anywhere in app or store copy

### Financial features declaration (within Play Console → App Content)
- [ ] Declare **Cryptocurrency exchange** with explanation: "Connects to user's existing Binance Futures account via user-generated API key; does not custody funds."
- [ ] Declare **Financial advice** with explanation: "Displays trade signals labelled as informational; not personalised investment advice."
- [ ] Provide privacy policy + ToS + risk disclosure URLs in the declaration

### Test track gates
- [ ] **Internal testing**: up to 100 emails, no review needed, instant publish
- [ ] **Closed testing**: ≥ 12 testers opted-in for ≥ 14 continuous days (https://support.google.com/googleplay/android-developer/answer/14151465) — **required for personal accounts before Production**
- [ ] **Open testing**: optional but recommended; expands to ~public; reviews still applied
- [ ] **Production**: after passing Closed Testing gate + Play review; expect 3–7 day review

---

## Section 5 — Realistic plan + timeline

### Phase 1 — Closed Testing (weeks 1–3)
**Goal:** App live on Play in Closed Testing track with ~20 invited testers from our internal email list.

| Week | Task |
|---|---|
| 1 | Open Play Console account ($25), submit India personal-account verification (PAN + Aadhaar/passport). Stand up privacy policy + ToS + risk disclosure on `lumin.app/legal/*`. Add in-app first-run risk modal, age gate, prominent-disclosure screen pre-API-entry, in-app account-deletion flow. Lock store description copy. |
| 2 | Build store assets (icon, feature graphic, 4–6 screenshots, no video v1). Fill Data Safety form (over-declare API key under both Personal Info → Other AND Financial Info → Other). Fill Financial Features Declaration (Cryptocurrency exchange + Financial advice, with free-text). Country-target India + UK + EU (exclude US, China, Bangladesh). Upload first AAB to Closed Testing. |
| 3 | Invite 20 testers; they install and use for 14 days. Watch for any review flags. |

**Likelihood of Closed-Testing-track admission:** **high (>90%).** Closed Testing has lighter review than Production.

### Phase 2 — Open Testing (weeks 4–6)
**Goal:** Expand to ~500 public testers with broader feedback.

| Week | Task |
|---|---|
| 4 | After Closed Testing 14-day window, promote build to Open Testing. Public opt-in URL available. Monitor crash analytics + Play Console violations dashboard. |
| 5 | Iterate on first review-flag cycle. Common Google reviewer questions: clarify auto-execution flow, clarify subscription billing flow, request additional proof of region-block enforcement. Respond within 7 days each round. |
| 6 | Build to 500 opted-in testers. Stable two consecutive weeks. |

**Likelihood of Open-Testing-track approval:** **medium-high (70–80%).** First-round questions are normal. Expect 1–2 rounds of reviewer back-and-forth.

### Phase 3 — Production (weeks 7–10)
**Goal:** Full public listing in India + UK + EU (no US).

| Week | Task |
|---|---|
| 7 | Confirm ≥ 12 testers met 14-day continuous opt-in requirement. Submit promotion to Production. |
| 8 | Production review (3–7 days typical, longer for crypto). Expect questions: (a) FIU-IND status for India, (b) leverage warning, (c) confirmation that no Play Billing is bypassed. |
| 9 | Address reviewer feedback; resubmit. |
| 10 | Production live OR appeal path opens. |

**Likelihood of first-attempt Production approval:** **medium (50–60%).** Likely outcomes:
- **(40–50%)** Approved with minor edits to description/data-safety after one round.
- **(30%)** Held for additional documentation — reviewers ask for proof of non-custodial nature, Binance API-key restriction screenshots, regulator-letter for India operations.
- **(15%)** Rejected initially under Financial Services policy ambiguity → appeal with the prepared Section 3.1 statement → re-approved.
- **(5–10%)** Hard rejection requiring product pivot (e.g., remove auto-execution, ship signals-only). Unlikely given Cornix et al. precedent but non-zero.

### Cumulative realistic timeline
**6–10 weeks** from "decision to ship" to a Production listing in India + UK + EU. Two failure modes that would extend it:
1. **FIU-IND legal review on the India side** could add 2–4 weeks if we choose to wait for clean compliance before launching to India. (Recommended path: launch to UK/EU first, India second.)
2. **Multiple rejection-appeal cycles** could add 2–6 weeks per cycle.

### Top risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Reviewer treats us as "in-scope crypto exchange" | Medium | High | Pre-empt with free-text in Financial Features Declaration explaining non-custodial pattern; cite Cornix/3Commas precedent |
| FIU-IND enforces against us in India | Low (today) / Medium (in 12 months) | High | Legal opinion; consider FIU registration once revenue justifies it |
| Marketing copy reads as "guaranteed returns" | Self-imposed | High | Strict copy guardrails: no yield numbers, no leverage numbers, "signal" not "advice" |
| Personal-account-12-tester requirement delays launch | High (it applies) | Low (just bake into timeline) | Recruit testers in week 1, not week 3 |
| Play Billing required because reviewer disagrees with our "consumed outside the app" framing | Low | Medium | Keep in-app surfaces free; sell Telegram subscription only off-Play; document this clearly in declaration free-text |
| US targeting accidentally enabled | Low (we exclude) | High (CFTC) | Server-side region block + Play Console country exclude list |

---

## Sources

### Google Play Policy (primary)
- Financial Services policy — https://support.google.com/googleplay/android-developer/answer/9876821
- Cryptocurrency Exchanges and Software Wallets policy — https://support.google.com/googleplay/android-developer/answer/16329703
- Financial Features Declaration — https://support.google.com/googleplay/android-developer/answer/13849271
- Payments policy — https://support.google.com/googleplay/android-developer/answer/10281818
- User Data policy — https://support.google.com/googleplay/android-developer/answer/10144311
- Data Safety section — https://support.google.com/googleplay/android-developer/answer/10787469
- Prominent disclosure best practices — https://support.google.com/googleplay/android-developer/answer/11150561
- App testing for new personal accounts (12 testers / 14 days) — https://support.google.com/googleplay/android-developer/answer/14151465
- India developer verification documents — https://support.google.com/googleplay/android-developer/answer/15633622
- India billing changes — https://support.google.com/googleplay/android-developer/answer/13306652
- User choice billing — https://support.google.com/googleplay/android-developer/answer/13821247
- Deceptive Behavior policy — https://support.google.com/googleplay/android-developer/answer/9888077
- Developer Program Policy — https://support.google.com/googleplay/android-developer/answer/16810878
- Developer community thread on automated trading — https://support.google.com/googleplay/android-developer/thread/380480270/

### Google Ads (supporting, not Play)
- Complex speculative financial products — https://support.google.com/adspolicy/answer/15188218
- Financial products and services — https://support.google.com/adspolicy/answer/2464998
- Restricted financial products certification — https://support.google.com/adspolicy/answer/7645254

### Analysis / commentary
- Manimama (15-jurisdiction breakdown) — https://manimama.eu/what-will-google-play-s-updated-policy-for-crypto-apps-look-like-an-overview-of-the-changes/
- CCN (jurisdictions, licensing) — https://www.ccn.com/education/crypto/google-play-crypto-wallet-licensing-us-eu-rules-explained/
- Ainvest (15-market enforcement) — https://www.ainvest.com/news/google-play-enforces-15-market-crypto-wallet-licensing-rules-october-29-2025-2508/
- FXStreet (non-custodial clarification) — https://www.fxstreet.com/cryptocurrencies/news/google-clarifies-non-custodial-wallets-not-part-of-recent-ban-on-unlicensed-crypto-exchanges-and-wallets-202508132319
- LeapRate (binary options Play ban) — https://www.leaprate.com/binary-options/platform/google-play-bans-binary-options-trading-apps/
- RevenueCat (closed testing survival) — https://www.revenuecat.com/blog/engineering/google-play-14-day/

### India regulatory
- FIU-IND VDA AML/CFT Guidelines (Jan 2026) — https://fiuindia.gov.in/pdfs/downloads/VDA08012026.pdf
- Global Legal Insights India 2026 — https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/india/
- Legal500 (PMLA scope) — https://www.legal500.com/developments/thought-leadership/the-requirement-of-fiu-ind-registration-and-its-ramifications-for-the-virtual-digital-asset-industry/
- PIB show-cause notices — https://www.pib.gov.in/PressReleasePage.aspx?PRID=1991372

### Competitor Play Store listings
- Cornix — https://play.google.com/store/apps/details?id=com.cornix
- Cornix ToS (risk language reference) — https://cornix.io/terms/
- 3Commas — https://play.google.com/store/apps/details?id=io.threecommas.client.global
- Bitsgap — https://play.google.com/store/apps/details?id=com.bitsgap.pwa
- Pionex (global) — https://play.google.com/store/apps/details?id=com.pionex.client
- Pionex US — https://play.google.com/store/apps/details?id=com.pionex.us.client
- WunderTrading — https://play.google.com/store/apps/details?id=com.wundertrading.android
- Wunderbit — https://play.google.com/store/apps/details?id=eu.wunderbit.trading_web
- Coinrule — https://play.google.com/store/apps/details?id=com.coinrule.crypto_app_currency_stocks_shares_defi_trading_investing_auto_trade_bot_automated_coinrule

### Notes on source quality
- All `support.google.com/googleplay/...` URLs return HTTP 403 to programmatic fetch; verbatim text is from Google's own search-result snippets. The URLs themselves are canonical.
- All `play.google.com/store/apps/details?...` URLs are similarly 403; competitor metadata is from AppBrain, Aptoide, Trustpilot, and search snippets.
- The October 2025 Crypto Exchanges policy is the most recently changed surface; any source predating August 2025 was excluded from this analysis.
