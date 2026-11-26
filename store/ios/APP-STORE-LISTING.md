# Axes & Aces: App Store listing (iPhone)

Bundle ID `io.github.zoerner6.axesandaces` was registered with Apple on 2026-11-26 (id 4Q5Z3KJN42).
The iPhone build compiles at GitHub (run 45906361680, 2026-11-26). The server functions the app calls
(leaderboard, cloud saves) already answer cross-origin calls on axesandaces.com.

## Josh: the one step (about 3 minutes)

App Store Connect > Apps > **+** > New App:
- Platforms: **iOS**
- Name: **Axes & Aces**
- Primary language: **English (U.S.)**
- Bundle ID: **Axes and Aces - io.github.zoerner6.axesandaces**
- SKU: **axesandaces-ios**
- User access: Full Access

Then tell Claude "Axes app made". Claude runs `python store/ios/fill-listing.py`, which fills everything
below through the API, then runs the GitHub "iPhone app" workflow with TestFlight upload on.

## Listing (filled by fill-listing.py)

- **Name:** Axes & Aces
- **Subtitle (30):** Poker hands vs. monsters
- **Category:** Games > Card; secondary Games > Role Playing
- **Price:** Free. No in-app purchases, no ads.
- **Privacy policy:** https://axesandaces.com/privacy.html
- **Support URL:** https://axesandaces.com
- **Marketing URL:** https://axesandaces.com
- **Copyright:** 2026 Gold Standard Web LLC
- **Keywords (100):** poker,cards,rpg,roguelike,monsters,fantasy,adventure,card battle,deckbuilder,dungeon,solitaire
- **Promotional text:** Every fight is a hand of cards. Build the best poker hand you can and strike.
- **Description:** same as Google Play (store/google-play/store-listing.txt), "No ads. No in-app purchases." kept.
- **Screenshots (6.9", 1320x2868):** iphone69-1-story.png, iphone69-2-fight.png, iphone69-3-aces-bonus.png
- **Age rating:** Infrequent/Mild Cartoon or Fantasy Violence; everything else None. Simulated gambling: **None**
  (poker hands are only a card mechanic; no betting, no wagering, no currency). Expected rating 9+.
- **App Review notes:** No login needed. Tap NEW HERO > START THE ADVENTURE. Leaderboards and cloud backup
  are anonymous (a random save code; no account). The game runs from files inside the app; the monster clips
  stream from axesandaces.com when online and fall back to still art offline.
- **Review contact:** Josh Zoerner, hello@goldstandardweb.com (phone: Josh adds in the console if Apple asks)

## App Privacy (Josh answers in the console; the API can't set these)

Data collected, **not linked to the user, not used for tracking**:
- **User Content > Gameplay Content:** game progress for cloud backup (automatic, about once a minute)
- **User Content > Other User Content:** the leaderboard nickname and score (only if the player posts a score)

No identifiers, no contact info, no location, no analytics, no ads.
