import mimetypes
import contextlib

from pathlib import Path

import httpx
import gradio as gr
import pandas as pd


CUSTOMER: str = "00000000-0000-0000-0000-000000000000"


# Sample data for demonstration
data = {
    "Name": ["John Doe", "Jane Smith"],
    "Contact": ["1234567890", "0987654321"],
    "Claim Type": ["RETURN", "REFUND"],
    "Quantity": [1, 2],
    "UOM": ["Piece", "Box"],
    "Amount": [100, 200],
    "Description": ["Damaged item", "Wrong item"],
    "Document": ["document1.pdf", "document2.pdf"],
    "Photo": ["photo1.png", "photo2.png"],
}

df = pd.DataFrame(data)


def show_table():
    return df


# def plot_statistics():
#     plt.figure(figsize=(10, 5))
#     df["Claim Type"].value_counts().plot(kind="bar")
#     plt.title("Number of Claims by Type")
#     plt.xlabel("Claim Type")
#     plt.ylabel("Number of Claims")
#     return plt.gcf()


# # Functions for creating plots
# def create_plot1():
#     fig, ax = plt.subplots(figsize=(4, 2))
#     ax.barh(["CLOSED", "IN_PROGRESS", "OPEN"], [30, 50, 20], color=["green", "blue", "orange"])
#     ax.set_title("QUANTITY by STATUS")
#     return fig


# def create_plot2():
#     fig, ax = plt.subplots(figsize=(4, 2))
#     ax.barh(["CLOSED", "IN_PROGRESS", "OPEN"], [60000, 40000, 20000], color=["green", "blue", "orange"])
#     ax.set_title("CLAIM_AMOUNT by STATUS")
#     return fig


# def create_plot3():
#     fig, ax = plt.subplots(figsize=(4, 2))
#     ax.plot(["2022-06-01", "2022-07-01", "2022-08-01"], [100, 200, 150], marker="o")
#     ax.set_title("SPEED of CLAIM CLOSURE")
#     return fig


# Creating table for display
def create_table():
    data = {"Description": ["Avr speed - 1.7 days", "Avr amount - 321 $", "Avr quantity - 15"]}
    df = pd.DataFrame(data)
    return df


def upload(api: str, claim: str, *paths: Path) -> dict:
    files: list[tuple[str, tuple[str, bytes, str]]] = []

    with contextlib.ExitStack() as stack:
        for path in paths:
            content_type = mimetypes.guess_type(path)[0]

            if not content_type:
                message = "Invalid document type"
                raise ValueError(message)

            buffer = stack.enter_context(path.open("rb"))

            files.append(("documents", (path.name, buffer, content_type)))

        response = httpx.post(f"{api}/documents/{claim}", files=files)
        response.raise_for_status()
        result = response.json()
    return result


def create_claim(
    baseurl,
    # name,
    # contact,
    claim_type,
    quantity,
    uom,
    amount,
    description,
    document: str,
    photo: str,
) -> str:
    baseurl = baseurl.rstrip("/")

    # create claim

    data = {
        # TODO: get real customer identifier
        "customer": CUSTOMER,
        "type": claim_type,
        "description": description or "",
        "quantity": quantity,
        "unit": uom,
        "amount": amount,
    }

    response = httpx.post(f"{baseurl}/claims", json=data, timeout=60.0)
    response.raise_for_status()

    claim = response.json()

    # upload document

    if document:
        document = Path(document)
        documents = upload(baseurl, claim["ID"], document)

        claim["document"] = documents[document.name]["ID"]

    # upload photos
    photos = [Path(photo)]
    claim["documents"] = []

    if photos:
        photos = upload(baseurl, claim["ID"], *photos)
        claim["documents"] = [photo["ID"] for photo in photos.values()]

    claim["status"] = "OPEN"

    # update claim to include uploaded documents
    response = httpx.patch(f"{baseurl}/claims/{{}}".format(claim["ID"]), json=claim)
    response.raise_for_status()

    claim = response.json()

    return str(claim)

    # # upload attached documents
    # result = upload(baseurl.rstrip("/"), Path(document))

    # update clain

    return str(result)

    # You can add logic to handle the inputs here
    return "\n".join([str(type(photo)), str(photo), str(dir(photo)), str(isinstance(photo, Path))])
    return f"Claim created for {name} with contact {contact} for a {claim_type} claim."


with gr.Blocks() as blocks:
    with gr.Tab("# Claims"):

        baseurl = gr.Text(visible=False)

        def geturl(request: gr.Request) -> str:
            return request.request.base_url

        blocks.load(geturl, None, baseurl)

        # with gr.Row():
        #     name = gr.Textbox(label="Name", placeholder="Name")
        #     contact = gr.Textbox(label="Contact", placeholder="Contact")

        # with gr.Row():
        #     claim_type = gr.Dropdown(label="Claim type", choices=["RETURN", "REFUND", "EXCHANGE"], value="RETURN")

        with gr.Row():
            claim_type = gr.Dropdown(label="Claim type", choices=["RETURN", "REFUND", "EXCHANGE"], value="RETURN")
            quantity = gr.Number(label="Quantity", value=1)
            uom = gr.Dropdown(label="UOM", choices=["Piece", "Box", "Kilogram", "Litre"], value="Piece")
            amount = gr.Number(label="Amount", value=1)

        description = gr.Textbox(label="Claim Description", placeholder="Description", lines=3)

        with gr.Row():
            document = gr.File(label="Upload document", file_types=[".pdf", ".docx"])
            # photo = gr.Image(label="Upload photo")
            photo = gr.File(label="Upload photo", file_types=[".png", ".jpg", ".jpeg"])

        submit_button = gr.Button("Create claim")

        result = gr.Textbox(label="Result")

        submit_button.click(
            create_claim,
            [
                baseurl,
                # name,
                # contact,
                claim_type,
                quantity,
                uom,
                amount,
                description,
                document,
                photo,
            ],
            result,
        )

    # with gr.Tab("View & Edit Claims"):
    #     gr.Markdown("## Claims Processing Dashboard")
    #     with gr.Row():
    #         # with gr.Column():
    #         #     plot1 = gr.Plot(create_plot1())
    #         # with gr.Column():
    #         #     plot2 = gr.Plot(create_plot2())
    #         with gr.Column():
    #             table = gr.DataFrame(value=create_table(), interactive=False, label="Speed of Claim Table")
    #         # with gr.Column():
    #         #     plot3 = gr.Plot(create_plot3())

    #     with gr.Row():
    #         with gr.Column(scale=2):
    #             gr.Markdown("## Details of the CLAIM ID")
    #             with gr.Row():
    #                 gr.Markdown("CLAIM_ID:")
    #                 quantity = gr.Dropdown(choices=list(range(2, 21)), value=4, label=None)
    #             with gr.Row():
    #                 gr.Markdown("CUSTOMER_ID:")
    #                 animal = gr.Dropdown(["cat", "dog", "bird"], label=None)
    #             with gr.Row():
    #                 gr.Markdown("CLAIM_DATE:")
    #                 countries = gr.Dropdown(["USA", "Japan", "Pakistan"], multiselect=True, label=None)
    #             with gr.Row():
    #                 gr.Markdown("CLAIM_TYPE:")
    #                 place = gr.Dropdown(["park", "zoo", "road"], label=None)
    #             with gr.Row():
    #                 gr.Markdown("CLAIM_DESCRIPTION:")
    #                 activity_list = gr.Dropdown(
    #                     ["ran", "swam", "ate", "slept"], value=["swam", "slept"], multiselect=True, label=None
    #                 )
    #             with gr.Row():
    #                 gr.Markdown("DOC_NUM:")
    #                 morning = gr.Dropdown([True, False], label=None)

    #             output = gr.Textbox(label="Generated Sentence")

    #             with gr.Row():
    #                 generate_button1 = gr.Button("Cancel")
    #                 generate_button2 = gr.Button("Edit")
    #                 generate_button3 = gr.Button("Approve")

    #             generate_button1.click(
    #                 create_claim,
    #                 inputs=[quantity, animal, countries, place, activity_list, morning],
    #                 outputs=output,
    #             )
    #             generate_button2.click(
    #                 create_claim,
    #                 inputs=[quantity, animal, countries, place, activity_list, morning],
    #                 outputs=output,
    #             )
    #             generate_button3.click(
    #                 create_claim,
    #                 inputs=[quantity, animal, countries, place, activity_list, morning],
    #                 outputs=output,
    #             )

    #         with gr.Column(scale=8):
    #             gr.Markdown("## Claims List")
    #             examples_table = gr.Examples(
    #                 examples=[
    #                     [
    #                         "John Doe",
    #                         "1234567890",
    #                         "RETURN",
    #                         1,
    #                         "Piece",
    #                         100,
    #                         "Damaged item",
    #                         # "document1.pdf",
    #                         # "photo1.png",
    #                     ],
    #                     [
    #                         "Jane Smith",
    #                         "0987654321",
    #                         "REFUND",
    #                         2,
    #                         "Box",
    #                         200,
    #                         "Wrong item",
    #                         # "document2.pdf",
    #                         # "photo2.png",
    #                     ],
    #                 ],
    #                 inputs=[name, contact, claim_type, quantity, uom, amount, description],
    #                 outputs=output,
    #                 examples_per_page=30,  # Display 30 examples per page
    #             )
