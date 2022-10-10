import asyncio
from collections import namedtuple
import json
import os
import sys
import time

import httpx

MEILI_URL = "http://localhost:7700/indexes/clashes/documents"
MEILI_UPDATE_KEY = os.environ.get("MEILI_UPDATE_KEY")
# the timestamp of the most recent update (as epoch time in milliseconds)
LAST_UPDATED_TIME = int(os.environ.get("LAST_UPDATED_TIME") or 1665000000000)

ClashCheckResult = namedtuple("ClashCheckResult", ["updated_count", "timestamp"])


def time_ms():
    return time.time_ns() // 1000000


def explanation(exc: httpx.HTTPError):
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    else:
        return type(exc).__name__


async def get_clash(session, clash_handle):
    response = await session.post(
        "https://www.codingame.com/services/Contribution/findContribution",
        json=[clash_handle, True]  # not sure what the True is for but it is required
    )
    response.raise_for_status()
    return response


async def check_clash_updates(session, last_updated_time) -> ClashCheckResult:
    updated_count = 0
    this_update_time = time_ms()
    print(f"{this_update_time} : Checking for new clashes...")
    try:
        resp = await session.post(
            "https://www.codingame.com/services/Contribution/getAcceptedContributions",
            json=["CLASHOFCODE"]
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"{last_updated_time} : Failed to get clashes ({explanation(exc)})")
        return ClashCheckResult(0, last_updated_time)

    with open("list_of_clashes.json", "w") as f:
        f.write(resp.text)

    updated_clashes = []
    clashes = resp.json()

    for clash in clashes:
        statuses = clash["statusHistory"]
        clash_timestamps = [status["date"] for status in statuses]
        clash_latest_update = max(clash_timestamps, default=0)
        if clash_latest_update > last_updated_time:
            updated_count += 1
            clash_title = clash["title"]
            clash_creator = clash.get("nickname", "Unknown")
            clash_handle = clash["publicHandle"]
            print(f"- New/updated clash '{clash_title}' by {clash_creator}")
            try:
                response = await get_clash(session, clash_handle)
            except httpx.HTTPError as exc:
                print(f"Problem fetching clash ({explanation(exc)})")
                return ClashCheckResult(0, last_updated_time)
            else:
                updated_clashes.append((clash_handle, response.text))

    if updated_count > 0:
        for clash_handle, clash_text in updated_clashes:
            # TODO: also put new clash to meilisearch
            with open(f"clashes/{clash_handle}.json", "w") as f:
                f.write(clash_text)

        if MEILI_UPDATE_KEY:
            new_docs = [json.loads(clash_text) for _, clash_text in updated_clashes]
            try:
                httpx.post(
                    MEILI_URL,
                    headers={"Authorization": f"Bearer {MEILI_UPDATE_KEY}"},
                    json=new_docs
                ).raise_for_status()
            except httpx.HTTPError as exc:
                print(f"- Failed to update MeiliSearch index! ({explanation(exc)})")
            else:
                print("- Successfully updated MeiliSearch index!")
    

    return ClashCheckResult(updated_count, this_update_time)


async def amain():
    last_updated_time = LAST_UPDATED_TIME
    check_interval = 3600  # seconds
    cookies = httpx.Cookies()
    # the CODINGAME_COOKIES environment variable should have a value
    # like this (can be copy-pasted from Firefox dev tools):
    # CODINGAME_COOKIES="Cookie: rememberMe=badc0de; AWSALB=BaDcOdE+EvEnWoRsECoDe==; AWSALBCORS=BaDcOdE+EvEnWoRsECoDe==; cgSession=baaaaaad-1337-c0de-abcdef123456"
    secret_cookies = os.environ.get("CODINGAME_COOKIES")
    if secret_cookies:
        for part in secret_cookies.removeprefix("Cookie: ").split("; "):
            k, _, v = part.partition("=")
            cookies.set(k, v)
    else:
        print("[WARNING] CODINGAME_COOKIES is not set, this might not work", file=sys.stderr)

    async with httpx.AsyncClient(cookies=cookies) as session:
        while True:
            r = await check_clash_updates(session, last_updated_time)
            updated_count = r.updated_count
            if r.timestamp > last_updated_time:
                last_updated_time = r.timestamp
                if updated_count > 0:
                    print(f"{last_updated_time} : Updated information for {updated_count} new clashes")
                else:
                    print(f"{last_updated_time} : No new clashes")
            print("...sleeping...")
            await asyncio.sleep(check_interval)


if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("\nQuitting (interrupted by user)")
