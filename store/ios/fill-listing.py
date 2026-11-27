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
PHONE_FROM_APP = "6824769272"  # Brown Noise: its review contact phone is reused here
API = "https://api.appstoreconnect.apple.com"

SUBTITLE = "Poker hands vs. monsters"
KEYWORDS = "poker,cards,rpg,roguelike,monsters,fantasy,adventure,card battle,deckbuilder,dungeon,solitaire"
PROMO = "Every fight is a hand of cards. Build the best poker hand you can and strike."
SHOTS = {  # display type -> files (6.9-inch iPhone 1320x2868, 13-inch iPad 2048x2732)
    "APP_IPHONE_67": ["iphone69-1-story.png", "iphone69-2-fight.png", "iphone69-3-aces-bonus.png"],
    "APP_IPAD_PRO_3GEN_129": ["ipad13-1-story.png", "ipad13-2-fight.png", "ipad13-3-aces-bonus.png"],
}
# China mainland needs a Security Assessment and an AIGC filing, so the app is not sold there.
EXCLUDED_TERRITORIES = {"CHN"}
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


def review_phone():
    """Copy the review contact phone from another GSW app (never printed, never stored in the repo)."""
    for v in call("GET", f"/v1/apps/{PHONE_FROM_APP}/appStoreVersions?limit=10")["data"]:
        rd = call("GET", f"/v1/appStoreVersions/{v['id']}/appStoreReviewDetail", ok=(200, 404))
        phone = (rd.get("data") or {}).get("attributes", {}).get("contactPhone")
        if phone:
            return phone
    return None


def set_free_price(app_id):
    """Free in every territory (US base), unless a price schedule already exists."""
    r = requests.get(API + f"/v1/appPriceSchedules/{app_id}/manualPrices",
                     headers={"Authorization": "Bearer " + token()})
    if r.status_code == 200 and r.json().get("data"):
        print("price already set")
        return
    points = call("GET", f"/v1/apps/{app_id}/appPricePoints?filter[territory]=USA&limit=200")["data"]
    free = next(p for p in points if float(p["attributes"]["customerPrice"]) == 0)
    call("POST", "/v1/appPriceSchedules", {
        "data": {"type": "appPriceSchedules", "relationships": {
            "app": {"data": {"type": "apps", "id": app_id}},
            "baseTerritory": {"data": {"type": "territories", "id": "USA"}},
            "manualPrices": {"data": [{"type": "appPrices", "id": "${price1}"}]}}},
        "included": [{"type": "appPrices", "id": "${price1}",
                      "attributes": {"startDate": None},
                      "relationships": {"appPricePoint": {"data": {"type": "appPricePoints", "id": free["id"]}}}}]})
    print("price set: free")


def exclude_territories(app_id):
    """Turn off the territories in EXCLUDED_TERRITORIES on an existing availability."""
    path = f"/v2/appAvailabilities/{app_id}/territoryAvailabilities?limit=200&include=territory"
    while path:
        page = call("GET", path)
        for ta in page["data"]:
            if ta["relationships"]["territory"]["data"]["id"] in EXCLUDED_TERRITORIES and ta["attributes"]["available"]:
                call("PATCH", f"/v1/territoryAvailabilities/{ta['id']}", {"data": {"type": "territoryAvailabilities",
                     "id": ta["id"], "attributes": {"available": False}}})
                print("not sold in", ta["relationships"]["territory"]["data"]["id"])
        nxt = page.get("links", {}).get("next")
        path = nxt.replace(API, "") if nxt else None


def set_availability(app_id):
    """Sold in every territory except EXCLUDED_TERRITORIES, and in new ones Apple adds."""
    r = requests.get(API + f"/v1/apps/{app_id}/appAvailabilityV2", headers={"Authorization": "Bearer " + token()})
    if r.status_code == 200:
        exclude_territories(app_id)
        print("availability already set")
        return
    terrs = call("GET", "/v1/territories?limit=200")["data"]
    inc = [{"type": "territoryAvailabilities", "id": f"${{t{i}}}",
            "attributes": {"available": t["id"] not in EXCLUDED_TERRITORIES},
            "relationships": {"territory": {"data": {"type": "territories", "id": t["id"]}}}}
           for i, t in enumerate(terrs)]
    call("POST", "/v2/appAvailabilities", {
        "data": {"type": "appAvailabilities", "attributes": {"availableInNewTerritories": True},
                 "relationships": {"app": {"data": {"type": "apps", "id": app_id}},
                                   "territoryAvailabilities": {"data": [{"type": x["type"], "id": x["id"]} for x in inc]}}},
        "included": inc})
    print(f"available in {len(terrs)} territories")


def upload_shots(vloc_id, display, files):
    """Reserve, upload and commit each screenshot in the set; skips files already there."""
    sets = call("GET", f"/v1/appStoreVersionLocalizations/{vloc_id}/appScreenshotSets")["data"]
    sset = next((s for s in sets if s["attributes"]["screenshotDisplayType"] == display), None)
    if not sset:
        sset = call("POST", "/v1/appScreenshotSets", {"data": {"type": "appScreenshotSets",
                    "attributes": {"screenshotDisplayType": display},
                    "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": vloc_id}}}}})["data"]
    have = {s["attributes"]["fileName"] for s in call("GET", f"/v1/appScreenshotSets/{sset['id']}/appScreenshots")["data"]}
    for name in files:
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
        print("uploaded", display, name)


def description():
    text = (HERE.parent / "google-play" / "store-listing.txt").read_text(encoding="utf-8")
    return text.split("FULL DESCRIPTION", 1)[1].split("APP CATEGORY", 1)[0].strip()


def main():
    apps = call("GET", f"/v1/apps?filter[bundleId]={BUNDLE}")["data"]
    if not apps:
        sys.exit("No App Store Connect app with this bundle ID yet. Josh makes it first (APP-STORE-LISTING.md).")
    app_id = apps[0]["id"]
    print("app", app_id)

    # Content rights: all art, music and clips are our own.
    call("PATCH", f"/v1/apps/{app_id}", {"data": {"type": "apps", "id": app_id,
         "attributes": {"contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT"}}})

    # App info: subtitle, privacy URL, categories (Games > Card + Role Playing; Apple won't take Games twice)
    info = call("GET", f"/v1/apps/{app_id}/appInfos")["data"][0]
    call("PATCH", f"/v1/appInfos/{info['id']}", {"data": {"type": "appInfos", "id": info["id"], "relationships": {
        "primaryCategory": {"data": {"type": "appCategories", "id": "GAMES"}},
        "primarySubcategoryOne": {"data": {"type": "appCategories", "id": "GAMES_CARD"}},
        "primarySubcategoryTwo": {"data": {"type": "appCategories", "id": "GAMES_ROLE_PLAYING"}},
    }}})
    for loc in call("GET", f"/v1/appInfos/{info['id']}/appInfoLocalizations")["data"]:
        call("PATCH", f"/v1/appInfoLocalizations/{loc['id']}", {"data": {"type": "appInfoLocalizations", "id": loc["id"],
             "attributes": {"subtitle": SUBTITLE, "privacyPolicyUrl": "https://axesandaces.com/privacy.html"}}})

    # Age rating (Apple's 2025 schema): fantasy violence only. Leaderboard nicknames count as user content.
    ar = call("GET", f"/v1/appInfos/{info['id']}/ageRatingDeclaration")["data"]
    none = "NONE"
    call("PATCH", f"/v1/ageRatingDeclarations/{ar['id']}", {"data": {"type": "ageRatingDeclarations", "id": ar["id"], "attributes": {
        "alcoholTobaccoOrDrugUseOrReferences": none, "contests": none, "gamblingSimulated": none,
        "gunsOrOtherWeapons": none, "horrorOrFearThemes": none, "matureOrSuggestiveThemes": none,
        "medicalOrTreatmentInformation": none, "profanityOrCrudeHumor": none,
        "sexualContentGraphicAndNudity": none, "sexualContentOrNudity": none,
        "violenceCartoonOrFantasy": "INFREQUENT_OR_MILD", "violenceRealistic": none,
        "violenceRealisticProlongedGraphicOrSadistic": none,
        "advertising": False, "gambling": False, "lootBox": False, "healthOrWellnessTopics": False,
        "messagingAndChat": False, "parentalControls": False, "unrestrictedWebAccess": False,
        "userGeneratedContent": True, "ageAssurance": False, "socialMedia": False,
        "datingAndRelationships": False, "sharedLocation": False, "socialMediaAgeRestricted": False,
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
    phone = review_phone()
    if phone:
        attrs["contactPhone"] = phone
    if rd.get("data"):
        call("PATCH", f"/v1/appStoreReviewDetails/{rd['data']['id']}", {"data": {"type": "appStoreReviewDetails",
             "id": rd["data"]["id"], "attributes": attrs}})
    else:
        call("POST", "/v1/appStoreReviewDetails", {"data": {"type": "appStoreReviewDetails", "attributes": attrs,
             "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": ver["id"]}}}}})

    set_free_price(app_id)
    set_availability(app_id)

    for display, files in SHOTS.items():
        upload_shots(vloc["id"], display, files)

    print("Listing filled. Left in the console: App Privacy answers, then pick the build and Add for Review.")


if __name__ == "__main__":
    main()
