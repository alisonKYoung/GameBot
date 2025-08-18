import discord
from discord.utils import get

async def send_dm(ctx, playername, message):
        """Internal function to DM a user."""
        if playername not in ("table1", "table2", "table3"):
            member = get(ctx.guild.members, name=playername)
            try:
                await member.send(message)
                return True
            except discord.Forbidden:
                return False
            
async def send_dm_with_reactions(bot, ctx, user_id, content, reactions):
    """Send a DM, add reactions, and return the chosen one."""
    user = ctx.guild.get_member_named(user_id)
    if not user:
        return None

    msg = await user.send(content)
    for emoji in reactions:
        await msg.add_reaction(emoji)

    def check(reaction, reactor):
        return (
            reactor == user
            and reaction.message.id == msg.id
            and str(reaction.emoji) in reactions
        )

    reaction, _ = await bot.wait_for("reaction_add", check=check)
    return str(reaction.emoji)

def blockquote(text):
    return f">>> {text}"