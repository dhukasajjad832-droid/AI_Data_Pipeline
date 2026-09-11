import asyncio
import aiohttp
import json
import re

from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse


NEWS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/"
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence"
    },
    {
        "name": "Ars Technica AI",
        "url": "https://arstechnica.com/ai/"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/"
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/"
    }
]


MAX_ARTICLES_PER_SOURCE = 10


def parse_datetime(value):
    if not value:
        return None

    value = value.strip()

    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")

        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except ValueError:
        pass

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%B %d, %Y",
        "%b %d, %Y"
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=timezone.utc)

        except ValueError:
            continue

    return None


def extract_published_date(soup):
    possible_values = []

    meta_names = [
        "article:published_time",
        "datePublished",
        "date",
        "pubdate",
        "publishdate",
        "parsely-pub-date"
    ]

    for name in meta_names:
        tag = soup.find(
            "meta",
            attrs={"property": name}
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"name": name}
            )

        if tag:
            value = (
                tag.get("content")
                or tag.get("value")
            )

            if value:
                possible_values.append(value)

    time_tag = soup.find("time")

    if time_tag:
        possible_values.append(
            time_tag.get("datetime", "")
        )

        possible_values.append(
            time_tag.get_text(
                " ",
                strip=True
            )
        )

    for value in possible_values:
        parsed = parse_datetime(value)

        if parsed:
            return parsed

    # Try JSON-LD structured data
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        text = script.get_text(
            strip=True
        )

        match = re.search(
            r'"datePublished"\s*:\s*"([^"]+)"',
            text
        )

        if match:
            parsed = parse_datetime(
                match.group(1)
            )

            if parsed:
                return parsed

    return None


def is_last_24_hours(published_date):
    if published_date is None:
        return False

    now = datetime.now(timezone.utc)

    twenty_four_hours_ago = (
        now - timedelta(hours=24)
    )

    return (
        twenty_four_hours_ago
        <= published_date
        <= now
    )


def extract_article_links(html, source_url):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = []

    for anchor in soup.find_all("a", href=True):

        href = anchor["href"]

        full_url = urljoin(
            source_url,
            href
        )

        parsed = urlparse(full_url)

        if parsed.scheme not in [
            "http",
            "https"
        ]:
            continue

        links.append(full_url)

    # Remove duplicates while keeping order
    unique_links = list(
        dict.fromkeys(links)
    )

    return unique_links


def extract_article_data(
    html,
    url,
    source_name,
    published_date
):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title = None

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True
        )

    description = ""

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta_description:
        description = (
            meta_description.get("content")
            or ""
        ).strip()

    paragraphs = []

    for paragraph in soup.find_all("p"):

        text = paragraph.get_text(
            " ",
            strip=True
        )

        if text and len(text) > 30:
            paragraphs.append(text)

        if len(paragraphs) >= 10:
            break

    published_iso = None

    if published_date:
        published_iso = published_date.isoformat()

    collected_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "schemaVersion": "1.0",
        "recordType": "NEWS",

        "source": {
            "name": source_name,
            "url": url
        },

        "content": {
            "title": title,
            "description": description,
            "publishedDate": published_iso,
            "freshness": (
                "FRESH_24H"
                if is_last_24_hours(
                    published_date
                )
                else "STALE_OR_UNKNOWN"
            ),
            "paragraphs": paragraphs
        },

        "collectedAt": collected_at
    }


async def fetch_source(
    session,
    source
):
    try:

        async with session.get(
            source["url"],
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/153.0 Safari/537.36"
                )
            }
        ) as response:

            html = await response.text()

            print(
                f"{source['name']} -> "
                f"Status: {response.status}"
            )

            if response.status != 200:
                return []

            links = extract_article_links(
                html,
                source["url"]
            )

            # Limit requests
            links = links[
                :MAX_ARTICLES_PER_SOURCE
            ]

            tasks = [
                fetch_article(
                    session,
                    source["name"],
                    link
                )
                for link in links
            ]

            results = await asyncio.gather(
                *tasks
            )

            return [
                result
                for result in results
                if result is not None
            ]

    except Exception as e:

        print(
            f"{source['name']} -> Error: {e}"
        )

        return []


async def fetch_article(
    session,
    source_name,
    url
):
    try:

        async with session.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/153.0 Safari/537.36"
                )
            }
        ) as response:

            if response.status != 200:
                return None

            html = await response.text()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            published_date = extract_published_date(
                soup
            )

            return extract_article_data(
                html,
                url,
                source_name,
                published_date
            )

    except Exception:
        return None


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_source(
                session,
                source
            )
            for source in NEWS_SOURCES
        ]

        source_results = await asyncio.gather(
            *tasks
        )

        all_records = []

        for records in source_results:
            all_records.extend(records)

        # Remove duplicate article URLs
        unique_records = {}

        for record in all_records:

            url = record["source"]["url"]

            unique_records[url] = record

        all_records = list(
            unique_records.values()
        )

        fresh_records = [
            record
            for record in all_records
            if record["content"]["freshness"]
            == "FRESH_24H"
        ]

        stale_or_unknown_records = [
            record
            for record in all_records
            if record["content"]["freshness"]
            != "FRESH_24H"
        ]

        # Assignment requirement:
        # only keep content published in the last 24 hours.
        all_records = fresh_records

        output = {
            "generatedAt": datetime.now(
                timezone.utc
            ).isoformat(),

            "totalCollected": len(
                all_records
            ),

            "freshLast24Hours": len(
                fresh_records
            ),

            "staleOrUnknown": len(
                stale_or_unknown_records
            ),

            "records": all_records
        }

        with open(
            "data/news_records.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            "\nNews collection completed!"
        )

        print(
            f"Fresh articles saved: "
            f"{len(all_records)}"
        )

        print(
            f"Fresh last 24 hours: "
            f"{len(fresh_records)}"
        )

        print(
            f"Stale/unknown excluded: "
            f"{len(stale_or_unknown_records)}"
        )

        print(
            "\nSaved to "
            "data/news_records.json"
        )


if __name__ == "__main__":
    asyncio.run(main())