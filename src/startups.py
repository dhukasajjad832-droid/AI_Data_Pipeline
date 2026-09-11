import asyncio
import aiohttp
import json
from datetime import datetime, timezone


GITHUB_SEARCH_URL = (
    "https://api.github.com/search/users"
    "?q=type:org+AI"
    "&per_page=100"
    "&page={page}"
)


async def fetch_page(session, page):
    url = GITHUB_SEARCH_URL.format(page=page)

    try:
        async with session.get(
            url,
            timeout=30,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI-Data-Pipeline"
            }
        ) as response:

            print(
                f"GitHub page {page} -> "
                f"Status: {response.status}"
            )

            if response.status != 200:
                return []

            data = await response.json()

            return data.get("items", [])

    except Exception as e:
        print(f"Page {page} -> Error: {e}")
        return []


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_page(session, page)
            for page in range(1, 11)
        ]

        pages = await asyncio.gather(*tasks)

    organizations = []

    for items in pages:
        organizations.extend(items)

    # Remove duplicates
    unique = {}

    for org in organizations:
        login = org.get("login")

        if login:
            unique[login.lower()] = org

    organizations = list(unique.values())[:1000]

    collected_at = datetime.now(
        timezone.utc
    ).isoformat()

    records = []

    for org in organizations:

        login = org.get("login")

        records.append({
            "schemaVersion": "1.0",
            "recordType": "STARTUP",
            "source": {
                "name": "GitHub Search API",
                "url": org.get("html_url")
            },
            "content": {
                "entityName": login,
                "data": {
                    "githubLogin": login,
                    "githubUrl": org.get("html_url"),
                    "avatarUrl": org.get("avatar_url"),
                    "classification": "STARTUP_CANDIDATE",
                    "verification": "GITHUB_ORGANIZATION"
                }
            },
            "collectedAt": collected_at
        })

    with open(
        "data/startup_records_1000.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nSaved {len(records)} "
        "startup candidate records!"
    )


if __name__ == "__main__":
    asyncio.run(main())