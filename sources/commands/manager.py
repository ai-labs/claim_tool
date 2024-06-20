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

    with artifice.clickerize(BadParameter):
        config = server.Config(
            server=settings.Server(host=host, port=port),
            general=settings.General(),
            database=settings.database.Database(),
            integrations=settings.integrations.Integrations(),
        )

    application = server.factory(config)

    application.state.appdir = appdir
    application.state.config = config

    uvicorn.run(
        application,
        log_config=None,
        host=config.server.host,
        port=config.server.port,
    )


logger = logging.getLogger(__name__)
