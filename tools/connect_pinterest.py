"""Connect the Sparrow Street Pinterest account to the robot. Peter runs this once, on his Mac, in Terminal:

    python3 social-robot/tools/connect_pinterest.py

1. It asks for the app's secret key (copy it from developers.pinterest.com → My apps → Sparrow Street Pins → Manage →
   App secret key → the copy icon). What you paste isn't shown on screen.
2. It opens Pinterest in the browser: click "Give access". Pinterest then shows our "Pinterest is connected" page with a
   one-time code: click "Copy code" and paste it into Terminal (also hidden).
3. It swaps the code for a long-lasting key and stores the secret and the key straight into GitHub's secret store, using
   the GitHub sign-in already on this Mac. Nothing is printed, saved to a file, or seen by anyone (Claude included).
It finishes by listing the board names it can see, as a check.
The key lasts a year; run this again next November (the Monday report will remind you).
"""
import base64
import getpass
import json
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

APP_ID = "1637347"
REDIRECT = "https://sparrowstreetstories.com/pinterest-callback.html"
SCOPES = "boards:read,pins:read,pins:write,user_accounts:read"
REPO = "sparrowstreetstories/sparrow-street-social"
GH = "/opt/homebrew/bin/gh"


def post(url, form, auth):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode(), method="POST",
                                 headers={"Authorization": "Basic " + base64.b64encode(auth.encode()).decode(),
                                          "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Pinterest said no ({e.code}). The code may have expired: run this again and paste the code straight away.")


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def store(name, value, secret=True):
    cmd = [GH, "secret" if secret else "variable", "set", name, "--repo", REPO]
    if secret:
        subprocess.run(cmd, input=value.encode(), check=True, capture_output=True)
    else:
        subprocess.run(cmd + ["--body", value], check=True, capture_output=True)


def main():
    print("Connecting Pinterest to the Sparrow Street robot.\n")
    secret = getpass.getpass("1) Paste the Pinterest App secret key (it won't show), then press Return: ").strip()
    if len(secret) < 20:
        sys.exit("That doesn't look like the secret key. Copy it again from the app's Configure page.")
    state = secrets.token_urlsafe(12)
    url = "https://www.pinterest.com/oauth/?" + urllib.parse.urlencode(
        {"client_id": APP_ID, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPES, "state": state})
    print("\n2) Opening Pinterest in your browser. Make sure you're signed in as Sparrow Street, click 'Give access',")
    print("   then click 'Copy code' on the page that opens.")
    webbrowser.open(url)
    code = getpass.getpass("\n3) Paste the code (it won't show), then press Return: ").strip()
    tok = post("https://api.pinterest.com/v5/oauth/token",
               {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT}, f"{APP_ID}:{secret}")
    refresh, access = tok.get("refresh_token"), tok.get("access_token")
    if not (refresh and access):
        sys.exit("Pinterest didn't return a key. Please run this again.")
    # store the keys first, so a hiccup in the checks below can't lose them
    store("PINTEREST_APP_SECRET", secret)
    store("PINTEREST_REFRESH_TOKEN", refresh)
    store("PINTEREST_APP_ID", APP_ID, secret=False)
    try:
        user = get("https://api.pinterest.com/v5/user_account", access).get("username", "?")
    except urllib.error.HTTPError:
        user = "?"
    try:
        boards = [b["name"] for b in get("https://api.pinterest.com/v5/boards?page_size=100", access).get("items", [])]
    except urllib.error.HTTPError:
        boards = []
    print(f"\n✅ Done. Connected to Pinterest as @{user}. Keys stored safely in GitHub.")
    print("   Boards I can see: " + (", ".join(boards) or "none"))
    print("   Tell Claude: \"Pinterest connected\".")


if __name__ == "__main__":
    main()
