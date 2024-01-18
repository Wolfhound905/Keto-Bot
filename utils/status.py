import os
from interactions import Task, IntervalTrigger, Activity, ActivityType


async def status_refresh(self):
    if os.getenv("CUSTOM_ACTIVITY") == "false":
        guild_count = len(self.bot.guilds)
        activity = Activity.create(
            name=str(guild_count) + " servers" if guild_count > 1 else "1 server",
            type=ActivityType.WATCHING,
        )

        await self.bot.change_presence(activity=activity)


@Task.create(IntervalTrigger(minutes=5))
async def status_refresh_interval(self):
    await status_refresh(self)
