import re, aiohttp, json, asyncio, pycurl
from aiocache import cached
from interactions import (
    CommandType,
    AutoShardedClient,
    AllowedMentions,
    Button,
    ButtonStyle,
    ContextMenuContext,
    Message,
    Permissions,
    context_menu,
    listen,
    Extension,
    cooldown,
    Buckets,
)
from interactions.api.events import MessageCreate
from utils.topgg import topgg_vote_embed


class FixSocials(Extension):
    bot: AutoShardedClient

    @context_menu(name="Fix Social Embed", context_type=CommandType.MESSAGE)
    @cooldown(Buckets.USER, 1, 3)
    async def quickvids_ctxmenu(self, ctx: ContextMenuContext):
        message: Message = ctx.target
        (
            tiktok_urls,
            instagram_urls,
            twitter_urls,
            reddit_urls,
        ) = await self.extract_urls(message.content.replace("https://www.", "https://"))
        components = Button(
            style=ButtonStyle.URL,
            label="Jump to Original Message",
            url=message.jump_url,
        )

        if (
            not tiktok_urls
            and not instagram_urls
            and not twitter_urls
            and not reddit_urls
        ):
            await ctx.respond(
                "No fixable links found. Use this command on TikTok, Instagram, Twitter, and Reddit links.",
                ephemeral=True,
                components=components,
            )
            return

        if len(message.content) > 400:
            return await ctx.respond(
                "Message is too long.", ephemeral=True, components=components
            )

        await self.process_urls(
            ctx, tiktok_urls, instagram_urls, twitter_urls, reddit_urls, components
        )

    @listen()
    async def on_message_create(self, event: MessageCreate):
        if (
            event.message.author.id == self.bot.user.id
            or len(event.message.content) > 400
        ):
            return

        (
            tiktok_urls,
            instagram_urls,
            twitter_urls,
            reddit_urls,
        ) = await self.extract_urls(
            event.message.content.replace("https://www.", "https://")
        )
        await self.process_urls(
            event.message, tiktok_urls, instagram_urls, twitter_urls, reddit_urls
        )

    async def process_urls(
        self,
        message,
        tiktok_urls,
        instagram_urls,
        twitter_urls,
        reddit_urls,
        components=None,
    ):
        vote_button, embed = await topgg_vote_embed()
        for url in tiktok_urls:
            quickvids_url = await self.quickvids(
                url[0].replace("https://vxtiktok.com/", "https://tiktok.com/")
            )
            if quickvids_url and not await self.is_carousel(quickvids_url):
                if isinstance(message, ContextMenuContext):
                    await message.respond(
                        quickvids_url,
                        components=components,
                        allowed_mentions=AllowedMentions.none(),
                    )
                else:
                    await message.reply(
                        quickvids_url, allowed_mentions=AllowedMentions.none()
                    )
                    await asyncio.sleep(0.1)
                    await message.suppress_embeds() if (
                        await message.guild.fetch_member(self.bot.user.id)
                    ).has_permission(Permissions.MANAGE_MESSAGES) else None
                    if vote_button and embed:
                        await message.channel.send(
                            components=vote_button, embed=embed, delete_after=20
                        )
            else:
                url_list = list(url)
                url_list[0] = await self.get_final_url(url_list[0])
                url_list[0] = url_list[0].replace(
                    "https://www.tiktok.com/", "https://tiktok.com/"
                )
                url = tuple(url_list)
                if not url[0].startswith("https://vxtiktok.com/") and not url[
                    0
                ].startswith("https://vxtiktok.com/"):
                    if isinstance(message, ContextMenuContext):
                        await message.respond(
                            url[0].replace(
                                "https://tiktok.com/", "https://vxtiktok.com/"
                            ),
                            components=components,
                            allowed_mentions=AllowedMentions.none(),
                        )
                    else:
                        await message.reply(
                            url[0].replace(
                                "https://tiktok.com/", "https://vxtiktok.com/"
                            ),
                            allowed_mentions=AllowedMentions.none(),
                        )
                        await asyncio.sleep(0.1)
                        await message.suppress_embeds() if (
                            await message.guild.fetch_member(self.bot.user.id)
                        ).has_permission(Permissions.MANAGE_MESSAGES) else None
                        if vote_button and embed:
                            await message.channel.send(
                                components=vote_button, embed=embed, delete_after=20
                            )

        for url in instagram_urls:
            if isinstance(message, ContextMenuContext):
                await message.respond(
                    url[0].replace(
                        "https://instagram.com/", "https://ddinstagram.com/"
                    ),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
            else:
                await message.reply(
                    url[0].replace(
                        "https://instagram.com/", "https://ddinstagram.com/"
                    ),
                    allowed_mentions=AllowedMentions.none(),
                )
                await asyncio.sleep(0.1)
                await message.suppress_embeds() if (
                    await message.guild.fetch_member(self.bot.user.id)
                ).has_permission(Permissions.MANAGE_MESSAGES) else None
                if vote_button and embed:
                    await message.channel.send(
                        components=vote_button, embed=embed, delete_after=20
                    )

        for url in reddit_urls:
            if isinstance(message, ContextMenuContext):
                await message.respond(
                    url[0]
                    .replace("reddit.com/", "rxddit.com/")
                    .replace("redd.it/", "rxddit.com/"),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
            else:
                await message.reply(
                    url[0]
                    .replace("reddit.com/", "rxddit.com/")
                    .replace("redd.it/", "rxddit.com/"),
                    allowed_mentions=AllowedMentions.none(),
                )
                await asyncio.sleep(0.1)
                await message.suppress_embeds() if (
                    await message.guild.fetch_member(self.bot.user.id)
                ).has_permission(Permissions.MANAGE_MESSAGES) else None
                if vote_button and embed:
                    await message.channel.send(
                        components=vote_button, embed=embed, delete_after=20
                    )

        for url in twitter_urls:
            if isinstance(message, ContextMenuContext):
                await message.respond(
                    url[0].replace("https://twitter.com/", "https://vxtwitter.com/"),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
            else:
                await message.reply(
                    url[0].replace("https://twitter.com/", "https://vxtwitter.com/"),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
                await asyncio.sleep(0.1)
                await message.suppress_embeds() if (
                    await message.guild.fetch_member(self.bot.user.id)
                ).has_permission(Permissions.MANAGE_MESSAGES) else None
                if vote_button and embed:
                    await message.channel.send(
                        components=vote_button, embed=embed, delete_after=20
                    )

    @cached(ttl=86400)
    async def get_final_url(self, url):
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(pycurl.WRITEFUNCTION, lambda bytes: len(bytes))
        c.perform()
        redirect = c.getinfo(c.EFFECTIVE_URL)
        c.close()
        return redirect.partition("?")[0]

    @cached(ttl=86400)
    async def extract_urls(self, text):
        tiktok_regex = r"(https:\/\/(www\.)?(vt|vm)\.tiktok\.com\/[A-Za-z0-9]+|https:\/\/(vx)?tiktok\.com\/@[\w.]+\/video\/[\d]+\/?|https:\/\/(vx)?tiktok\.com\/t\/[a-zA-Z0-9]+\/?)"
        instagram_regex = r"(https:\/\/(www.)?instagram\.com\/(?:p|reel)\/([^/?#&]+))"
        twitter_regex = (
            r"(https:\/\/(www.)?(twitter|x)\.com\/[a-zA-Z0-9_]+\/status\/[0-9]+)"
        )
        reddit_regex = r"(https?://(?:www\.)?(?:old\.)?reddit\.com/r/[A-Za-z0-9_]+/(?:comments|s)/[A-Za-z0-9_]+(?:/[^/ ]+)?(?:/\w+)?)|(https?://(?:www\.)?redd\.it/[A-Za-z0-9]+)"

        tiktok_urls = re.findall(tiktok_regex, text)
        instagram_urls = re.findall(instagram_regex, text)
        twitter_urls = re.findall(
            twitter_regex, text.replace("https://x.com/", "https://twitter.com/")
        )
        reddit_urls = re.findall(reddit_regex, text)

        return tiktok_urls, instagram_urls, twitter_urls, reddit_urls

    @cached(ttl=86400)
    async def quickvids(self, tiktok_url):
        try:
            headers = {
                "content-type": "application/json",
                "user-agent": "Keto - stkc.win",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                url = "https://api.quickvids.win/v1/shorturl/create"
                data = {"input_text": tiktok_url}
                async with session.post(
                    url, json=data, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        data = json.loads(text)
                        quickvids_url = data["quickvids_url"]
                        return quickvids_url
                    else:
                        return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    @cached(ttl=86400)
    async def is_carousel(self, link: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        return ">Download All Images</button>" in text
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""

    FixSocials(bot)
