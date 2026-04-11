#!/usr/bin/env python3
import os
import sys
import time
import requests
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv

load_dotenv()

API_URL       = "https://api.intra.42.fr"
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SHEILA_LOGIN  = os.getenv("SHEILA_LOGIN")
WEBHOOK       = os.getenv("WEBHOOK")
WEBHOOK_SHEILA = os.getenv("WEBHOOK_SHEILA")
CAMPUS_ID     = int(os.getenv("CAMPUS_ID", "21"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

_missing = [k for k, v in {
    "CLIENT_ID": CLIENT_ID, "CLIENT_SECRET": CLIENT_SECRET,
    "SHEILA_LOGIN": SHEILA_LOGIN, "WEBHOOK": WEBHOOK, "WEBHOOK_SHEILA": WEBHOOK_SHEILA
}.items() if not v]
if _missing:
    print(f"[error] Missing .env variables: {', '.join(_missing)}")
    sys.exit(1)


def get_token() -> str:
    resp = requests.post(
        f"{API_URL}/oauth/token",
        data={
            "grant_type":    "client_credentials",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def check_sheila(headers: dict) -> tuple[bool, str]:
    resp = requests.get(
        f"{API_URL}/v2/users/{SHEILA_LOGIN}/locations",
        params={
            "filter[active]": "true",
            "per_page":       1,
        },
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    records = resp.json()

    if not records:
        return False, ""

    return True, records[0].get("host", "?")


def notify(msg: str) -> None:
    DiscordWebhook(url=WEBHOOK_SHEILA, content=msg).execute()


def main() -> None:
    print(f"👀 Tracker started — watching sheishei every {POLL_INTERVAL}s")

    token   = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    here, host = check_sheila(headers)

    if here:
        notify(f"Sheila is heeere ! life is worth living lol ✨\n📍 Post: **{host}**")
    else:
        notify("😔 Sheila is not here yet …")

    sheila_online = here

    while True:
        time.sleep(POLL_INTERVAL)

        try:
            token   = get_token()
            headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"[warn] token refresh failed: {e}")
            continue

        try:
            here, host = check_sheila(headers)
        except Exception as e:
            print(f"[warn] API error: {e}")
            continue

        if here and not sheila_online:
            notify(f"Sheila is heeere !!! spark spark ✨\n📍 Post: **{host}**")

        elif not here and sheila_online:
            notify("👋 Sheila is gone!")

        sheila_online = here


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[stopped] Tracker killed.")
