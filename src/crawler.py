import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json


async def fetch_website(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.get_text(strip=True) if soup.title else "No title"

            headings = []
            for heading in soup.find_all(["h1", "h2", "h3"]):
                text = heading.get_text(" ", strip=True)
                if text:
                    headings.append(text)

            paragraphs = []
            for paragraph in soup.find_all("p"):
                text = paragraph.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)

            return {
                "url": url,
                "status": response.status,
                "title": title,
                "headings": headings,
                "paragraphs": paragraphs
            }

    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }


async def main():
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_website(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    with open("data/raw_data.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print("Data saved successfully!")


asyncio.run(main())