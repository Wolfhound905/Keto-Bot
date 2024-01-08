import io, aiohttp, re
from interactions import (
    Permissions,
    AutoShardedClient,
    slash_default_member_permission,
    OptionType,
    Extension,
    Button,
    ButtonStyle,
    ContextMenuContext,
    context_menu,
    CommandType,
    cooldown,
    Buckets,
    SlashContext,
    slash_command,
    slash_option,
    PartialEmoji,
)


class Emojis(Extension):
    bot: AutoShardedClient

    @slash_command(name="jumbo", description="Jumbo an emoji")
    @slash_option(
        name="emoji",
        description="The emoji to jumbo",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def jumbo(self, ctx: SlashContext, emoji: str):
        emoji = PartialEmoji.from_str(emoji)

        if not emoji.id:
            return await ctx.send("Invalid emoji.", ephemeral=True)

        await ctx.send(
            f"https://cdn.discordapp.com/emojis/{emoji.id}.{('gif' if emoji.animated else 'png')}?size=4096"
        )

    @context_menu(name="Steal Emojis", context_type=CommandType.MESSAGE)
    @slash_default_member_permission(Permissions.MANAGE_EMOJIS_AND_STICKERS)
    @cooldown(Buckets.USER, 1, 5)
    async def steal_ctxmenu(self, ctx: ContextMenuContext):
        message = ctx.target
        components = Button(
            style=ButtonStyle.URL,
            label="Jump to Original Message",
            url=message.jump_url,
        )

        matches = re.findall(r"<(a?):(\w+):(\d+)>", message.content)

        if not matches:
            return await ctx.respond(
                "No emojis found.", ephemeral=True, components=components
            )

        if len(matches) > 5:
            return await ctx.respond(
                "You can only steal up to 5 emojis at a time.",
                ephemeral=True,
                components=components,
            )

        added_emojis = []
        processed_ids = set()  # Track processed IDs

        for match in matches:
            emoji_name = match[1]
            emoji_id = match[2]

            if emoji_id in processed_ids:
                continue  # Skip if ID has already been processed

            is_animated = match[0].startswith("a")
            file_extension = "gif" if is_animated else "png"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_extension}"
                ) as resp:
                    image = io.BytesIO(await resp.read())
                    e = await ctx.guild.create_custom_emoji(
                        imagefile=image, name=emoji_name
                    )
                    added_emojis.append(
                        f"<{'a' if e.animated else ''}:{e.name}:{e.id}> `:{e.name}:`"
                    )
                    processed_ids.add(emoji_id)  # Add ID to the processed set

        if added_emojis:
            emojis_text = ", ".join(added_emojis)
            if len(added_emojis) > 1:
                await ctx.send(
                    f"Emojis {emojis_text} were added.", components=components
                )
            else:
                await ctx.send(f"Emoji {emojis_text} was added.", components=components)

    @slash_command(name="steal", description="Steal an emoji")
    @slash_option(
        name="emoji",
        description="Discord emoji or a URL to an image",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="name",
        description="Name of the emoji",
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_default_member_permission(Permissions.MANAGE_EMOJIS_AND_STICKERS)
    @cooldown(Buckets.USER, 1, 5)
    async def steal(self, ctx: SlashContext, emoji: str, name: str = None):
        get_emoji = PartialEmoji.from_str(emoji)

        if name and not name.isalnum():
            return await ctx.send("Emoji name must be alphanumeric.", ephemeral=True)
        if get_emoji:
            url = f"https://cdn.discordapp.com/emojis/{get_emoji.id}.{('gif' if get_emoji.animated else 'png')}"
        elif name is None:
            return await ctx.send(
                "You must provide a name for the emoji.", ephemeral=True
            )

        async with aiohttp.ClientSession() as session:
            async with session.get(emoji if not get_emoji else url) as resp:
                image = io.BytesIO(await resp.read())
                e = await ctx.guild.create_custom_emoji(
                    imagefile=image, name=name if name is not None else get_emoji.name
                )
                await ctx.send(
                    f"Emoji <{'a' if e.animated else ''}:{e.name}:{e.id}> `:{e.name}:` was added."
                )

    @slash_command(name="delete", description="Delete an emoji")
    @slash_option(
        name="emoji",
        description="Discord emoji",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_default_member_permission(Permissions.MANAGE_EMOJIS_AND_STICKERS)
    @cooldown(Buckets.USER, 1, 5)
    async def delete(self, ctx: SlashContext, emoji: str):
        emoji = PartialEmoji.from_str(emoji)

        if not emoji:
            return await ctx.send("Emoji not found.", ephemeral=True)

        emoji = await ctx.guild.fetch_custom_emoji(emoji)
        try:
            await emoji.delete()
        except AttributeError:
            return await ctx.send(
                "Emoji not found, it might not belong to this server.", ephemeral=True
            )
        await ctx.send(f"Emoji `:{emoji.name}:` was deleted.")


def setup(bot: AutoShardedClient):
    Emojis(bot)
