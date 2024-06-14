import json

from base64 import b64encode
from pathlib import Path

from openai import OpenAI


RESTRICTION: str = """
Do NOT include anything besides valid JSON in your answer.

Do NOT format as markdown - return raw JSON document.
"""


DESCRIBE_DOCUMENT: str = """
Here is an image. It can be an invoice, damaged product photo or something else.

Give a JSON object with following structure:

{
    "type": <INVOICE, PRODUCT or OTHER>,
    "text": <free-form textual representation of picture content>
}
"""


ANALYZE_PRODUCT: str = """
Here is a description of a possibly damaged product.

Give a JSON object with following structure:

{
    "product": <free-form, short text with product name, e.g. Coca-Cola>,
    "damaged": <float from 0.0 to 1.0, where 0.0 - not damaged, 1.0 - completely destroyed>,
    "damages": [
        <short name for each damage type, e.g. scratches>
    ]
}

If more significant damage type implies more significant - include only more significant one.
For example, if Coca-Cola bottle is crushed - omit scratches from damage types.
"""


def describe(
    client: OpenAI,
    path: Path,
    content_type: str,
    *,
    prompt: str = DESCRIBE_DOCUMENT,
) -> dict:
    if not content_type.startswith("image"):
        message = f"Only image/* content is supported, got {content_type}"
        raise ValueError(message)

    data = b64encode(path.read_bytes()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "\n".join([prompt, RESTRICTION]),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{data}",
                        },
                    },
                ],
            }
        ],
        max_tokens=800,
        stream=False,
    )

    return json.loads(response.choices[0].message.content)


def analyze(
    client: OpenAI,
    description: dict[str, str],
    prompt: str = ANALYZE_PRODUCT,
) -> dict:
    if description["type"] != "PRODUCT":
        message = "Can analyze only product images, not {}".format(description["type"])
        raise ValueError(message)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "\n".join([prompt, RESTRICTION]),
                    },
                    {
                        "type": "text",
                        "text": description["text"],
                    },
                ],
            }
        ],
        max_tokens=800,
        stream=False,
    )

    return json.loads(response.choices[0].message.content)
