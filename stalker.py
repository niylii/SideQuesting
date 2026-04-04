#!/usr/bin/env python3

import requests
from discord_webhook import DiscordWebhook

API_URL = "https://api.intra.42.fr"

CLIENT_ID = ""
CLIENT_SECRET = ""
POST = ""
MY_LOGIN = ""

WEBHOOK = ""

def get_token(url, ID, secret):
    response = requests.post(f"{url}/oauth/token", data={'grant_type': 'client_credentials',
                                        'client_id': ID, 'client_secret': secret})
    token = response.json()
    return(token.get('access_token'))

def get_post(url, headers):
    response = requests.get(f"{url}/v2/campus/21/locations?filter[host]={POST}", headers=headers)
    history = response.json()
    return history[0]

if __name__ == "__main__":
    token = get_token(API_URL, CLIENT_ID, CLIENT_SECRET);
    headers = {
        'Authorization': f"Bearer {token}"
    }

    current_state = get_post(API_URL, headers)
    data = {
        'is_logged_in': current_state.get('end_at') is None,
        'who_is_logged_in': current_state["user"]["login"]
    }

    if MY_LOGIN not in data and False in data:
        webhook = DiscordWebhook(
            url=WEBHOOK,
            content=f"JRII"
        )
        response = webhook.execute()
    else:
        webhook = DiscordWebhook(
            url=WEBHOOK,
            content=f"Maendk zhr"
        )
        response = webhook.execute()
