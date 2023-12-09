import re, aiohttp, json, asyncio
from aiocache import cached
from core.base import CustomClient
from interactions import (
    CommandType,
    AllowedMentions,
    Button,
    ButtonStyle,
    ContextMenuContext,
    Message,
    context_menu,
    listen,
    Extension,
    cooldown,
    Buckets,
)
from interactions.api.events import MessageCreate


class FixSocials(Extension):
    bot: CustomClient

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
                "No fixable links found. Use this command on TikTok, Instagram Reels, Twitter, and Reddit links.",
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
        if event.message.author.bot or len(event.message.content) > 400:
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
                    await message.suppress_embeds()
            else:
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
                        await message.suppress_embeds()

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
                await message.suppress_embeds()

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
                await message.suppress_embeds()

        for url in twitter_urls:
            await asyncio.sleep(1)

            if isinstance(message, ContextMenuContext):
                await message.respond(
                    url[0].replace("https://twitter.com/", "https://vxtwitter.com/"),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
                await asyncio.sleep(0.1)
            else:
                if message.embeds:
                    embed = message.embeds[0]
                    embed_dict = embed.to_dict()
                    if embed_dict.get("image") or (
                        embed_dict.get("thumbnail")
                        and "video_thumb" in embed_dict["thumbnail"].get("url", "")
                    ):
                        await message.reply(
                            url[0].replace(
                                "https://twitter.com/", "https://vxtwitter.com/"
                            ),
                            components=components,
                            allowed_mentions=AllowedMentions.none(),
                        )
                        await asyncio.sleep(0.1)
                        await message.suppress_embeds()
                else:
                    await message.reply(
                        url[0].replace(
                            "https://twitter.com/", "https://vxtwitter.com/"
                        ),
                        components=components,
                        allowed_mentions=AllowedMentions.none(),
                    )
                    await asyncio.sleep(0.1)
                    await message.suppress_embeds()

    @cached(ttl=604800)
    async def extract_urls(self, text):
        tiktok_regex = r"(https:\/\/(www.)?((vm|vt).tikt(o|x)k.com\/[A-Za-z0-9]+|(vx)?tikt(o|x)k.com\/@[\w.]+\/video\/[\d]+\/?|(vx)?tikt(o|x)k.com\/t\/[a-zA-Z0-9]+))"
        instagram_regex = r"(https:\/\/(www.)?instagram\.com\/(?:p|reel)\/([^/?#&]+))"
        twitter_regex = (
            r"(https:\/\/(www.)?(twitter|x)\.com\/[a-zA-Z0-9_]+\/status\/[0-9]+)"
        )
        reddit_regex = r"(https?://(?:www\.)?(?:old\.)?reddit\.com/r/[A-Za-z0-9_]+/comments/[A-Za-z0-9]+)|(https?://(?:www\.)?redd\.it/[A-Za-z0-9]+)"

        tiktok_urls = re.findall(
            tiktok_regex,
            text.replace("https://vm.tiktok.com/", "https://tiktok.com/").replace(
                "https://vt.tiktok.com/", "https://tiktok.com/"
            ),
        )
        instagram_urls = re.findall(instagram_regex, text)
        twitter_urls = re.findall(
            twitter_regex, text.replace("https://x.com/", "https://twitter.com/")
        )
        reddit_urls = re.findall(reddit_regex, text)

        return tiktok_urls, instagram_urls, twitter_urls, reddit_urls

    @cached(ttl=604800)
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

    @cached(ttl=604800)
    async def is_carousel(self, link: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        return ">Download All Images</button>" in text
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    FixSocials(bot)
