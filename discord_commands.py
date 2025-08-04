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