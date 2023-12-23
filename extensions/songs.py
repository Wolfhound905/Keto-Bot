import aiohttp, json, asyncio
from aiocache import cached
from interactions import (
    CommandType,
    AutoShardedClient,
    Button,
    AllowedMentions,
    Embed,
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
from utils.colorthief import get_color


class Songs(Extension):
    bot: AutoShardedClient
    import re

    song_pattern = re.compile(
        r"https:\/\/(open.spotify.com\/track\/[A-Za-z0-9]+|music.apple.com\/[a-zA-Z][a-zA-Z]?\/album\/[a-zA-Z\d%\(\)-]+/[\d]{1,10}\?i=[\d]{1,15}|spotify.link\/[A-Za-z0-9]+)"
    )
    fmbot_id = 356268235697553409

    @cached(ttl=604800)
    async def process_song_link(self, link):
        title, artist, thumbnail, spotify, applemusic = await self.get_music(link)
        spotify_button = Button(
            style=ButtonStyle.URL, emoji="<:spotify:1140397216066977903>", url=spotify
        )
        applemusic_button = Button(
            style=ButtonStyle.URL,
            emoji="<:applemusic:1140397213621686396>",
            url=applemusic,
        )

        embed = Embed(
            author={"name": f"{title} - {artist}", "icon_url": thumbnail},
            color=await get_color(thumbnail),
        )

        components = []
        if spotify_button is not None:
            components.append(spotify_button)
        if applemusic_button is not None:
            components.append(applemusic_button)

        return embed, components

    @context_menu(name="Create song.link Embed", context_type=CommandType.MESSAGE)
    @cooldown(Buckets.USER, 1, 3)
    async def songlinks_ctxmenu(self, ctx: ContextMenuContext):
        message: Message = ctx.target
        jump_button = Button(
            style=ButtonStyle.URL,
            label="Jump to Original Message",
            url=message.jump_url,
        )
        jump_button_e = Button(style=ButtonStyle.URL, label="⤴️", url=message.jump_url)

        match = self.song_pattern.search(message.content.strip("<>"))
        if match:
            link = match.group(0)
        else:
            await ctx.respond(
                "No fixable links found. Use this command on Spotify and Apple Music links.",
                ephemeral=True,
                components=jump_button,
            )
            return

        embed, components = await self.process_song_link(link)
        components.insert(0, jump_button_e if len(components) > 0 else jump_button)
        await ctx.respond(components=components, embed=embed)

    @listen()
    async def on_message_create(self, event: MessageCreate):
        fmbot = False
        if (
            event.message.author.bot and event.message.author.id != self.fmbot_id
        ):  # .fmbot
            return

        if event.message.author.id == self.fmbot_id:
            fmbot = True

        match = self.song_pattern.search(event.message.content.strip("<>"))
        if match:
            link = match.group(0)
        else:
            return

        embed, components = await self.process_song_link(link)
        if fmbot:
            await event.message.delete()
            await event.message.channel.send(components=components, embed=embed)
        else:
            await event.message.reply(
                components=components,
                embed=embed,
                allowed_mentions=AllowedMentions.none(),
            )
        await asyncio.sleep(0.1)
        await event.message.suppress_embeds()

    @cached(ttl=604800)
    async def get_music(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.song.link/v1-alpha.1/links?url={url}"
            ) as resp:
                if resp.status != 200:
                    return None

                res = await resp.text()
                res = json.loads(res)

                unique_id = (
                    res.get("linksByPlatform").get("spotify", {}).get("entityUniqueId")
                )

                if unique_id is None:
                    return None

                title = res["entitiesByUniqueId"][unique_id]["title"]
                artist = res["entitiesByUniqueId"][unique_id]["artistName"]
                thumbnail = res["entitiesByUniqueId"][unique_id]["thumbnailUrl"]

                spotify_data = res.get("linksByPlatform").get("spotify")
                spotify = (
                    spotify_data.get("url") + "?autoplay=0" if spotify_data else None
                )

                applemusic_data = res.get("linksByPlatform").get("appleMusic")
                applemusic = applemusic_data.get("url") if applemusic_data else None

                return title, artist, thumbnail, spotify, applemusic


def setup(bot: AutoShardedClient):
    """Let interactions load the extension"""
    Songs(bot)
