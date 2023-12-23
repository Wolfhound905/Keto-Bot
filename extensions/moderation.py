import aiohttp, datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from humanize import naturaldelta
from interactions import (
    Extension,
    AutoShardedClient,
    SlashContext,
    slash_command,
    slash_option,
    OptionType,
    Permissions,
    slash_default_member_permission,
)


class Moderation(Extension):
    bot: AutoShardedClient

    @slash_command(name="mute", description="Mute a user")
    @slash_option(
        name="user",
        description="User to mute",
        required=True,
        opt_type=OptionType.USER,
    )
    @slash_option(
        name="time",
        description="Length to mute in seconds",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reason",
        description="Reason for mute",
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_default_member_permission(Permissions.MUTE_MEMBERS)
    async def mute(
        self, ctx: SlashContext, time: str, user: OptionType.USER, reason: str = None
    ):
        if ctx.author.top_role.position <= user.top_role.position:
            await ctx.send(
                "You can't mute someone above or equal to you.", ephemeral=True
            )
            return

        valid_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

        if (
            not any(time.endswith(unit) for unit in valid_units)
            or len([unit for unit in valid_units if unit in time]) > 1
        ):
            await ctx.send("Invalid time format. Example: 2h", ephemeral=True)
            return

        unit = time[-1]
        time_value = int(time[:-1])

        if unit not in valid_units:
            await ctx.send("Invalid time unit.", ephemeral=True)
            return

        duration_in_seconds = time_value * valid_units[unit]
        date = datetime.datetime.now() + datetime.timedelta(seconds=duration_in_seconds)

        if duration_in_seconds < 5:
            await ctx.send(
                "You can't mute someone for less than 5 seconds.", ephemeral=True
            )
            return

        if date > datetime.datetime.now() + datetime.timedelta(weeks=2):
            await ctx.send(
                "You can't mute someone for more than 2 weeks.", ephemeral=True
            )
            return

        await user.timeout(date, reason if reason else "No reason provided")
        duration_seconds = (date - datetime.datetime.now()).total_seconds()
        rounded_duration = round(duration_seconds)
        duration_str = naturaldelta(datetime.timedelta(seconds=rounded_duration))
        await ctx.send(f"{user.mention} has been muted for {duration_str}.")


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""

    Moderation(bot)
