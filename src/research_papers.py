import asyncio
import aiohttp
import json
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


ARXIV_URL = (
    "https://export.arxiv.org/api/query"
    "?search_query=cat:cs.AI"
    "&start=0"
    "&max_results=1000"
)


async def fetch_papers():

    # Local SSL certificate issue workaround
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        async with session.get(
            ARXIV_URL,
            timeout=30
        ) as response:

            print(
                f"arXiv API -> Status: {response.status}"
            )

            xml_data = await response.text()

            if response.status != 200:
                print(
                    "Could not fetch arXiv data."
                )
                return

            root = ET.fromstring(
                xml_data
            )

            namespace = {
                "atom": "http://www.w3.org/2005/Atom"
            }

            records = []

            for entry in root.findall(
                "atom:entry",
                namespace
            ):

                title = entry.find(
                    "atom:title",
                    namespace
                )

                summary = entry.find(
                    "atom:summary",
                    namespace
                )

                published = entry.find(
                    "atom:published",
                    namespace
                )

                paper_id = entry.find(
                    "atom:id",
                    namespace
                )

                authors = []

                for author in entry.findall(
                    "atom:author",
                    namespace
                ):

                    name = author.find(
                        "atom:name",
                        namespace
                    )

                    if name is not None:
                        authors.append(
                            name.text.strip()
                        )

                records.append(
                    {
                        "schemaVersion": "1.0",

                        "recordType": "RESEARCH_PAPER",

                        "source": {
                            "name": "arXiv",
                            "url": (
                                paper_id.text.strip()
                                if paper_id is not None
                                else None
                            )
                        },

                        "content": {

                            "title": (
                                title.text.strip()
                                if title is not None
                                else None
                            ),

                            "authors": authors,

                            "abstract": (
                                summary.text.strip()
                                if summary is not None
                                else None
                            ),

                            "paper_url": (
                                paper_id.text.strip()
                                if paper_id is not None
                                else None
                            ),

                            "github_url": None,

                            "github_stars": None,

                            "published_date": (
                                published.text.strip()
                                if published is not None
                                else None
                            )
                        },

                        "collectedAt": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }
                )

            with open(
                "data/research_papers.json",
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
                f"Saved {len(records)} "
                "research paper records successfully!"
            )


if __name__ == "__main__":
    asyncio.run(
        fetch_papers()
    )