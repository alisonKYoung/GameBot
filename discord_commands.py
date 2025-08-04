import discord

async def send_dm(member, message):
        """Internal function to DM a user."""
        try:
            await member.send(message)
            return True
        except discord.Forbidden:
            return False