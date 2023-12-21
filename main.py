import os
from utils.topgg import update_topgg_count
from dotenv import load_dotenv
from interactions import Intents, listen
from interactions.ext.debug_extension import DebugExtension
from core.init_logging import init_logging
from core.base import CustomClient
from core.extensions_loader import load_extensions


if __name__ == "__main__":
    load_dotenv()

    logger = init_logging()

    bot = CustomClient(
        intents=Intents.MESSAGES | Intents.MESSAGE_CONTENT | Intents.GUILDS,
        auto_defer=True,
        activity="https://stkc.win/",
        logger=logger,
        delete_unused_application_cmds=True,
        fetch_members=False,
        send_not_ready_messages=True,
        disable_dm_commands=True,
        debug_scope=os.getenv("MAIN_GUILD_ID")
        if os.getenv("SINGLE_SERVER") == "true"
        else False,
        send_command_tracebacks=True
        if os.getenv("SEND_TRACEBACKS") == "true"
        else False,
    )

    if os.getenv("LOAD_DEBUG_COMMANDS") == "true":
        DebugExtension(bot=bot)

    load_extensions(bot=bot)

    @listen()
    async def on_startup(self):
        update_topgg_count.start(self)

    bot.start(os.getenv("DISCORD_TOKEN"))
