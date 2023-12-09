from core.base import CustomClient
from interactions import (
    Button,
    ButtonStyle,
    OptionType,
    Extension,
    ComponentContext,
    Embed,
    SlashContext,
    slash_command,
    component_callback,
    slash_option,
    cooldown,
    Buckets,
)
from utils.colorthief import get_color


class Users(Extension):
    bot: CustomClient
    avatar_button = Button(
        style=ButtonStyle.PRIMARY, label="View Other Avatar", custom_id="avatar_button"
    )
    guild_av_dict = {}

    @slash_command(name="userinfo", description="View a user's info")
    @slash_option(
        name="user",
        description="User to get info from",
        required=False,
        opt_type=OptionType.USER,
    )
    @cooldown(Buckets.USER, 1, 3)
    async def userinfo(self, ctx: SlashContext, user: str = None):
        if not user:
            user = ctx.author
        embed = Embed(thumbnail=user.avatar_url, footer=str(user.id))
        embed.color = await get_color(user.avatar_url)
        embed.set_author(name=str(user))
        if user.roles:
            embed.add_field(
                name="Roles", value=", ".join([f"<@&{role.id}>" for role in user.roles])
            )
        embed.add_field(
            name="Created",
            value=f"<t:{str(int(user.created_at.timestamp()))}:R>\n<t:{str(int(user.created_at.timestamp()))}:D>",
            inline=True,
        )
        embed.add_field(
            name="Joined",
            value=f"<t:{str(int(user.joined_at.timestamp()))}:R>\n<t:{str(int(user.joined_at.timestamp()))}:D>",
            inline=True,
        )
        embed.add_field(
            name="Boosting for",
            value=f"<t:{str(int(user.premium_since.timestamp()))}:R>\n<t:{str(int(user.premium_since.timestamp()))}:D>"
            if user.premium_since
            else "Not boosting",
            inline=True,
        )
        await ctx.send(embed=embed)

    @slash_command(name="avatar", description="View a user's avatar")
    @slash_option(
        name="user",
        description="User to get avatar from",
        required=False,
        opt_type=OptionType.USER,
    )
    async def avatar(self, ctx: SlashContext, user: str = None):
        if not user:
            user = ctx.author
        guild_av = user.display_avatar.url
        user_av = user.avatar_url

        embed = Embed(images=[guild_av], url=guild_av, footer=str(user.id))
        embed.color = await get_color(guild_av)
        embed.set_author(name=str(user))
        await ctx.send(
            embed=embed, components=self.avatar_button if guild_av != user_av else None
        )

    @component_callback("avatar_button")
    @cooldown(Buckets.USER, 1, 0.5)
    async def avatar_callback(self, ctx: ComponentContext):
        if not ctx.author.id == ctx.message.interaction._user_id:
            return

        user_id = ctx.message.embeds[0].footer.text
        user = await self.bot.fetch_user(user_id)
        user_av = user.avatar_url

        if user_id not in self.guild_av_dict:
            self.guild_av_dict[user_id] = ctx.message.embeds[0].url

        guild_av = self.guild_av_dict[user_id]

        if ctx.message.embeds[0].url == guild_av:
            embed = Embed(images=[user_av], url=user_av, footer=str(user.id))
            embed.color = await get_color(user_av)
            embed.set_author(name=str(user))
        else:
            embed = Embed(images=[guild_av], url=guild_av, footer=str(user.id))
            embed.color = await get_color(guild_av)
            embed.set_author(name=str(user))
        await ctx.edit_origin(embed=embed, components=self.avatar_button)


def setup(bot: CustomClient):
    Users(bot)
