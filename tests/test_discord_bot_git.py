import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.cli.discord_bot import DiscordBot

@pytest.fixture
def scriptService_mock():
    return MagicMock()

@pytest.fixture
def bot(scriptService_mock):
    return DiscordBot(scriptService=scriptService_mock)

@pytest.fixture
def message():
    msg = MagicMock()
    msg.author = MagicMock()
    channel_mock = MagicMock()
    channel_mock.send = AsyncMock()
    msg.channel = channel_mock
    return msg

@pytest.mark.asyncio
async def test_git_fetch_repo_command(bot, message, scriptService_mock):
    """
    '$git fetch --repo myrepo'
    """
    message.content = "$git fetch --repo myrepo"
    scriptService_mock.git_fetch_repo.return_value = "Fetched repo myrepo successfully."
    
    await bot.client.on_message(message)
    
    scriptService_mock.git_fetch_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Fetched repo myrepo successfully." in sent_args[0]

@pytest.mark.asyncio
async def test_git_fetch_repo_error(bot, message, scriptService_mock):
    """
    Service에서 ValueError 발생 시, 봇이 에러 메시지를 채널로 보낸다.
    """
    message.content = "$git fetch --repo unknown"

    scriptService_mock.git_fetch_repo.side_effect = ValueError("Repo not found!")
    
    await bot.client.on_message(message)

    scriptService_mock.git_fetch_repo.assert_called_once_with("unknown")
    message.channel.send.assert_called_once_with("Repo not found!")

@pytest.mark.asyncio
async def test_git_clone_command(bot, message, scriptService_mock):
    """
    '$git clone git@github.com:ghyeongl/budget-calc-discord-bot.git'
    """
    message.content = "$git clone git@github.com:ghyeongl/budget-calc-discord-bot.git"
    scriptService_mock.git_clone.return_value = "Cloned repo from git@github.com:ghyeongl/budget-calc-discord-bot.git."
    
    await bot.client.on_message(message)

    scriptService_mock.git_clone.assert_called_once_with("git@github.com:ghyeongl/budget-calc-discord-bot.git")
    message.channel.send.assert_called_once_with("Cloned repo from git@github.com:ghyeongl/budget-calc-discord-bot.git.")

@pytest.mark.asyncio
async def test_git_clone_error(bot, message, scriptService_mock):
    """
    Service에서 RuntimeError 발생 시, 봇이 에러 메시지를 채널로 보낸다.
    """
    message.content = "$git clone git@github.com:ghyeongl/budget-calc-discord-bot.git"

    scriptService_mock.git_clone.side_effect = RuntimeError("git clone failed!")
    
    await bot.client.on_message(message)

    scriptService_mock.git_clone.assert_called_once_with("git@github.com:ghyeongl/budget-calc-discord-bot.git")
    message.channel.send.assert_called_once_with("git clone failed!")
