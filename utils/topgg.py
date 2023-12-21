import aiohttp, os
from interactions import Task, IntervalTrigger


async def topgg_refresh(self):
    if os.getenv("TOPGG_TOKEN"):
        url = "https://botblock.org/api/count"
        data = {
            "server_count": len(self.bot.guilds),
            "bot_id": f"{self.bot.user.id}",
            "top.gg": os.getenv("TOPGG_TOKEN"),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                data = await response.json()
                return data


@Task.create(IntervalTrigger(minutes=30))
async def update_topgg_count(self):
    await topgg_refresh(self)
