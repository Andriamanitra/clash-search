import asyncio
import os
from pathlib import Path
import pickle
import sys
import time

import httpx

MEILI_URL = os.environ["VITE_MEILI_URL"] + "/indexes/clashes/documents"
MEILI_UPDATE_KEY = os.environ["MEILI_UPDATE_KEY"]
DATADIR = Path(__file__).parent.parent / "data"

class MeiliUpdateException(Exception): pass


def info(*args, **kwargs):
    tstamp = time.strftime("[%b %d %H:%M:%S GMT]", time.gmtime())
    print(tstamp, *args, **kwargs)

def explanation(exc: httpx.HTTPError):
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    else:
        return type(exc).__name__

async def find_contribution(session, clash_handle):
    response = await session.post(
        "https://www.codingame.com/services/Contribution/findContribution",
        json=[clash_handle, True]  # not sure what the True is for but it is required
    )
    response.raise_for_status()
    return response

async def get_accepted_contributions(session, kind="CLASHOFCODE"):
    response = await session.post(
        "https://www.codingame.com/services/Contribution/getAcceptedContributions",
        json=[kind]
    )
    response.raise_for_status()
    return response

async def update_clashes(session):
    clashversions_pickle = DATADIR / "clashversions.pickle"
    # 1. get dict of latest versions
    if clashversions_pickle.exists():
        with open(clashversions_pickle, "rb") as f:
            stored_version = pickle.load(f)
    else:
        stored_version = {}

    # 2. fetch list of clashes & store file
    response = await get_accepted_contributions(session)
    with open(DATADIR / "list_of_clashes.json", "w") as f:
        f.write(response.text)
    clashes = response.json()

    # 3. check which ones are new/updated & request them from api
    updated_clashes = []
    for clash in clashes:
        clash_handle = clash["publicHandle"]

        if stored_version.get(clash_handle, -1) >= clash["activeVersion"]:
            continue

        clash_title = clash["title"]
        clash_creator = clash.get("nickname", "Unknown")
        info(f"New/updated clash '{clash_title}' by {clash_creator}")

        response = await find_contribution(session, clash_handle)
        # sleep 1 second to avoid sending too many requests, we are in no rush
        await asyncio.sleep(1)
        updated_clash_json = response.json()
        updated_clashes.append(updated_clash_json)

        # 4. save file
        with open(DATADIR / "clashes" / f"{clash_handle}.json", "w") as f:
            f.write(response.text)

    if not updated_clashes:
        return

    # 5. upload to meili
    try:
        httpx.post(
            MEILI_URL+"?primaryKey=publicHandle",
            headers={"Authorization": f"Bearer {MEILI_UPDATE_KEY}"},
            json=updated_clashes
        ).raise_for_status()
    except httpx.HTTPError as exc:
        raise MeiliUpdateException(f"Failed to update MeiliSearch index ({explanation(exc)})") from exc

    # 6. update latest versions dict
    for clash in updated_clashes:
        stored_version[clash["publicHandle"]] = clash["activeVersion"]
    with open(clashversions_pickle, "wb") as f:
        pickle.dump(stored_version, f)
    info("Successfully updated MeiliSearch index!")



async def amain():
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

    async with httpx.AsyncClient(cookies=cookies, timeout=15.0) as session:
        while True:
            try:
                info("Attempting to update clashes...")
                await update_clashes(session)
            except httpx.HTTPError as exc:
                info(f"Failed to get clashes ({explanation(exc)})")
            except MeiliUpdateException as exc:
                info(exc)

            info("...sleeping...")
            await asyncio.sleep(check_interval)


if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        info("Quitting (interrupted by user)")
