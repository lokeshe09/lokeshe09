"""Shared GitHub GraphQL helpers for the live cards."""
import json
import os
import sys
import urllib.request
from datetime import date, datetime


def token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok:
        sys.exit("GITHUB_TOKEN is required")
    return tok


def gql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def created_on(login):
    raw = gql(f'{{ user(login:"{login}"){{ createdAt }} }}')["user"]["createdAt"]
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()


def calendar(login):
    """{date: contributionCount} for every day from account creation through today (UTC)."""
    created = created_on(login)
    today = datetime.utcnow().date()
    parts = [
        f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z")'
        "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }"
        for y in range(created.year, today.year + 1)
    ]
    data = gql(f'{{ user(login:"{login}") {{ {" ".join(parts)} }} }}')["user"]
    days = {}
    for block in data.values():
        for wk in block["contributionCalendar"]["weeks"]:
            for d in wk["contributionDays"]:
                dd = date.fromisoformat(d["date"])
                if dd <= today:
                    days[dd] = d["contributionCount"]
    return days, today
