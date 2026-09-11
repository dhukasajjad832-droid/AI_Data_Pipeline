import asyncio
import aiohttp
import json
import ssl
from datetime import datetime, timezone


HF_API_URL = (
    "https://huggingface.co/api/models"
    "?sort=downloads"
    "&direction=-1"
    "&limit=1000"
)


async def fetch_models():

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
            HF_API_URL,
            timeout=60,
            headers={
                "User-Agent": "AI-Data-Pipeline"
            }
        ) as response:

            print(
                f"Hugging Face API -> "
                f"Status: {response.status}"
            )

            if response.status != 200:
                print(
                    "Could not fetch Hugging Face models."
                )
                return

            models = await response.json()

            records = []

            collected_at = datetime.now(
                timezone.utc
            ).isoformat()

            for model in models:

                model_id = model.get("id")

                if not model_id:
                    continue

                downloads = model.get(
                    "downloads"
                )

                likes = model.get(
                    "likes"
                )

                pipeline_tag = model.get(
                    "pipeline_tag"
                )

                tags = model.get(
                    "tags",
                    []
                )

                records.append({
                    "schemaVersion": "1.0",
                    "recordType": "PRODUCT",

                    "source": {
                        "name": "Hugging Face Hub",
                        "url": (
                            f"https://huggingface.co/"
                            f"{model_id}"
                        )
                    },

                    "content": {
                        "productName": model_id,
                        "description": (
                            f"AI/ML model hosted on "
                            f"Hugging Face Hub"
                        ),
                        "pricing": "UNKNOWN",
                        "category": (
                            pipeline_tag
                            or "AI_MODEL"
                        ),
                        "downloads": downloads,
                        "likes": likes,
                        "tags": tags
                    },

                    "collectedAt": collected_at
                })

            with open(
                "data/product_records.json",
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
                "real product/model records!"
            )


if __name__ == "__main__":
    asyncio.run(fetch_models())