import io
from colorthief import ColorThief
from aiocache import cached
from urllib.request import urlopen, Request


@cached(ttl=604800)
async def get_color(query):
    try:
        req = Request(query)
        req.add_header("User-Agent", "Keto - stkc.win")
        content = urlopen(req, timeout=5).read()
        color = int(
            ("#%02x%02x%02x" % ColorThief(io.BytesIO(content)).get_color(quality=1000))[
                1:
            ],
            16,
        )
        return color
    except:
        color = 0x505050
        return color
