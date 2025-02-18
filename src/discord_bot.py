# discord_bot.py
import discord
import asyncio

class DiscordBot:
    def __init__(self, manager):
        self.manager = manager
        self.client = discord.Client(intents=discord.Intents.default())

        @self.client.event
        async def on_ready():
            print(f"[DiscordBot] Logged in as {self.client.user}")

        @self.client.event
        async def on_message(message):
            # 봇이 스스로 보내는 메시지는 무시
            if message.author == self.client.user:
                return

            # 간단한 명령어 예시
            if message.content.startswith("$stop_all"):
                self.manager.stop_all()
                await message.channel.send("All processes stopped.")
            elif message.content.startswith("$stop"):
                # 예: $stop repo1
                _, repo_name = message.content.split(" ", 1)
                self.manager.send_signal(repo_name, "STOP")
                await message.channel.send(f"Stop signal sent to {repo_name}.")
            # 그 외, 필요에 따라 명령 분기

    async def run_discord_bot(self, token):
        await self.client.start(token)
