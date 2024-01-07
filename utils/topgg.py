import aiohttp, os, random
from interactions import Task, IntervalTrigger
from interactions import Button, ButtonStyle, Embed


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


async def topgg_vote_embed():
    vote_url = os.getenv("TOPGG_VOTE_URL")
    bot_name = os.getenv("PROJECT_NAME")
    number = random.random()

    if not vote_url:
        components, embed = None, None
        return components, embed
    if number >= 0.20:
        components, embed = None, None
        return components, embed

    components = [
        Button(
            style=ButtonStyle.URL,
            label="Vote on Top.gg",
            url=vote_url,
            emoji="⬆️",
        ),
        Button(
            style=ButtonStyle.URL,
            label="Star on GitHub",
            url="https://github.com/stekc/Keto-Bot",
            emoji="⭐",
        ),
        Button(
            style=ButtonStyle.URL,
            label="Join Support Server",
            url="https://discord.gg/FVvaa9QZnm",
            emoji="💬",
        ),
    ]
    embed = Embed(
        description=f"*Enjoying {bot_name}? Please vote, it helps the bot grow!*",
        color=0xFF3366,
    )

    return components, embed


@Task.create(IntervalTrigger(minutes=30))
async def update_topgg_count(self):
    await topgg_refresh(self)
