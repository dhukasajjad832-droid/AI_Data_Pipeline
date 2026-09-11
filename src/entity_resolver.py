import re
import json


CANONICAL_ENTITIES = {
    "openai": "OpenAI",
    "openai inc": "OpenAI",
    "open ai": "OpenAI",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "nvidia": "NVIDIA"
}


def normalize_name(name):
    name = name.lower().strip()
    name = re.sub(r"[.,]", "", name)
    name = re.sub(r"\s+", " ", name)

    return name


def resolve_entity(name):
    normalized = normalize_name(name)

    return CANONICAL_ENTITIES.get(
        normalized,
        name
    )


test_names = [
    "OpenAI",
    "OpenAI, Inc.",
    "Open AI",
    "HuggingFace",
    "NVIDIA"
]


mapping_log = []

for name in test_names:
    canonical = resolve_entity(name)

    mapping_log.append({
        "rawName": name,
        "canonicalName": canonical
    })


with open(
    "data/entity_mapping_log.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        mapping_log,
        file,
        indent=4,
        ensure_ascii=False
    )


print("Entity mapping log saved successfully!")