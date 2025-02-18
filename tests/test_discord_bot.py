import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.cli.discord_bot import DiscordBot

@pytest.fixture
def scriptService_mock():
    """ScriptService를 모킹하여 반환."""
    return MagicMock()

@pytest.fixture
def bot(scriptService_mock):
    """
    DiscordBot 인스턴스 생성.
    - scriptService를 mock으로 주입
    """
    return DiscordBot(scriptService=scriptService_mock)

@pytest.fixture
def message():
    """
    Discord 메시지 객체를 mock으로 생성.
    - content, channel, author 등 자주 쓰는 속성만 설정
    """
    msg = MagicMock()
    msg.author = MagicMock()
    channel_mock = MagicMock()
    channel_mock.send = AsyncMock()
    msg.channel = channel_mock
    return msg


@pytest.mark.asyncio
async def test_unknown_command(bot, message):
    """
    '$abc' 처럼 존재하지 않는 명령이 들어왔을 때
    Unknown command: abc
    """
    message.content = "$abc"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Unknown command: abc" in sent_args[0]


@pytest.mark.asyncio
async def test_help_command(bot, message):
    """
    '$help' -> help_msg가 전송되는지
    """
    message.content = "$help"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Command list" in sent_args[0]
    assert "$repo list" in sent_args[0]


# -----------------------------------------------------------------------------
# REPO 명령어 관련
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repo_no_args(bot, message):
    """
    '$repo' -> Usage 안내
    """
    message.content = "$repo"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Usage: $repo" in sent_args[0]


@pytest.mark.asyncio
async def test_repo_list(bot, message, scriptService_mock):
    """
    '$repo list' -> scriptService.get_repo_list() 호출, 결과를 채널에 전송
    """
    message.content = "$repo list"
    scriptService_mock.get_repo_list.return_value = ["repo1", "repo2"]

    await bot.client.on_message(message)

    scriptService_mock.get_repo_list.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Repo list: ['repo1', 'repo2']" in sent_args[0]


@pytest.mark.asyncio
async def test_repo_start(bot, message, scriptService_mock):
    """
    '$repo --name "myrepo" start --arg "-v"'
    -> scriptService.start_repo("myrepo", "-v")
    """
    message.content = '$repo --name "myrepo" start --arg "-v"'
    await bot.client.on_message(message)

    scriptService_mock.start_repo.assert_called_once_with("myrepo", "-v")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Started repo 'myrepo' with arg -v" in sent_args[0]


@pytest.mark.asyncio
async def test_repo_stop(bot, message, scriptService_mock):
    message.content = '$repo --name "myrepo" stop'
    await bot.client.on_message(message)

    scriptService_mock.stop_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Stopped repo 'myrepo'." in sent_args[0]


@pytest.mark.asyncio
async def test_repo_restart(bot, message, scriptService_mock):
    message.content = '$repo --name "myrepo" restart'
    await bot.client.on_message(message)

    scriptService_mock.restart_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Restarted repo 'myrepo'." in sent_args[0]


@pytest.mark.asyncio
async def test_repo_kill(bot, message, scriptService_mock):
    message.content = '$repo --name "myrepo" kill'
    await bot.client.on_message(message)

    scriptService_mock.kill_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Killed repo 'myrepo'." in sent_args[0]


@pytest.mark.asyncio
async def test_repo_no_name(bot, message):
    """
    '$repo stop' -> --name 없이 stop이 들어오면 "Need to specify --name"
    """
    message.content = "$repo stop"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Need to specify --name" in sent_args[0]


@pytest.mark.asyncio
async def test_repo_status(bot, message, scriptService_mock):
    """
    '$repo --name "myrepo" status'
    """
    # given
    message.content = '$repo --name "myrepo" status'
    scriptService_mock.status_repo.return_value = "running"

    # when
    await bot.client.on_message(message)

    # then
    scriptService_mock.status_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once_with("Repo 'myrepo' is running.")

@pytest.mark.asyncio
async def test_repo_status_nonexistent(bot, message, scriptService_mock):
    """
    없는 레포 조회 시 -> ValueError -> Discord에 에러 메시지 전송
    """
    message.content = '$repo --name "foo" status'
    scriptService_mock.status_repo.side_effect = ValueError("Repo 'foo' does not exist.")

    await bot.client.on_message(message)

    scriptService_mock.status_repo.assert_called_once_with("foo")
    message.channel.send.assert_called_once_with("Repo 'foo' does not exist.")


# -----------------------------------------------------------------------------
# LOG 명령어 관련
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_log_no_args(bot, message):
    """
    '$log' -> Usage
    """
    message.content = "$log"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Usage: $log" in sent_args[0]


@pytest.mark.asyncio
async def test_log_all(bot, message, scriptService_mock):
    """
    '$log --all' -> scriptService.get_all_logs()
    """
    message.content = "$log --all"
    scriptService_mock.get_all_logs.return_value = "ALL LOGS"

    await bot.client.on_message(message)

    scriptService_mock.get_all_logs.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "ALL LOGS" in sent_args[0]


@pytest.mark.asyncio
async def test_log_today(bot, message, scriptService_mock):
    """
    '$log --today' -> scriptService.get_today_logs()
    """
    message.content = "$log --today"
    scriptService_mock.get_today_logs.return_value = "TODAY LOGS"

    await bot.client.on_message(message)

    scriptService_mock.get_today_logs.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "TODAY LOGS" in sent_args[0]


@pytest.mark.asyncio
async def test_log_invalid(bot, message):
    """
    '$log --unknown' -> "No valid log option found."
    """
    message.content = "$log --unknown"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "No valid log option found." in sent_args[0]


# -----------------------------------------------------------------------------
# SYSTEM 명령어 관련
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_system_no_args(bot, message):
    """
    '$system' -> Usage
    """
    message.content = "$system"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Usage: $system" in sent_args[0]


@pytest.mark.asyncio
async def test_system_restart(bot, message, scriptService_mock):
    """
    '$system restart' -> scriptService.restart_system(alert=False)
    """
    message.content = "$system restart"
    await bot.client.on_message(message)

    scriptService_mock.restart_system.assert_called_once_with(alert=False)
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "System restarting..." in sent_args[0]


@pytest.mark.asyncio
async def test_system_restart_alert(bot, message, scriptService_mock):
    """
    '$system restart --alert' -> scriptService.restart_system(alert=True)
    """
    message.content = "$system restart --alert"
    await bot.client.on_message(message)

    scriptService_mock.restart_system.assert_called_once_with(alert=True)
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Alert mode on" in sent_args[0]


@pytest.mark.asyncio
async def test_system_status(bot, message, scriptService_mock):
    """
    '$system status' -> CPU/Temp 없는 경우 None
    """
    message.content = "$system status"
    # 기본: cpu/temp는 None
    scriptService_mock.get_cpu_usage.return_value = None
    scriptService_mock.get_temp.return_value = None

    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    # System status:
    # (no CPU or Temp lines)
    assert "System status:" in sent_args[0]
    assert "CPU" not in sent_args[0]
    assert "Temp" not in sent_args[0]


@pytest.mark.asyncio
async def test_system_status_cpu_temp(bot, message, scriptService_mock):
    """
    '$system status --cpu --temp'
      -> scriptService.get_cpu_usage()
      -> scriptService.get_temp()
    """
    message.content = "$system status --cpu --temp"
    scriptService_mock.get_cpu_usage.return_value = "CPU usage X"
    scriptService_mock.get_temp.return_value = "Temp Y"

    await bot.client.on_message(message)

    scriptService_mock.get_cpu_usage.assert_called_once()
    scriptService_mock.get_temp.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "CPU usage X" in sent_args[0]
    assert "Temp Y" in sent_args[0]


@pytest.mark.asyncio
async def test_system_unknown(bot, message):
    """
    '$system something' -> Unknown system command
    """
    message.content = "$system something"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Unknown system command: something" in sent_args[0]


# -----------------------------------------------------------------------------
# GIT 명령어 관련
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_git_no_args(bot, message):
    """
    '$git' -> Usage
    """
    message.content = "$git"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Usage: $git fetch" in sent_args[0]


@pytest.mark.asyncio
async def test_git_fetch_all(bot, message, scriptService_mock):
    """
    '$git fetch --all'
    """
    message.content = "$git fetch --all"
    await bot.client.on_message(message)

    scriptService_mock.git_fetch_all.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Fetched all repos." in sent_args[0]


@pytest.mark.asyncio
async def test_git_fetch_repo(bot, message, scriptService_mock):
    """
    '$git fetch --repo myrepo'
    """
    message.content = "$git fetch --repo myrepo"
    await bot.client.on_message(message)

    scriptService_mock.git_fetch_repo.assert_called_once_with("myrepo")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Fetched repo myrepo." in sent_args[0]


@pytest.mark.asyncio
async def test_git_fetch_no_repo(bot, message):
    """
    '$git fetch --repo' -> usage
    """
    message.content = "$git fetch --repo"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "No repo specified." in sent_args[0]


@pytest.mark.asyncio
async def test_git_unknown_subcmd(bot, message):
    """
    '$git push' -> Unknown git command: push
    """
    message.content = "$git push"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Unknown git command: push" in sent_args[0]


# -----------------------------------------------------------------------------
# CONTAINER 명령어 관련
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_container_no_args(bot, message):
    """
    '$container' -> Usage
    """
    message.content = "$container"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Usage: $container --list" in sent_args[0]


@pytest.mark.asyncio
async def test_container_list(bot, message, scriptService_mock):
    """
    '$container --list' -> scriptService.list_containers()
    """
    message.content = "$container --list"
    scriptService_mock.list_containers.return_value = ["c1", "c2"]

    await bot.client.on_message(message)

    scriptService_mock.list_containers.assert_called_once()
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Container list: ['c1', 'c2']" in sent_args[0]


@pytest.mark.asyncio
async def test_container_start(bot, message, scriptService_mock):
    """
    '$container --name mycont --start'
    """
    message.content = "$container --name mycont --start"
    await bot.client.on_message(message)

    scriptService_mock.container_start.assert_called_once_with("mycont")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Container 'mycont' started." in sent_args[0]


@pytest.mark.asyncio
async def test_container_stop(bot, message, scriptService_mock):
    """
    '$container --name mycont --stop'
    """
    message.content = "$container --name mycont --stop"
    await bot.client.on_message(message)

    scriptService_mock.container_stop.assert_called_once_with("mycont")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Container 'mycont' stopped." in sent_args[0]


@pytest.mark.asyncio
async def test_container_restart(bot, message, scriptService_mock):
    """
    '$container --name mycont --restart'
    """
    message.content = "$container --name mycont --restart"
    await bot.client.on_message(message)

    scriptService_mock.container_restart.assert_called_once_with("mycont")
    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Container 'mycont' restarted." in sent_args[0]


@pytest.mark.asyncio
async def test_container_no_name(bot, message):
    """
    '$container --start' -> Please specify --name
    """
    message.content = "$container --start"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Please specify --name" in sent_args[0]


@pytest.mark.asyncio
async def test_container_unknown_action(bot, message):
    """
    '$container --name cont --foobar' -> Unknown container action
    """
    message.content = "$container --name cont --foobar"
    await bot.client.on_message(message)

    message.channel.send.assert_called_once()
    sent_args, _ = message.channel.send.call_args
    assert "Unknown container action." in sent_args[0]
