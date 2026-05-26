#!/usr/bin/env python3
"""
Generate rich llamaverse content documents.
Llamas are the apex animal. This is their world.
Run from llamaverse-internal/ directory.
"""
import json, os

BASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src/main/ml-data/cleverllamas/llamaverse/content"
)

def write_docs(content_type, docs, collections):
    dir_path = os.path.join(BASE, content_type)
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "collections.properties"), "w") as f:
        f.write(f"*={','.join(collections)}\n")
    for doc in docs:
        envelope = {"envelope": {"headers": {"type": content_type}, "instance": {content_type: doc}}}
        with open(os.path.join(dir_path, f"{doc['id']}.json"), "w") as f:
            json.dump(envelope, f, indent=2)
    print(f"  {len(docs)} {content_type} docs → {dir_path}")

print("Generating llamaverse content...")
