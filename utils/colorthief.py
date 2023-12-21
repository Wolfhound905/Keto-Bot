import io
import fast_colorthief
from aiocache import cached
from urllib.request import urlopen, Request


@cached(ttl=604800)
async def get_color(query):
    try:
        req = Request(query)
        req.add_header("User-Agent", "Keto - stkc.win")
        content = urlopen(req, timeout=5).read()
        color = fast_colorthief.get_dominant_color(io.BytesIO(content), quality=100)
        return color
    except:
        color = 0x505050
        return color
