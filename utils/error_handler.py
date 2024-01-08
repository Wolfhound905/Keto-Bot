import traceback, uuid, aiohttp, json, os
from interactions import listen, Extension, AutoShardedClient, events, Embed


class ErrorHandling(Extension):
    bot: AutoShardedClient

    @listen(disable_default_listeners=True)
    async def on_error(self, event: events.Error):
        error_id = uuid.uuid4().hex.upper()[0:6]
        error_type = str(type(event.error).__name__)
        error_str = str(event.error.__str__())
        tb_str = str(traceback.format_exception(event.error))
        if event.ctx:
            guild_name = event.ctx.guild.name
            guild_id = event.ctx.guild.id
            user_name = event.ctx.author
            user_mention = event.ctx.author.mention
            user_id = event.ctx.author.id

            embed = Embed(
                title=":(",
                description=f"Sorry, {user_mention}, something went wrong while running your command. `{error_id}`",
                footer=f"{error_type}: {error_str}",
                color=0xF23F42,
            )

            await event.ctx.send(embed=embed)

        embed = {
            "title": f"{guild_name + ' (' + str(guild_id) + ') ' + str(user_name) + ' (' + str(user_id) + ')' if event.ctx else 'An error occured'}",
            "description": f"```{tb_str[:4090]}```",
            "color": 16711680,
        }

        await self.send_error_webhook(embed, error_id)

    async def send_error_webhook(self, embed, code=None):
        payload = {"content": f"`{code}`" if code else None, "embeds": [embed]}

        async with aiohttp.ClientSession() as session:
            await session.post(
                os.getenv("ERROR_WEBHOOK_URL"),
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""
    ErrorHandling(bot)
