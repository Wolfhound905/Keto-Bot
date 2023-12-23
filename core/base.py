import os
from interactions import Client, listen


class AutoShardedClient(Client):
    """Subclass of interactions.Client with on_startup event"""

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        self.logger.info(f"Logged in as {os.getenv('PROJECT_NAME')}!")
