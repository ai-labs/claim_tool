import logging

from typing import Annotated

from typer import Typer, Option, Context
from click.exceptions import BadParameter

from ailabs.claims import settings
from ailabs.claims.vendor import artifice, basedirs


application = Typer(name=__name__.rsplit(".", 1)[-1])


@application.callback(invoke_without_command=True)
def callback(
    context: Context,
    host: Annotated[str, Option()] = settings.Server.model_fields["host"].default,
    port: Annotated[int, Option()] = settings.Server.model_fields["port"].default,
) -> None:
    import uvicorn

    from ailabs.claims import server

    appdir: basedirs.Directories = context.obj["appdir"]
    server.root.state.appdir = appdir

    with artifice.clickerize(BadParameter):
        config = server.root.state.config = server.Config(
            server=settings.Server(host=host, port=port),
            general=settings.General(),
        )

    uvicorn.run(
        server.root,
        log_config=None,
        host=config.server.host,
        port=config.server.port,
    )


logger = logging.getLogger(__name__)
