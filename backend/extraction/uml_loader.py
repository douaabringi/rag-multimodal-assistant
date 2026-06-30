import base64
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def extract_text_from_uml(file_path: str) -> str:
    cache_path = file_path + ".cache.txt"

    if os.path.exists(cache_path):
        print(" Description UML chargée depuis le cache")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    print(" Analyse UML par Groq Vision...")
    image_data = image_to_base64(file_path)

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this UML diagram in detail. List:
1. The type of diagram
2. ALL actors, classes, or elements present with their EXACT names
3. ALL relationships and connections between elements
4. ALL labels on arrows (include, extend, etc.)
Be exhaustive and precise."""
                    }
                ]
            }
        ],
        max_tokens=1024
    )

    description = response.choices[0].message.content

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(description)
    print(" Description sauvegardée dans le cache")

    return description