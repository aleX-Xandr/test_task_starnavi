import os

from alembic.config import Config
from alembic.script import Script
from dependency_injector.wiring import inject, Provide
from pathlib import Path
from typing import List, Union, Optional

from app.configs import DbConfig
from app.containers import container, Container


@inject
def get_alembic_config(
    db_config: DbConfig = Provide[Container.config.provided.db],
) -> Config:
    """
    Returns migrations `Config` object which can be used e.g. in `click` commands.
    """
    config_file_location = Path(__file__).resolve().parent.parent
    config_file = os.path.join(config_file_location, "alembic.ini")
    alembic_config = Config(config_file)
    alembic_config.set_main_option("sqlalchemy.url", db_config.master_sync)
    alembic_config.set_main_option(
        "script_location", 
        os.path.dirname(os.path.realpath(__file__))
    )
    return alembic_config


def update_last_revision(
    scripts: Union[Optional[Script], List[Optional[Script]]]
) -> None:
    """
    Saves the latest revision(s) to file 'last_revision'. It allows to get GIT conflict in case of migrations conflict.
    :param scripts: new migrations scripts to save their revisions
    """
    alembic_config = get_alembic_config()
    file_location = alembic_config.get_main_option("script_location") or "app/migrations"
    last_revision_file = os.path.join(file_location, "last_revision")

    if not isinstance(scripts, (list, tuple)):
        scripts = [scripts]

    with open(last_revision_file, "w") as last_revision_file_h:
        last_revision_file_h.writelines(
            [script.revision for script in scripts if script]
        )


container.wire(modules=[__name__])
