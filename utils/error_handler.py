import traceback, uuid, aiohttp, json, os
from interactions import (
    listen,
    Extension,
    AutoShardedClient,
    events,
    Embed,
    Button,
    ButtonStyle,
)


class ErrorHandling(Extension):
    bot: AutoShardedClient

    @listen(disable_default_listeners=True)
    async def on_error(self, event: events.Error):
        if not os.getenv("ERROR_WEBHOOK_URL") or not os.getenv(
            "ERROR_WEBHOOK_URL"
        ).startswith("https://discord.com/api/webhooks/"):
            return traceback.print_exception(
                type(event.error), event.error, event.error.__traceback__
            )

        error_id = uuid.uuid4().hex.upper()[0:6]
        error_type = str(type(event.error).__name__)
        error_str = str(event.error.__str__())

        if error_type == "CommandOnCooldown":
            embed = Embed(description=error_str + ".", color=0xF23F42)
            return await event.ctx.send(embed=embed, delete_after=5)

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

            components = Button(
                style=ButtonStyle.URL,
                label="Join Support Server",
                url="https://discord.gg/wsxncM7skr",
            )

            await event.ctx.send(embed=embed, components=components)

        embed = {
            "title": f"{'A command errored in ' + guild_name + ' (' + str(guild_id) + ') - ' + str(user_name) + ' (' + str(user_id) + ') - ' + os.getenv('PROJECT_NAME') if event and event.ctx else 'An error occurred - ' + os.getenv('PROJECT_NAME')}",
            "description": f"```{tb_str[:4090]}```",
            "color": 16776960 if event and event.ctx else 16711680,
        }

        await self.send_error_webhook(embed, event, error_id, length=len(tb_str))

    async def send_error_webhook(self, embed, event=None, code=None, length=0):
        if length > 4090:
            return traceback.print_exception(
                type(event.error), event.error, event.error.__traceback__
            )

        payload = {"content": f"`{code}`" if code else None, "embeds": [embed]}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                os.getenv("ERROR_WEBHOOK_URL"),
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ) as resp:
                if not resp.status in [200, 204]:
                    traceback.print_exception(
                        type(event.error), event.error, event.error.__traceback__
                    )


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""
    ErrorHandling(bot)
