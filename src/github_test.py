import aiohttp
import asyncio
import json


ORGANIZATIONS = [
    "openai",
    "huggingface",
    "pytorch",
    "tensorflow",
    "nvidia"
]


async def get_github_data(session, org_name):
    url = f"https://api.github.com/orgs/{org_name}"

    try:
        async with session.get(url) as response:
            data = await response.json()

            if response.status != 200:
                return {
                    "organization": org_name,
                    "error": data.get("message", "Unknown error")
                }

            return {
                "schemaVersion": "1.0",
                "recordType": "STARTUP",
                "source": {
                    "name": "GitHub API",
                    "url": url
                },
                "content": {
                    "entityName": data.get("login"),
                    "data": {
                        "website": data.get("blog"),
                        "publicRepositories": data.get("public_repos")
                    }
                },
                "collectedAt": "2026-09-10T00:00:00Z"
            }

    except Exception as e:
        return {
            "organization": org_name,
            "error": str(e)
        }


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_github_data(session, org)
            for org in ORGANIZATIONS
        ]

        results = await asyncio.gather(*tasks)

    with open(
        "data/startup_records.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print(f"Saved {len(results)} startup records successfully!")


asyncio.run(main())