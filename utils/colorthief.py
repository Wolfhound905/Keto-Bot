import io, re, os
import fast_colorthief
from aiocache import cached
from aiohttp import ClientSession, ClientTimeout


@cached(ttl=604800)
async def get_color(query):
    quality = os.getenv("COLOR_FETCH_QUALITY", default="low")

    if quality == "off":
        return 0x505050

    try:
        # Speed up color fetching for discord avatars
        if any(
            s in query
            for s in {"cdn.discordapp.com/icons/", "cdn.discordapp.com/avatars/"}
        ):
            if quality == "low":
                query = re.sub(
                    r"\?size=(32|64|128|256|512|1024|2048|4096)$", "?size=16", query
                )
            elif quality == "medium":
                query = re.sub(
                    r"\?size=(16|32|128|256|512|1024|2048|4096)$", "?size=64", query
                )
            elif quality == "high":
                query = re.sub(
                    r"\?size=(16|32|64|256|512|1024|2048|4096)$", "?size=128", query
                )
        async with ClientSession() as session:
            async with session.get(query, timeout=5) as response:
                content = await response.read()

        color = fast_colorthief.get_dominant_color(io.BytesIO(content), quality=100)
        return color
    except:
        return 0x505050
