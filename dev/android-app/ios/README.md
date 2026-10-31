# The iPhone app

Same Capacitor shell as Android: it opens https://axesandaces.com, so website
updates reach it without a rebuild.

## You do not need a Mac

The build runs on a macOS machine at GitHub. The repo is public, so those
runners are free. Go to the repo's **Actions** tab, pick **iPhone app**, and
press **Run workflow**. Leave "Send the build to TestFlight" off the first
time: that run only checks the app compiles.

## Before the first real build

Three repository secrets are needed (Settings > Secrets and variables >
Actions > New repository secret):

| Secret | Where it comes from |
|---|---|
| `APPSTORE_ISSUER_ID` | App Store Connect > Users and Access > Integrations > App Store Connect API |
| `APPSTORE_KEY_ID` | the Key ID shown next to the key you generate there |
| `APPSTORE_P8` | open the downloaded `AuthKey_XXXXX.p8` in Notepad and paste all of it |

Apple only lets you download the .p8 once. Save it somewhere safe.

The app also has to exist in App Store Connect first, with bundle ID
`io.github.zoerner6.axesandaces` (the same one Android uses).

## Version numbers

In `ios/App/App.xcodeproj/project.pbxproj`:

- `MARKETING_VERSION` is the public version (1.0)
- `CURRENT_PROJECT_VERSION` is the build number, which must go up every upload

## Worth knowing before you submit

Apple's review guideline 4.2 turns down apps that are only a wrapper around a
website. Google accepted this one; Apple is much stricter. If it gets rejected
for that, the fix is to bundle the game inside the app instead of loading the
site: build the game into `dev/android-app/www` and drop the `server.url` line
from `capacitor.config.json`. The app then works with no signal, which is also
a better answer to the reviewer.
