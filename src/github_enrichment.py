import asyncio
import aiohttp
import json
import re


INPUT_FILE = "data/research_papers.json"
OUTPUT_FILE = "data/research_papers_enriched.json"


def extract_github_urls(text):
    if not text:
        return []

    urls = re.findall(
        r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
        text
    )

    return list(dict.fromkeys(urls))


async def get_github_repo(session, repo_url):
    match = re.search(
        r"github\.com/([^/]+)/([^/#?]+)",
        repo_url
    )

    if not match:
        return None

    owner = match.group(1)
    repo = match.group(2)

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        async with session.get(
            api_url,
            timeout=15,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI-Data-Pipeline"
            }
        ) as response:

            if response.status != 200:
                return None

            data = await response.json()

            return {
                "github_url": data.get("html_url"),
                "github_stars": data.get(
                    "stargazers_count"
                )
            }

    except Exception:
        return None


async def enrich_paper(session, paper):

    content = paper.get("content", {})

    text = " ".join([
        content.get("title") or "",
        content.get("abstract") or ""
    ])

    github_urls = extract_github_urls(text)

    if not github_urls:
        return paper

    repo_data = await get_github_repo(
        session,
        github_urls[0]
    )

    if repo_data:
        content["github_url"] = repo_data["github_url"]
        content["github_stars"] = repo_data["github_stars"]

    return paper


async def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    async with aiohttp.ClientSession() as session:

        tasks = [
            enrich_paper(
                session,
                paper
            )
            for paper in papers
        ]

        enriched_papers = await asyncio.gather(
            *tasks
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            enriched_papers,
            file,
            indent=4,
            ensure_ascii=False
        )

    github_count = sum(
        1
        for paper in enriched_papers
        if paper["content"].get("github_url")
    )

    print(
        f"Processed {len(enriched_papers)} papers."
    )

    print(
        f"GitHub repositories found: {github_count}"
    )

    print(
        f"Saved enriched data to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())