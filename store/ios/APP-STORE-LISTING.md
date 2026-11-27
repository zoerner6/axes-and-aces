# Axes & Aces: App Store listing (iPhone)

## State (2026-11-27)

- App record: App Store Connect app **6839978375**, "Axes & Aces: Poker RPG", bundle
  `io.github.zoerner6.axesandaces` (registered 2026-11-26, id 4Q5Z3KJN42), SKU axesandaces-ios.
- Listing filled through the API by `python store/ios/fill-listing.py` (safe to re-run).
- **Build 1 (version 1.0)** uploaded by GitHub run 45987724572, processed (VALID), export compliance set
  (no non-exempt encryption), and attached to the 1.0 version. Info.plist now carries
  `ITSAppUsesNonExemptEncryption = false`, so later builds don't ask.
- **Not submitted.** Left for Josh in the console:
  1. App Privacy: answer as below, then Publish.
  2. Version 1.0 page: check it over, then **Add for Review** and submit. (Done by API 2026-11-27: China mainland removed from availability, content rights set, 13-inch iPad screenshots added; review submission b669b468.)

## Builds

GitHub > Actions > "iPhone app" > Run workflow with "Send the build to TestFlight" on
(`gh workflow run ios.yml -R zoerner6/axes-and-aces -f upload=true`). Raise `CURRENT_PROJECT_VERSION`
in `dev/android-app/ios/App/App.xcodeproj/project.pbxproj` before each new upload.
The archive is built unsigned and signed for the App Store at export (the team has no registered devices,
so a development profile can't be made). Apple warnings to handle before April 2027: target iOS 15+, build
with the iOS 27 SDK.

## Listing (filled by fill-listing.py)

- **Name:** Axes & Aces: Poker RPG (set when the record was made)
- **Subtitle (30):** Poker hands vs. monsters
- **Category:** Games, subcategories Card and Role Playing (Apple won't take Games as primary and secondary)
- **Price:** Free (USA base, price schedule set). Available in all 175 territories and new ones.
  No in-app purchases, no ads.
- **Privacy policy:** https://axesandaces.com/privacy.html
- **Support URL:** https://axesandaces.com
- **Marketing URL:** https://axesandaces.com
- **Copyright:** 2026 Gold Standard Web LLC
- **Keywords (100):** poker,cards,rpg,roguelike,monsters,fantasy,adventure,card battle,deckbuilder,dungeon,solitaire
- **Promotional text:** Every fight is a hand of cards. Build the best poker hand you can and strike.
- **Description:** same as Google Play (store/google-play/store-listing.txt), "No ads. No in-app purchases." kept.
- **Screenshots (6.9", 1320x2868):** iphone69-1-story.png, iphone69-2-fight.png, iphone69-3-aces-bonus.png
- **Age rating (Apple's 2025 questions):** Infrequent/Mild Cartoon or Fantasy Violence; every other content
  item None (including simulated gambling and weapons: poker hands are only a card mechanic, no betting).
  User-generated content: **Yes** (leaderboard nicknames only). Ads, gambling, loot boxes, chat, social media,
  web access, health topics, parental controls, age assurance: No.
- **App Review notes:** No login needed. Tap NEW HERO > START THE ADVENTURE. Leaderboards and cloud backup
  are anonymous (a random save code; no account). The game runs from files inside the app; the monster clips
  stream from axesandaces.com when online and fall back to still art offline.
- **Review contact:** Josh Zoerner, hello@goldstandardweb.com, phone copied from Brown Noise's review details.

## App Privacy (Josh answers in the console; the API can't set these)

Data collected, **not linked to the user, not used for tracking**:
- **User Content > Gameplay Content:** game progress for cloud backup (automatic, about once a minute)
- **User Content > Other User Content:** the leaderboard nickname and score (only if the player posts a score)

No identifiers, no contact info, no location, no analytics, no ads.
