import asyncio

from alembic import command

from app.migrations.utils import get_alembic_config


class MigrationRunner:
    def __init__(self, *, loop=None):
        self._loop = loop or asyncio.get_running_loop()
        self._alembic_config = get_alembic_config()

    def _upgrade(self):
        command.upgrade(self._alembic_config, "head")

    async def upgrade(self):
        self._loop.run_in_executor(None, self._upgrade)

    def _downgrade(self):
        command.downgrade(self._alembic_config, "base")

    async def downgrade(self):
        self._loop.run_in_executor(None, self._downgrade)
