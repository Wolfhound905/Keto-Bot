import os
from core.base import CustomClient
from interactions import (
    listen,
    Extension,
    Embed,
    SlashContext,
    slash_command,
    Permissions,
    slash_default_member_permission,
)
from interactions.api.events import MessageCreate
from utils.colorthief import get_color


class Snipe(Extension):
    bot: CustomClient
    deleted_msgs = {}

    @listen()
    async def on_message_delete(self, event):
        message = event.message
        if not message or not message.guild:
            return
        try:
            if not message.content and message.attachments:
                return
        except AttributeError:
            return

        self.deleted_msgs.update({str(message.channel.id) + "message": message.content})
        self.deleted_msgs.update(
            {str(message.channel.id) + "member": message.author.id}
        )
        if message.embeds:
            self.deleted_msgs.update(
                {str(message.channel.id) + "embed": message.embeds[0].to_dict()}
            )
        else:
            self.deleted_msgs.update({str(message.channel.id) + "embed": None})

    @slash_command(
        name="snipe", description="View the last deleted message in a channel"
    )
    @slash_default_member_permission(Permissions.MANAGE_MESSAGES)
    async def snipe(self, ctx: SlashContext):
        channel = ctx.channel

        if not str(channel.id) + "message" in self.deleted_msgs:
            await ctx.respond(
                f"I couldn't find any deleted messages in this channel.", ephemeral=True
            )
            return

        member = await self.bot.fetch_user(
            self.deleted_msgs[str(channel.id) + "member"]
        )
        message = self.deleted_msgs[str(channel.id) + "message"]
        old_embed = self.deleted_msgs[str(channel.id) + "embed"]

        if old_embed:
            author_text = f"Embed from {member} deleted in #{channel.name}"
            icon_url = member.avatar_url
            color = await get_color(member.avatar_url)

            if message:
                author_text = (
                    f"Message and embed from {member} deleted in #{channel.name}"
                )
                description = f"```diff\n- {message}```"
            else:
                description = None

            embed = Embed(
                author={"name": author_text, "icon_url": icon_url},
                color=color,
                description=description,
                footer=str(member.id),
            )

            await ctx.respond(embeds=[embed, old_embed])
        else:
            author_text = f"Message from {member} deleted in #{channel.name}"
            icon_url = member.avatar_url
            color = await get_color(member.avatar_url)

            if message:
                description = f"```diff\n- {message}```"
            else:
                description = None

            embed = Embed(
                author={"name": author_text, "icon_url": icon_url},
                color=color,
                description=description,
                footer=str(member.id),
            )

            await ctx.respond(embed=embed)


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    Snipe(bot)
