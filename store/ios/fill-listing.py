"""Fill the Axes & Aces App Store listing through the App Store Connect API.

Run after the app record exists in App Store Connect (see APP-STORE-LISTING.md):
    python store/ios/fill-listing.py

Needs: pip install pyjwt cryptography requests
The API key is read from ASC_KEY_PATH (default: the GSW key kept in the Steps & Scripture repo).
Safe to re-run: it updates fields in place and skips screenshots that are already uploaded.
"""
import hashlib, json, os, sys, time
from pathlib import Path

import jwt, requests

KEY_PATH = os.environ.get("ASC_KEY_PATH", r"C:\dev\steps-and-scripture\secrets\AuthKey_JL975X97K8.p8")
KEY_ID = os.environ.get("ASC_KEY_ID", "JL975X97K8")
ISSUER = os.environ.get("ASC_ISSUER_ID", "609d047b-7c29-4529-8b10-1a5aed2efacd")
BUNDLE = "io.github.zoerner6.axesandaces"
HERE = Path(__file__).parent
API = "https://api.appstoreconnect.apple.com"

SUBTITLE = "Poker hands vs. monsters"
KEYWORDS = "poker,cards,rpg,roguelike,monsters,fantasy,adventure,card battle,deckbuilder,dungeon,solitaire"
PROMO = "Every fight is a hand of cards. Build the best poker hand you can and strike."
SHOTS = ["iphone69-1-story.png", "iphone69-2-fight.png", "iphone69-3-aces-bonus.png"]
REVIEW_NOTES = (
    "No login needed. Tap NEW HERO, then START THE ADVENTURE. Leaderboards and cloud backup are anonymous "
    "(a random save code, no account). The game runs from files inside the app; the monster clips stream "
    "from axesandaces.com when online and fall back to still art offline."
)


def token():
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "iat": now, "exp": now + 1100, "aud": "appstoreconnect-v1"},
                      Path(KEY_PATH).read_text(), algorithm="ES256", headers={"kid": KEY_ID})


def call(method, path, body=None, ok=(200, 201, 204)):
    r = requests.request(method, API + path, json=body,
                         headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"})
    if r.status_code not in ok:
        sys.exit(f"{method} {path} -> {r.status_code}\n{r.text[:2000]}")
    return r.json() if r.content else {}


def description():
    text = (HERE.parent / "google-play" / "store-listing.txt").read_text(encoding="utf-8")
    return text.split("FULL DESCRIPTION", 1)[1].split("APP CATEGORY", 1)[0].strip()


def main():
    apps = call("GET", f"/v1/apps?filter[bundleId]={BUNDLE}")["data"]
    if not apps:
        sys.exit("No App Store Connect app with this bundle ID yet. Josh makes it first (APP-STORE-LISTING.md).")
    app_id = apps[0]["id"]
    print("app", app_id)

    # App info: subtitle, privacy URL, categories
    info = call("GET", f"/v1/apps/{app_id}/appInfos")["data"][0]
    call("PATCH", f"/v1/appInfos/{info['id']}", {"data": {"type": "appInfos", "id": info["id"], "relationships": {
        "primaryCategory": {"data": {"type": "appCategories", "id": "GAMES"}},
        "primarySubcategoryOne": {"data": {"type": "appCategories", "id": "GAMES_CARD"}},
        "secondaryCategory": {"data": {"type": "appCategories", "id": "GAMES"}},
        "secondarySubcategoryOne": {"data": {"type": "appCategories", "id": "GAMES_ROLE_PLAYING"}},
    }}})
    for loc in call("GET", f"/v1/appInfos/{info['id']}/appInfoLocalizations")["data"]:
        call("PATCH", f"/v1/appInfoLocalizations/{loc['id']}", {"data": {"type": "appInfoLocalizations", "id": loc["id"],
             "attributes": {"subtitle": SUBTITLE, "privacyPolicyUrl": "https://axesandaces.com/privacy.html"}}})

    # Age rating: fantasy violence only
    ar = call("GET", f"/v1/appInfos/{info['id']}/ageRatingDeclaration")["data"]
    none = "NONE"
    call("PATCH", f"/v1/ageRatingDeclarations/{ar['id']}", {"data": {"type": "ageRatingDeclarations", "id": ar["id"], "attributes": {
        "alcoholTobaccoOrDrugUseOrReferences": none, "contests": none, "gamblingSimulated": none,
        "horrorOrFearThemes": none, "matureOrSuggestiveThemes": none, "medicalOrTreatmentInformation": none,
        "profanityOrCrudeHumor": none, "sexualContentGraphicAndNudity": none, "sexualContentOrNudity": none,
        "violenceCartoonOrFantasy": "INFREQUENT_OR_MILD", "violenceRealistic": none,
        "violenceRealisticProlongedGraphicOrSadistic": none, "gambling": False, "unrestrictedWebAccess": False,
        "kidsAgeBand": None,
    }}}, ok=(200,))

    # Version 1.0 text
    ver = call("GET", f"/v1/apps/{app_id}/appStoreVersions?filter[platform]=IOS")["data"][0]
    call("PATCH", f"/v1/appStoreVersions/{ver['id']}", {"data": {"type": "appStoreVersions", "id": ver["id"],
         "attributes": {"copyright": "2026 Gold Standard Web LLC"}}})
    vloc = call("GET", f"/v1/appStoreVersions/{ver['id']}/appStoreVersionLocalizations")["data"][0]
    call("PATCH", f"/v1/appStoreVersionLocalizations/{vloc['id']}", {"data": {"type": "appStoreVersionLocalizations",
         "id": vloc["id"], "attributes": {"description": description(), "keywords": KEYWORDS, "promotionalText": PROMO,
                                          "supportUrl": "https://axesandaces.com", "marketingUrl": "https://axesandaces.com"}}})

    # Review details
    rd = call("GET", f"/v1/appStoreVersions/{ver['id']}/appStoreReviewDetail", ok=(200, 404))
    attrs = {"contactFirstName": "Josh", "contactLastName": "Zoerner", "contactEmail": "hello@goldstandardweb.com",
             "demoAccountRequired": False, "notes": REVIEW_NOTES}
    if rd.get("data"):
        call("PATCH", f"/v1/appStoreReviewDetails/{rd['data']['id']}", {"data": {"type": "appStoreReviewDetails",
             "id": rd["data"]["id"], "attributes": attrs}})
    else:
        call("POST", "/v1/appStoreReviewDetails", {"data": {"type": "appStoreReviewDetails", "attributes": attrs,
             "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": ver["id"]}}}}})

    # Screenshots (6.9-inch iPhone)
    sets = call("GET", f"/v1/appStoreVersionLocalizations/{vloc['id']}/appScreenshotSets")["data"]
    sset = next((s for s in sets if s["attributes"]["screenshotDisplayType"] == "APP_IPHONE_67"), None)
    if not sset:
        sset = call("POST", "/v1/appScreenshotSets", {"data": {"type": "appScreenshotSets",
                    "attributes": {"screenshotDisplayType": "APP_IPHONE_67"},
                    "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": vloc["id"]}}}}})["data"]
    have = {s["attributes"]["fileName"] for s in call("GET", f"/v1/appScreenshotSets/{sset['id']}/appScreenshots")["data"]}
    for name in SHOTS:
        if name in have:
            continue
        data = (HERE / name).read_bytes()
        shot = call("POST", "/v1/appScreenshots", {"data": {"type": "appScreenshots",
                    "attributes": {"fileName": name, "fileSize": len(data)},
                    "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": sset["id"]}}}}})["data"]
        for op in shot["attributes"]["uploadOperations"]:
            part = data[op["offset"]: op["offset"] + op["length"]]
            requests.request(op["method"], op["url"], data=part,
                             headers={h["name"]: h["value"] for h in op["requestHeaders"]}).raise_for_status()
        call("PATCH", f"/v1/appScreenshots/{shot['id']}", {"data": {"type": "appScreenshots", "id": shot["id"],
             "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
        print("uploaded", name)

    print("Listing filled. Left in the console: App Privacy answers, then pick the build and Add for Review.")


if __name__ == "__main__":
    main()
