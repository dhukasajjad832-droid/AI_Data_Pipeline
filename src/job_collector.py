import asyncio
import aiohttp
import json
from datetime import datetime, timezone


JOB_SOURCES = [
    {
        "name": "LinkedIn Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=AI"
    },
    {
        "name": "Indeed",
        "url": "https://www.indeed.com/jobs?q=artificial+intelligence"
    },
    {
        "name": "Wellfound",
        "url": "https://wellfound.com/jobs"
    },
    {
        "name": "Y Combinator Jobs",
        "url": "https://www.ycombinator.com/jobs"
    },
    {
        "name": "Remote OK",
        "url": "https://remoteok.com/remote-ai-jobs"
    }
]


def check_freshness(collected_at):
    collected_time = datetime.fromisoformat(collected_at)

    now = datetime.now(timezone.utc)

    age_hours = (
        now - collected_time
    ).total_seconds() / 3600

    if age_hours <= 24:
        return "FRESH"

    return "STALE"


async def fetch_job_source(session, source):
    try:
        async with session.get(
            source["url"],
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        ) as response:

            text = await response.text()

            print(
                f"{source['name']} -> Status: {response.status}"
            )

            collected_at = datetime.now(
                timezone.utc
            ).isoformat()

            freshness = check_freshness(
                collected_at
            )

            return {
                "schemaVersion": "1.0",
                "recordType": "JOB",
                "source": {
                    "name": source["name"],
                    "url": source["url"]
                },
                "content": {
                    "company": None,
                    "date": None,
                    "is_remote": None,
                    "role_family": "AI",
                    "freshness": freshness,
                    "rawTextLength": len(text)
                },
                "collectedAt": collected_at
            }

    except Exception as e:
        print(
            f"{source['name']} -> Error: {e}"
        )
        return None


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_job_source(session, source)
            for source in JOB_SOURCES
        ]

        results = await asyncio.gather(*tasks)

        results = [
            result
            for result in results
            if result is not None
        ]

        with open(
            "data/job_records.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\nSaved {len(results)} job source records successfully!"
        )


if __name__ == "__main__":
    asyncio.run(main())