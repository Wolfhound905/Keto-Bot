import re, aiohttp, json, asyncio, pycurl
from aiocache import cached
from interactions import (
    CommandType,
    AutoShardedClient,
    AllowedMentions,
    Button,
    ButtonStyle,
    Embed,
    ContextMenuContext,
    ComponentContext,
    component_callback,
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
from utils.colorthief import get_color


class FixSocials(Extension):
    bot: AutoShardedClient
    tiktok_counts = {}

    @context_menu(name="Fix Social Embed", context_type=CommandType.MESSAGE)
    @cooldown(Buckets.USER, 1, 3)
    async def quickvids_ctxmenu(self, ctx: ContextMenuContext):
        message: Message = ctx.target
        (
            tiktok_urls,
            instagram_urls,
            twitter_urls,
            reddit_urls,
            youtube_urls,
        ) = await self.extract_urls(message.content.replace("https://www.", "https://"))
        jump_url = message.jump_url
        components = Button(
            style=ButtonStyle.URL,
            label="Jump to Original Message",
            url=jump_url,
        )

        if (
            not tiktok_urls
            and not instagram_urls
            and not twitter_urls
            and not reddit_urls
            and not youtube_urls
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
            ctx,
            tiktok_urls,
            instagram_urls,
            twitter_urls,
            reddit_urls,
            youtube_urls,
            jump_url,
            components,
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
            youtube_urls,
        ) = await self.extract_urls(
            event.message.content.replace("https://www.", "https://")
        )
        await self.process_urls(
            event.message,
            tiktok_urls,
            instagram_urls,
            twitter_urls,
            reddit_urls,
            youtube_urls,
        )

    @component_callback("tiktok_button")
    async def c_tiktok_button(self, ctx: ComponentContext):
        await self.description_embed(ctx)

    @component_callback("tiktok_button_2")
    async def c_tiktok_button_2(self, ctx: ComponentContext):
        await self.description_embed(ctx)

    @component_callback("tiktok_button_3")
    async def c_tiktok_button_3(self, ctx: ComponentContext):
        await self.description_embed(ctx)

    @cached(ttl=86400)
    async def description_embed(self, ctx: ComponentContext):
        message = ctx.message.content
        if not message.startswith("https://quickvids.win/"):
            message = await self.quickvids(
                ctx.message.content.replace(
                    "https://vxtiktok.com/", "https://tiktok.com/"
                )
            )
            message = message[0]
        description = self.tiktok_counts.get(message)["description"]
        author = self.tiktok_counts.get(message)["author"]
        avatar = self.tiktok_counts.get(message)["avatar"]
        embed = Embed(description=description, color=await get_color(avatar))
        embed.set_author(name="@" + author, icon_url=avatar)
        await ctx.send(embed=embed, ephemeral=True)

    async def process_urls(
        self,
        message,
        tiktok_urls,
        instagram_urls,
        twitter_urls,
        reddit_urls,
        youtube_urls,
        jump_url=None,
        components=None,
    ):
        vote_button, embed = await topgg_vote_embed()
        for url in tiktok_urls:
            (
                quickvids_url,
                likes,
                comments,
                views,
                description,
                author,
                author_avatar,
                author_link,
            ) = await self.quickvids(
                url[0].replace("https://vxtiktok.com/", "https://tiktok.com/")
            )
            self.tiktok_counts[quickvids_url] = {
                "likes": likes,
                "comments": comments,
                "views": views,
                "description": description,
                "author": author,
                "avatar": author_avatar,
            }
            buttons = [
                Button(
                    style=ButtonStyle.RED,
                    label=await self.format_number_str(likes),
                    emoji="🤍",
                    custom_id="tiktok_button",
                    disabled=False,
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label=await self.format_number_str(comments),
                    emoji="💬",
                    custom_id="tiktok_button_2",
                    disabled=False,
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label=await self.format_number_str(views),
                    emoji="👀",
                    custom_id="tiktok_button_3",
                    disabled=False,
                ),
                Button(
                    style=ButtonStyle.URL,
                    label="@" + author,
                    emoji="👤",
                    url=author_link,
                ),
            ]
            if isinstance(message, ContextMenuContext):
                buttons.append(
                    Button(
                        style=ButtonStyle.URL,
                        label="⤴️",
                        url=jump_url,
                    ),
                )
            if quickvids_url and not await self.is_carousel(quickvids_url):
                if isinstance(message, ContextMenuContext):
                    await message.respond(
                        quickvids_url,
                        components=buttons,
                        allowed_mentions=AllowedMentions.none(),
                    )
                else:
                    await message.reply(
                        quickvids_url,
                        allowed_mentions=AllowedMentions.none(),
                        components=buttons,
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
                if url[0].startswith("https://vxtiktok.com/"):
                    continue
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
                            components=buttons if quickvids_url else components,
                            allowed_mentions=AllowedMentions.none(),
                        )
                    else:
                        msg = await message.reply(
                            url[0].replace(
                                "https://tiktok.com/", "https://vxtiktok.com/"
                            ),
                            components=buttons if quickvids_url else components,
                            allowed_mentions=AllowedMentions.none(),
                        )
                        await asyncio.sleep(2)
                        if msg.embeds and msg.embeds[0].description:
                            if (
                                "Failed to get video data from TikTok"
                                in msg.embeds[0].description
                            ):
                                await msg.delete()
                                continue
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
                msg = await message.reply(
                    url[0].replace(
                        "https://instagram.com/", "https://ddinstagram.com/"
                    ),
                    allowed_mentions=AllowedMentions.none(),
                )
                await asyncio.sleep(2)
                if msg.embeds and msg.embeds[0].description:
                    if "Post not found" in msg.embeds[0].description:
                        await msg.delete()
                        continue
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
                    url[0].replace("https://twitter.com/", "https://fxtwitter.com/"),
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
                )
            else:
                await message.reply(
                    url[0].replace("https://twitter.com/", "https://fxtwitter.com/"),
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

        for url in youtube_urls:
            if isinstance(message, ContextMenuContext):
                await message.respond(
                    url[0]
                    .replace(
                        "https://youtube.com/watch?v=",
                        "https://lillieh1000.gay/yt/?videoID=",
                    )
                    .replace(
                        "https://youtu.be/", "https://lillieh1000.gay/yt/?videoID="
                    )
                    + "#",
                    components=components,
                    allowed_mentions=AllowedMentions.none(),
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
        youtube_regex = r"(https:\/\/(www\.)?(youtube\.com\/watch\?v=[A-Za-z0-9_]+|youtu\.be\/[A-Za-z0-9_]+))"

        tiktok_urls = re.findall(tiktok_regex, text)
        instagram_urls = re.findall(instagram_regex, text)
        twitter_urls = re.findall(
            twitter_regex, text.replace("https://x.com/", "https://twitter.com/")
        )
        reddit_urls = re.findall(reddit_regex, text)
        youtube_urls = re.findall(youtube_regex, text)

        return tiktok_urls, instagram_urls, twitter_urls, reddit_urls, youtube_urls

    @cached(ttl=86400)
    async def quickvids(self, tiktok_url):
        try:
            headers = {
                "content-type": "application/json",
                "user-agent": "Keto - stkc.win",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                url = "https://api.quickvids.win/v1/shorturl/create"
                data = {"input_text": tiktok_url, "detailed": True}
                async with session.post(
                    url, json=data, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        data = json.loads(text)
                        quickvids_url = data["quickvids_url"]
                        likes = data["details"]["video"]["counts"]["likes"]
                        comments = data["details"]["video"]["counts"]["comments"]
                        views = data["details"]["video"]["counts"]["views"]
                        description = data["details"]["video"]["raw_description"][:2000]
                        author = data["details"]["author"]["username"]
                        author_avatar = data["details"]["author"]["avatar"]
                        author_link = data["details"]["author"]["link"]
                        return (
                            quickvids_url,
                            likes,
                            comments,
                            views,
                            description,
                            author,
                            author_avatar,
                            author_link,
                        )
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

    async def format_number_str(self, num):
        if num >= 1000:
            powers = ["", "k", "M", "B", "T"]
            power = max(0, min(int((len(str(num)) - 1) / 3), len(powers) - 1))
            scaled_num = round(num / (1000**power), 1)
            formatted_num = f"{scaled_num:.1f}{powers[power]}"
            return formatted_num
        else:
            return str(num)


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""

    FixSocials(bot)
