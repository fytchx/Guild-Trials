"""
Guild Trials Bot — Main entry point.
Run with: python bot.py
"""

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.database import init_db

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "data", "bot.log"),
            encoding="utf-8",
        ),
    ],
)
log = logging.getLogger("guild_trials")

# ─────────────────────────────────────────────
# Environment
# ─────────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    log.error("DISCORD_TOKEN is not set in .env — cannot start bot.")
    sys.exit(1)

# ─────────────────────────────────────────────
# Bot setup
# ─────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class GuildTrialsBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",   # Fallback prefix (slash commands are primary)
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        """Called before the bot connects — load cogs and sync commands."""
        await init_db()
        log.info("Database initialized.")

        cogs = [
            "cogs.trial_commands",
            "cogs.leaderboard",
            "cogs.staff",
            "cogs.admin",
            "cogs.setup",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception as exc:
                log.error(f"Failed to load cog {cog}: {exc}", exc_info=True)

        # Sync slash commands globally (takes up to 1 hour to propagate globally;
        # for instant testing, sync to a specific guild using bot.tree.sync(guild=...))
        synced = await self.tree.sync()
        log.info(f"Synced {len(synced)} slash command(s).")

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Guild Trials | /trial",
            )
        )


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
async def main():
    bot = GuildTrialsBot()
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
