# Lumin Play Store — Execution Plan

**Last updated:** 2026-05-20
**Reference research:** [`PLAYSTORE_RESEARCH_2026-05-20.md`](./PLAYSTORE_RESEARCH_2026-05-20.md) — read first
**Owner decision required to start:** YES (this PR is the design/decision artefact; build begins once approved)

---

## TL;DR

- **Publishable.** India is NOT in the 15-jurisdiction crypto-custody licensing list. Our pattern (non-custodial of funds, holds trade-only API key) is the same as Cornix / 3Commas / Bitsgap / Pionex / WunderTrading — all live on Play.
- **Play Billing NOT required** for the Telegram-channel subscription (content consumed outside the Play-distributed app). Keep in-app surfaces free; sell off-Play.
- **Realistic timeline: 6–10 weeks.** Closed Testing live in week 2–3, Production in week 7–10. Two failure modes (FIU-IND review, reviewer back-and-forth) can extend by 2–6 weeks each.
- **Independent FIU-IND VASP registration question** — separate from Play, business-side legal review needed before serving India in Production. Not a blocker for Closed/Open Testing, and not for UK/EU.

---

## Decisions taken (committed by this PR)

| Decision | Choice | Why |
|---|---|---|
| Vocabulary | **"signal"**, **"automation"**, **"strategy execution"** everywhere. NEVER **"advice"**, **"recommendation"**, **"guidance"**, **"expert tips"**, **"guaranteed"**, **"X% return"**, **"NN× leverage"** | Per §3.5 — "signal" is distinct from "advice" in Google's own Financial features taxonomy; matches Cornix / 3Commas precedent. |
| Subscription billing | **Off-Play (website/Stripe/Razorpay).** No Play Billing in v1. App surfaces stay 100% free. | Per §1.4 + §3.4 — Telegram channel content consumed outside the app fits the explicit Play Billing carve-out. |
| Launch geo (Phase 1+2) | **India, UK, EU.** Exclude US, China, Bangladesh. | Per §1.9 — minimises review friction and avoids CFTC complexity. |
| Account type | **Personal account.** $25 one-time fee. PAN + Aadhaar verification. No D-U-N-S needed. | Per §Account/verification — organisation-account D-U-N-S overhead unnecessary for v1. |
| Content rating | Answer IARC honestly — expect **PEGI 12 / ESRB Teen**. Add app-level 18+ confirmation regardless. | Per §1.7 — matches Pionex et al; "18+" gate is owner-prudent independent of rating. |
| In-app paywall | **None in v1.** Auto-execute capability is a *gated capability* verified server-side against subscriber status; not a Play-Billing-purchased item. | Per §3.4 — moment we paywall in-app, we owe Play Billing. |
| Financial features declaration | Declare **BOTH** "Cryptocurrency exchange" AND "Financial advice" with explicit free-text explanations. Over-declare rather than under-declare. | Per §1.1 + §3.1 — pre-empts reviewer ambiguity; cites Cornix/3Commas precedent in the free-text. |
| Data Safety form | Declare API key under **BOTH** "Personal info → Other" AND "Financial info → Other". Over-declare. | Per §1.5 — Pionex's "we collect nothing" stance is risky; we go the other way. |

---

## Code work needed before Closed Testing

Each row is a separate PR. Each ships to a topic branch off `main`, opens a PR, and goes through review.

### App-side (lumin-app repo)

| # | PR title | Scope | Est. effort |
|---|---|---|---|
| A1 | `feat(launch): first-run age confirmation gate (18+)` | Modal at first launch; cannot dismiss without affirming. Persists in shared preferences. Blocks app entry if rejected. | XS (1 day) |
| A2 | `feat(launch): first-run risk disclosure modal` | After age gate. Three checkboxes: (a) I am 18+, (b) I understand crypto futures involves substantial risk of loss, (c) Lumin signals are not financial advice. "Continue" disabled until all three ticked. | S (1–2 days) |
| A3 | `feat(connect): prominent disclosure screen before API-key entry` | Mandatory per Play policy. Explains: what we collect (trade-only key), why (server-side execution), where it's stored (KMS-encrypted, IP-whitelisted VPS), how to revoke. Affirmative "I understand" button required before showing the API-key input field. | S (1–2 days) |
| A4 | `feat(settings): in-app account & API key deletion flow` | Required by Play policy (https://support.google.com/googleplay/android-developer/answer/13327111). Settings → "Delete my account" → confirmation modal → calls backend `DELETE /api/account` → revokes Binance key blob + deletes user row + logs out. | M (3–4 days) |
| A5 | `feat(settings): ToS / Privacy / Risk disclosure links` | Settings → Legal section with three links opening in browser. Already mostly wired; just need the URLs once docs exist. | XS (0.5 day) |
| A6 | `feat(launch): region-block enforcement` | On startup, check device locale + IP-derived region (via backend `GET /api/region`). If in US / China / Bangladesh → app enters "signals-display-only" mode (auto-trade disabled, connect button hidden). Soft fail open if region check fails (avoid bricking app). | M (2–3 days) |
| A7 | `chore(copy): vocabulary audit pass` | Grep every user-facing string in `lib/` for "advice", "recommendation", "guaranteed", "X%", "NNx" — replace with policy-compliant terms. | S (1 day) |
| A8 | `feat(launch): privacy-policy linked from PUT consent` | When user PUTs ANY data (notional, leverage, API key), Settings shows "Your data is handled per our Privacy Policy" inline link. Belt-and-suspenders for prominent-disclosure compliance. | XS (0.5 day) |

**Total app code work:** ~10–15 days serial, 7–10 days if parallelised.

### Backend-side (360-v2 repo)

| # | PR title | Scope | Est. effort |
|---|---|---|---|
| E1 | `feat(api): DELETE /api/account endpoint` | Hard-delete user_id row + cascade to all per-user tables + revoke + zero-out the encrypted-key blob in Firestore + remove from `_active_uids` cache. Audit-log the deletion. | M (3 days) |
| E2 | `feat(api): GET /api/region for client region-check` | Returns the IP-derived ISO country code. Client uses for the region-block in A6. Soft-fail (returns "unknown") on geolocation lookup failure. | XS (0.5 day) |
| E3 | `feat(content): standardised user-facing copy module` | Centralise risk-disclosure / ToS / privacy-policy text in `src/content/` so both the app fetches them via API AND the engine's Telegram welcome message reads from the same source. Single source of truth. | S (1 day) |

**Total backend code work:** ~4–5 days.

---

## Non-code work (parallel track — start immediately)

| # | Task | Owner | Blocks |
|---|---|---|---|
| L1 | Open Play Console account ($25), India personal-account verification (PAN + Aadhaar/passport) | Owner | Everything Play-side |
| L2 | Reserve & set up `lumin.app/legal/privacy`, `lumin.app/legal/terms`, `lumin.app/legal/risk` URLs on a stable HTTPS host | Owner | A5, store listing |
| L3 | Draft Privacy Policy text — explicitly covering API-key collection, KMS encryption, IP-whitelisting, revocation right, retention, deletion request channel. Use IAPP template + Cornix as reference | Owner / legal | L2 |
| L4 | Draft Terms of Service — Cornix-style: "not investment advice, high risk of loss, no regulator protection, USD-denominated trading carries currency risk, our service is non-custodial, you remain responsible for your Binance account security" | Owner / legal | L2 |
| L5 | Draft Risk Disclosure (separate from ToS) — "you may lose all funds, past performance does not guarantee future results, leverage amplifies both gains and losses, Binance Futures uses USDT-margined contracts, our signals are informational, do not trade with funds you cannot afford to lose" | Owner / legal | L2 |
| L6 | Store listing copy — short description (≤80 chars), full description (≤4000 chars). Must include risk-disclaimer block at bottom. Run through vocabulary audit (no "advice", no "guaranteed", no "NN%"). | Owner | Closed Testing submit |
| L7 | Store listing assets — icon (512×512), feature graphic (1024×500), 4–6 phone screenshots (16:9 or 9:16, 320–3840 px). No video v1. | Owner / designer | Closed Testing submit |
| L8 | Recruit 12+ testers for Closed Testing — must opt in within the same 14-day window | Owner | Production promotion |
| L9 | Engage Indian crypto-VDA lawyer for FIU-IND registration opinion. **Scope:** does Lumin's trade-key custody qualify as a Reporting Entity under PMLA? If yes, registration timeline + cost. Two-week turnaround target. | Owner / external | India Production launch |
| L10 | Optional: 1-page "compliance summary" PDF — pre-emptively explains non-custodial model + names Cornix/3Commas precedent. Attach to Play Console as supporting document in case of reviewer questions. | Owner / CTE | Production submit |

---

## Phased timeline

### Phase 0 — Foundation (week 1)

Parallel:
- Owner: L1, L2, L3, L4, L5 in flight (Play Console account, legal pages on host, three legal docs drafted)
- CTE: open PRs A1, A2, A5, A7, E2 (lowest-effort code work to unblock Closed Testing build)

### Phase 1 — Closed Testing (weeks 2–3)

| Week | Activity |
|---|---|
| 2 | All PRs from Phase 0 merged. PRs A3, A4, A8, E1, E3 open + merged. Store listing assets (L7) ready. Store copy (L6) drafted. Build first AAB. Submit to Closed Testing track with India + UK + EU geo. Invite 12+ testers (L8). |
| 3 | Testers install + use for 14 continuous days. Monitor crash analytics + Play Console violations dashboard. Iterate on any flags. |

**Exit criteria:**
- ≥12 testers active for 14 continuous days
- Zero open policy violations
- Zero crash-rate regressions
- All in-app legal links resolve to live URLs

### Phase 2 — Open Testing (weeks 4–6)

| Week | Activity |
|---|---|
| 4 | Promote build to Open Testing. Public opt-in URL goes live. PR A6 (region block) merged + tested. Region exclude list enforced server-side AND client-side. |
| 5 | Iterate on first reviewer-feedback cycle. Likely questions: clarify auto-execution flow, prove non-Play-Billing for subscription, confirm region block. Respond within 7 days per round. |
| 6 | Expand to ≥500 opted-in testers. Two consecutive weeks of stable build. |

**Exit criteria:**
- ≥500 testers
- Two consecutive weeks no new policy flags
- Reviewer back-and-forth resolved
- ToS / Privacy / Risk URLs stable + indexed
- FIU-IND legal opinion received (L9) → decision: launch India in Production or hold India for FIU registration

### Phase 3 — Production (weeks 7–10)

| Week | Activity |
|---|---|
| 7 | Submit promotion to Production. Attach compliance summary PDF (L10). Geo: UK + EU first (lowest regulatory risk). India deferred pending L9 outcome. |
| 8 | Production review (3–7 days typical, expect 7–10 for crypto). Reviewer may ask for FIU-IND status if India included. |
| 9 | Address feedback; resubmit. |
| 10 | Production live OR appeal path opens. India added once L9 cleared. |

**Exit criteria:**
- Production listing live in UK + EU
- Indian production listing live OR explicit hold pending FIU registration
- Crash-free rate ≥99.5%
- No open Data Safety form errors

---

## Risk register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Reviewer classifies us as in-scope "crypto exchange" requiring licensing | Medium | High | Pre-empt with free-text in Financial Features Declaration explaining non-custodial pattern; cite Cornix/3Commas precedent; attach compliance summary PDF (L10) |
| R2 | FIU-IND enforces against signal/bot services in India | Low (today) / Medium (12mo horizon) | High (loss of India market) | L9 legal opinion; consider FIU registration once revenue justifies it |
| R3 | Store copy reads as "guaranteed returns" / promotional | Self-imposed | High (rejection) | A7 vocabulary audit + L6 copy review against the never-use list in §3.5 |
| R4 | 12-tester / 14-day rule delays Production | High (it applies) | Low (just bake into timeline) | Recruit testers in week 1, not week 3 |
| R5 | Play Billing required because reviewer disagrees with "consumed outside app" framing | Low | Medium (subscription must move into app or pivot revenue) | Keep in-app 100% free; sell only via off-Play web; document clearly in declaration free-text |
| R6 | US targeting accidentally enabled → CFTC | Low | Very High | A6 region block (client-side) + server-side region block (E2) + Play Console country exclude list. Belt + suspenders + Kevlar. |
| R7 | Reviewer asks for proof of API-key trade-only restriction | Medium | Low | Screenshots of Binance permission settings + the `binance_connect_validator` code path attached pre-emptively |
| R8 | First production rejection requires product pivot (e.g. remove auto-execute) | Very Low (~5%) | Very High | If rejected on substance, fall back to "signals-only" Phase 1; auto-execute lives off-Play as a webapp |

---

## Decision queue — owner sign-off needed BEFORE Phase 0 starts

1. **Approve this plan?** (Yes / changes requested)
2. **Confirm legal pages host** — is `lumin.app` registered + DNS pointable, or do we need a domain decision first?
3. **FIU-IND lawyer engagement** — owner-side procurement; budget approval needed
4. **Designer engagement for L7** — owner-side procurement
5. **Closed-testing tester recruitment** — owner has 12+ contacts to invite, or need to advertise the slot?

---

## What this PR ships

- `docs/PLAYSTORE_RESEARCH_2026-05-20.md` — the full research report from the deep-research agent (anchored to URLs; flagged source-quality caveats for the 403-blocked Google Play pages)
- `docs/PLAYSTORE_PLAN.md` — this document
- `ACTIVE_CONTEXT.md` — new section "Queued — Play Store Phase 0–3" tracking the work

**Nothing else changes.** No code, no app changes — those are the per-row PRs in the table above, owner-approved one at a time.

---

## Sources for the policy summary

See full citation list at the end of [`PLAYSTORE_RESEARCH_2026-05-20.md`](./PLAYSTORE_RESEARCH_2026-05-20.md). Key URLs anchored here for navigation:

- Crypto Exchanges & Software Wallets policy — https://support.google.com/googleplay/android-developer/answer/16329703
- Financial Features Declaration — https://support.google.com/googleplay/android-developer/answer/13849271
- Payments policy — https://support.google.com/googleplay/android-developer/answer/10281818
- Prominent disclosure best practices — https://support.google.com/googleplay/android-developer/answer/11150561
- In-app account deletion requirement — https://support.google.com/googleplay/android-developer/answer/13327111
- 12-testers-for-14-days rule — https://support.google.com/googleplay/android-developer/answer/14151465
- India developer verification — https://support.google.com/googleplay/android-developer/answer/15633622
- FIU-IND VDA AML/CFT guidelines (Jan 2026) — https://fiuindia.gov.in/pdfs/downloads/VDA08012026.pdf
