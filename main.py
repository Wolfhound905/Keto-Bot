import os
from utils.topgg import update_topgg_count
from utils.status import status_refresh_interval
from dotenv import load_dotenv
from interactions import (
    Intents,
    AutoShardedClient,
    listen,
    Activity,
    ActivityType,
    Status,
)
from interactions.ext.debug_extension import DebugExtension
from core.init_logging import init_logging
from core.extensions_loader import load_extensions


if __name__ == "__main__":
    load_dotenv()

    logger = init_logging()

    activity = Activity.create(
        name="Keto is starting...",
        type=ActivityType.WATCHING,
    )

    bot = AutoShardedClient(
        intents=Intents.MESSAGES | Intents.MESSAGE_CONTENT | Intents.GUILDS,
        auto_defer=True,
        activity=activity,
        logger=logger,
        delete_unused_application_cmds=True,
        fetch_members=False,
        send_not_ready_messages=True,
        disable_dm_commands=True,
        debug_scope=os.getenv("MAIN_GUILD_ID")
        if os.getenv("SINGLE_SERVER") == "true"
        else False,
        send_command_tracebacks=False,
    )

    if os.getenv("LOAD_DEBUG_COMMANDS") == "true":
        DebugExtension(bot=bot)

    load_extensions(bot=bot)

    @listen()
    async def on_startup(self):
        update_topgg_count.start(self)
        status_refresh_interval.start(self)
        if os.getenv("CUSTOM_ACTIVITY") == "false":
            guild_count = len(self.bot.guilds)
            activity = Activity.create(
                name=str(guild_count) + " servers" if guild_count > 1 else "1 server",
                type=ActivityType.WATCHING,
            )
            await self.bot.change_presence(
                activity=activity,
                status=Status.IDLE
                if os.getenv("STATUS") == "idle"
                else Status.DND
                if os.getenv("STATUS") == "dnd"
                else Status.INVISIBLE
                if os.getenv("STATUS") == "invisible"
                else Status.OFFLINE
                if os.getenv("STATUS") == "offline"
                else Status.ONLINE,
            )
        else:
            activity = Activity.create(
                name=os.getenv("ACTIVITY_MESSAGE"),
                type=ActivityType[os.getenv("ACTIVITY_TYPE").upper()],
            )
            await self.bot.change_presence(
                activity=activity,
                status=Status.IDLE
                if os.getenv("STATUS") == "idle"
                else Status.DND
                if os.getenv("STATUS") == "dnd"
                else Status.INVISIBLE
                if os.getenv("STATUS") == "invisible"
                else Status.OFFLINE
                if os.getenv("STATUS") == "offline"
                else Status.ONLINE,
            )

    bot.start(os.getenv("DISCORD_TOKEN"))
