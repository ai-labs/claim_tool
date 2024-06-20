import json
import logging

from base64 import b64encode
from pathlib import Path

from openai import OpenAI

from ailabs.claims.database.models import CLAIM, RESULT, DOCUMENT


RESTRICTION: str = """
Do NOT include anything besides valid JSON in your answer.

Do NOT format as markdown - return raw JSON document.
"""

ANALYZE_DOCUMENT: str = """
Here is a document. Analyze it and provide following data:

 - is document appropriate and relevant to the claim description
 - document summary; free-form text
 - material number, if exists

Give a JSON output with following structure:

{
    "relevant": <bool>,
    "material": <material number or null>,
    "summary": <free-form textual representation of the document>,
}
"""


ANALYZE_DOCUMENTS: str = """
Here is a documents (photos) related to the possibly damaged product.

Give a JSON output with following structure:

{
    "description": <free-form textual representation of documents' content>,
    "department": <recommendation of the department that should process such a claim>,
    "damage": {
        "factor": <float from 0.0 to 1.0, where 0.0 - not damaged, 1.0 - completely destroyed>,
        "damage": <short summary of the damages>
    }
}
"""


# DESCRIBE_DOCUMENT: str = """
# Here is an image. It can be an invoice, damaged product photo or something else.

# Give a JSON object with following structure:

# {
#     "type": <INVOICE, PRODUCT or OTHER>,
#     "text": <free-form textual representation of picture content>
# }
# """


# ANALYZE_PRODUCT: str = """
# Here is a description of a possibly damaged product.

# Give a JSON object with following structure:

# {
#     "product": <free-form, short text with product name, e.g. Coca-Cola>,
#     "damaged": <float from 0.0 to 1.0, where 0.0 - not damaged, 1.0 - completely destroyed>,
#     "damages": [
#         <short name for each damage type, e.g. scratches>
#     ]
# }

# If more significant damage type implies more significant - include only more significant one.
# For example, if Coca-Cola bottle is crushed - omit scratches from damage types.
# """


def analyze(
    client: OpenAI,
    claim: CLAIM,
    document: DOCUMENT,
    documents: list[DOCUMENT],
) -> RESULT:
    if document is not None and not document.type.startswith("image"):
        logger.warning("Unsupported document type: %s", document.type)
        document = None

    for index, file in enumerate(documents.copy()):
        if not file.type.startswith("image"):
            logger.warning("Unsupported document type: %s", file.type)
            del documents[index]

    result = {"document": None, "response": None}

    # analyze document, if any

    if document:
        request = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "\n".join([ANALYZE_DOCUMENT, RESTRICTION]),
                    },
                    {
                        "type": "text",
                        "text": f"Claim description: {claim.description}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{document.type};base64,{b64encode(document.data).decode('utf-8')}",
                        },
                    },
                ],
            }
        ]

        response = client.chat.completions.create(
            # model="gpt-4-vision-preview",
            model="gpt-4-turbo",
            messages=request,
            max_tokens=800,
            stream=False,
        )

        result["document"] = json.loads(response.choices[0].message.content)

    # analyse claim

    if documents:
        request = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "\n".join([ANALYZE_DOCUMENTS, RESTRICTION]),
                    },
                    # {
                    #     "type": "text",
                    #     "text": f"Claim description: {claim.description}",
                    # },
                ],
            }
        ]

        for document in documents:
            part = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{document.type};base64,{b64encode(document.data).decode('utf-8')}",
                },
            }

            request[0]["content"].append(part)

        response = client.chat.completions.create(
            # model="gpt-4-vision-preview",
            model="gpt-4-turbo",
            messages=request,
            max_tokens=800,
            stream=False,
        )

        result["response"] = json.loads(response.choices[0].message.content)

    return result


# def describe(
#     client: OpenAI,
#     path: Path,
#     content_type: str,
#     *,
#     prompt: str = DESCRIBE_DOCUMENT,
# ) -> dict:
#     if not content_type.startswith("image"):
#         message = f"Only image/* content is supported, got {content_type}"
#         raise ValueError(message)

#     data = b64encode(path.read_bytes()).decode("utf-8")

#     response = client.chat.completions.create(
#         # model="gpt-4-vision-preview",
#         model="gpt-4-turbo",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": "\n".join([prompt, RESTRICTION]),
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:{content_type};base64,{data}",
#                         },
#                     },
#                 ],
#             }
#         ],
#         max_tokens=800,
#         stream=False,
#     )

#     return json.loads(response.choices[0].message.content)


# def analyze(
#     client: OpenAI,
#     description: dict[str, str],
#     prompt: str = ANALYZE_PRODUCT,
# ) -> dict:
#     if description["type"] != "PRODUCT":
#         message = "Can analyze only product images, not {}".format(description["type"])
#         raise ValueError(message)

#     response = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": "\n".join([prompt, RESTRICTION]),
#                     },
#                     {
#                         "type": "text",
#                         "text": description["text"],
#                     },
#                 ],
#             }
#         ],
#         max_tokens=800,
#         stream=False,
#     )

#     return json.loads(response.choices[0].message.content)

logger = logging.getLogger(__name__)
