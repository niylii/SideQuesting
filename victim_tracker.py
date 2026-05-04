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
VICTIM_LOGIN  = os.getenv("VICTIM_LOGIN")
WEBHOOK       = os.getenv("WEBHOOK")
WEBHOOK_VICTIM = os.getenv("WEBHOOK_VICTIM")
CAMPUS_ID     = int(os.getenv("CAMPUS_ID", "21"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

_missing = [k for k, v in {
    "CLIENT_ID": CLIENT_ID, "CLIENT_SECRET": CLIENT_SECRET,
    "victim_LOGIN": VICTIM_LOGIN, "WEBHOOK": WEBHOOK, "WEBHOOK_VICTIM": WEBHOOK_VICTIM
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


def check_victim(headers: dict) -> tuple[bool, str]:
    resp = requests.get(
        f"{API_URL}/v2/users/{VICTIM_LOGIN}/locations",
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
    DiscordWebhook(url=WEBHOOK_VICTIM, content=msg).execute()


def main() -> None:
    print(f" Tracker started : watching victim every {POLL_INTERVAL}s")

    token   = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    here, host = check_victim(headers)

    if here:
        notify(f"victim is here! at: **{host}**")
    else:
        notify("victim is not here yet …")

    victim_online = here

    while True:
        time.sleep(POLL_INTERVAL)

        try:
            token   = get_token()
            headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"[warn] token refresh failed: {e}")
            continue

        try:
            here, host = check_victim(headers)
        except Exception as e:
            print(f"[warn] API error: {e}")
            continue

        if here and not victim_online:
            notify(f"victim is at **{host}**")

        elif not here and victim_online:
            notify("victim is gone!")

        victim_online = here


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[stopped] Tracker killed.")
