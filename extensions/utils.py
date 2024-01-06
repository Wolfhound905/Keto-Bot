import os, aiohttp, psutil, platform, uuid
from dotenv import load_dotenv
from aiocache import cached
from interactions import (
    Extension,
    Embed,
    AutoShardedClient,
    SlashContext,
    __version__,
    slash_command,
    slash_option,
    OptionType,
    cooldown,
    Buckets,
)
from utils.colorthief import get_color
from utils.topgg import topgg_refresh


class Utilities(Extension):
    bot: AutoShardedClient
    load_dotenv()

    @cached(ttl=86400)
    async def get_currency_conversion(
        self, base_currency: str, target_currency: str, api_key: str
    ) -> dict:
        async with aiohttp.ClientSession() as session:
            params = {
                "apikey": api_key,
                "base_currency": base_currency.upper(),
                "currencies": target_currency.upper(),
            }

            async with session.get(
                "https://api.freecurrencyapi.com/v1/latest", params=params
            ) as response:
                if not response.status == 200:
                    return None
                data = await response.json()
                return data

    @slash_command(name="currency", description="Convert currencies")
    @slash_option(
        name="amount",
        description="Amount of money to convert",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="from_currency",
        description="Base currency",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="to_currency",
        description="Currency to convert to",
        required=True,
        opt_type=OptionType.STRING,
    )
    @cooldown(Buckets.USER, 2, 30)
    async def currency(
        self, ctx: SlashContext, amount: str, from_currency: str, to_currency: str
    ):
        api_key = os.getenv("FREECURRENCYAPI_KEY")
        if not api_key:
            return await ctx.respond(
                "This command is unavailable because no API key is set.\nAn API key can be obtained from https://freecurrencyapi.com.",
                ephemeral=True,
            )

        currency_codes = [
            "EUR",
            "USD",
            "JPY",
            "BGN",
            "CZK",
            "DKK",
            "GBP",
            "HUF",
            "PLN",
            "RON",
            "SEK",
            "CHF",
            "ISK",
            "NOK",
            "HRK",
            "RUB",
            "TRY",
            "AUD",
            "BRL",
            "CAD",
            "CNY",
            "HKD",
            "IDR",
            "ILS",
            "INR",
            "KRW",
            "MXN",
            "MYR",
            "NZD",
            "PHP",
            "SGD",
            "THB",
            "ZAR",
        ]
        currency_symbols = "$¢€£¥₹฿₽₩₺₴₦₲₡₱₮₭₪₸₫₵₢₯₠₣₧₤₥₰₶₺₾"

        amount = amount.strip(currency_symbols)
        from_currency = from_currency.strip(currency_symbols)
        to_currency = to_currency.strip(currency_symbols)

        if not amount.isnumeric:
            return await ctx.respond("Amount must be a number.", ephemeral=True)

        if from_currency.upper() not in currency_codes:
            return await ctx.respond(
                f"Invalid base currency `{from_currency}`.", ephemeral=True
            )

        if to_currency.upper() not in currency_codes:
            return await ctx.respond(
                f"Invalid currency to convert to (`{to_currency}`).", ephemeral=True
            )

        data = await self.get_currency_conversion(from_currency, to_currency, api_key)
        if data is None:
            return await ctx.respond(
                "An error occurred while fetching the data.", ephemeral=True
            )

        result = (
            "{:,.2f}".format(
                round(data["data"].get(to_currency.upper()), 2) * float(amount)
            )
            + " "
            + to_currency.upper()
        )
        amount = "{:,.2f}".format(round(float(amount), 2)) + " " + from_currency.upper()
        embed = Embed(
            description=f"**{amount}** is equal to **{result}**.", color=0x23A55A
        )
        await ctx.respond(embed=embed)

    @slash_command(name="stats", description="View bot statistics")
    @cooldown(Buckets.GUILD, 1, 10)
    async def stats(self, ctx: SlashContext):
        ram = f"{psutil.virtual_memory().used >> 20} MB / {psutil.virtual_memory().total >> 20} MB"
        cpu = f"{psutil.cpu_percent(interval=1)}%"
        randstr = uuid.uuid4().hex.upper()[0:16]
        embed = Embed(title="Bot Stats")
        embed.color = await get_color(self.bot.user.avatar_url)
        embed.set_image(
            url=f"https://opengraph.githubassets.com/{randstr}/stekc/Keto-Bot"
        )
        embed.add_field(
            name="Guilds (Shards)",
            value=str(len(self.bot.guilds))
            + " ("
            + str(len(set(state.shard_id for state in self.bot.shards)))
            + ")",
            inline=False,
        )
        embed.add_field(name="OS", value=platform.system(), inline=True)
        embed.add_field(name="CPU", value=cpu, inline=True)
        embed.add_field(name="RAM", value=ram, inline=True)
        embed.add_field(
            name="Python Version", value=platform.python_version(), inline=False
        )
        embed.add_field(name="interactions.py Version", value=__version__, inline=False)
        embed.set_footer(
            text="https://github.com/stekc/keto-bot", icon_url=self.bot.owner.avatar_url
        )
        await ctx.respond(embed=embed)


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""

    Utilities(bot)
