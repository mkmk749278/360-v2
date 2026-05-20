# Closed Testing — tester recruitment templates

**Last updated:** 2026-05-20
**Use this for:** recruiting 12+ paid Telegram subscribers as Closed Testing testers, then keeping them engaged for the mandatory 14-day continuous-opt-in window.

The Closed Testing track on Play Console gives you a public opt-in URL after submission (looks like `https://play.google.com/apps/testing/com.luminapp.lumin`). Each tester taps the URL on their Android phone, taps "Become a tester", and then Lumin appears in their Play Store for install.

---

## 1. Initial DM to a paid subscriber

**Send via Telegram DM to each of the 12+ candidates.** Replace `[OPT-IN URL]` with the actual one Play Console generates after you submit.

```
Hey 👋

I'm putting Lumin on the Play Store and need a few testers to help me complete Google's 14-day testing requirement before the public launch.

You'd just need to:
1. Tap this on your Android phone: [OPT-IN URL]
2. Hit "Become a tester"
3. Wait ~10 min, then Lumin shows up in your Play Store — install it like any other app

That's it — no commitment to actually use it, just need it installed on your account for 14 days so Google releases the public version.

If you're up for it, lmk. Thanks 🙏
```

**~120 words. No marketing pitch, no risk language repeats (they're already paid subscribers — they know the product). Just an honest "help me unblock Google" ask.**

---

## 2. Broadcast variant (post to channel if DM is slow)

If you don't hit 12 individual DM yeses in a day, broadcast this in the paid channel. The first 12 opt-ins are all you need.

```
📱 Lumin Android app — Play Store soft launch

Putting Lumin on the Play Store. Google requires 12+ testers
to opt in for 14 continuous days before they let me publish.

I need 12 paid subscribers to help me unblock that step:
1. Tap on Android phone: [OPT-IN URL]
2. "Become a tester"
3. Install Lumin from your Play Store when it appears

That's literally it. The app stays installed for 14 days,
you don't have to use it actively.

First 12 who do this and DM me confirmation — public launch is
on you 🙏
```

---

## 3. Reminder DM (day 7 if anyone hasn't opted in)

If by day 7 you haven't hit 12 active testers, gently nudge the candidates who DM'd yes but haven't shown up in your tester list:

```
Hey — quick reminder, the Lumin Play Store tester link still
needs your tap so the 14-day clock can start:

[OPT-IN URL]

Takes 30 seconds. Lumin will show up in your Play Store
afterwards. Once 12 of us are in, the clock starts and we're
good to go public 2 weeks later.
```

---

## 4. After Production goes live (day ~25)

Once the public listing is live, thank the testers + close the loop:

```
Hey 🎉

Lumin is now LIVE on the Play Store — thanks to you for opting
into testing.

Public URL: https://play.google.com/store/apps/details?id=com.luminapp.lumin

You can stay opted in as a tester (you'll get builds 1-2 days
before the public on every release), or unenroll — your choice,
zero pressure.

Cheers
```

---

## 5. Operational notes

### How many to ask

You need **12+ active testers for 14 continuous days**. Plan for attrition:

- DM ~20 subscribers to land 12 opt-ins (Telegram DM open rate + actual-tap rate puts the realistic conversion at ~60-70%)
- If you only have 12-15 active paid subscribers total, broadcast option #2 is the right call — gets the message in front of everyone

### What "continuous" means

Play Console counts a tester as continuous if their Google account stays opted into the Closed Testing track without unenrolling. They do NOT have to actually launch the app every day. So once they tap the URL and "Become a tester", the 14-day clock starts and runs independently of their actual app usage.

### Tracking who's in

Play Console → Closed testing → Manage testers shows the current opt-in count + a list of opted-in emails. Check this once a day during the 14-day window. If anyone drops below 12, the clock resets.

### Tester contact info

Add `mulakapati446@gmail.com` as the "Email for testers" in Play Console — testers see this if they tap "Contact developer" inside the Play Store listing. This is separate from the public Privacy Policy / support contact.

### Common tester questions (pre-drafted DM replies)

| Tester asks | You reply |
|---|---|
| "The link doesn't work" | "Open it directly on your Android phone (not iOS, not desktop). If still broken, send a screenshot." |
| "I don't see Lumin in my Play Store" | "Wait ~10 minutes after tapping 'Become a tester' — Play Store needs to cache the listing for your account. If still missing after 30 min, try clearing Play Store cache: Settings → Apps → Play Store → Clear cache." |
| "Does this cost anything?" | "No — Closed Testing is free. You're helping me unblock the public launch." |
| "Can I really test signals?" | "Yes if you connect a Binance Futures API key. Otherwise you'll see the signals feed + Recent Activity but no orders fire." |
| "How do I unenroll?" | "Tap the same opt-in URL again on your Android phone → 'Leave the program'. But please wait until day 14 if you're up for it 🙏" |

---

## 6. Mental model — what NOT to say

Things to deliberately NOT include in any tester recruitment message (would invite Play Store complications if a reviewer ever sees the message):

- ❌ "Guaranteed profits" / "you'll make money testing this"
- ❌ "Sign up here to start trading" — you're testing the *app*, not the trading
- ❌ Specific yield numbers ("our signals do +47% / month")
- ❌ "This is a financial advisory service"
- ❌ Any language implying testers will be compensated (Play prohibits paid testing in most contexts)
- ❌ Personal information requests beyond the standard Telegram DM ("send me your Binance UID" — never do this)

The recruitment templates above stick to "Google requires testers + please tap this URL". That's the safe framing.
