from fastapi import FastAPI


def dummy(application: FastAPI, path: str) -> FastAPI:
    import gradio as gr

    from .dummy import blocks

    integration = gr.mount_gradio_app(
        application,
        blocks,
        path,
    )

    return integration
