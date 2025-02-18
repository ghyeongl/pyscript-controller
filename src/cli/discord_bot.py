# discord_bot.py
import discord
import asyncio
import shlex  # 문자열을 공백 기준으로 파싱, 따옴표 처리 등에 편리함

class DiscordBot:
    def __init__(self, scriptService):
        """
        scriptService: script_service.py에 정의된 ScriptService 인스턴스
        """
        self.scriptService = scriptService
        self.client = discord.Client(intents=discord.Intents.default())

        @self.client.event
        async def on_ready():
            print(f"[DiscordBot] Logged in as {self.client.user}")

        @self.client.event
        async def on_message(message):
            # 봇이 스스로 보내는 메시지는 무시
            if message.author == self.client.user:
                return

            # 봇 명령은 $로 시작한다고 가정
            if not message.content.startswith("$"):
                return

            # shlex.split()을 사용하면,
            #  "$repo --name \"repo_name\" restart" 같은 명령에서
            #  따옴표로 묶인 부분을 제대로 하나의 토큰으로 파싱해줌
            tokens = shlex.split(message.content)
            # tokens[0] = '$repo', tokens[1] = '--name', tokens[2] = 'repo_name', tokens[3] = 'restart' ...

            main_cmd = tokens[0][1:]  # '$repo'에서 '$' 제거 → 'repo'
            args = tokens[1:]        # 나머지는 서브명령/옵션들

            # 메인 명령어에 따라 분기
            if main_cmd == "repo":
                await self._handle_repo_cmd(message, args)
            elif main_cmd == "log":
                await self._handle_log_cmd(message, args)
            elif main_cmd == "system":
                await self._handle_system_cmd(message, args)
            elif main_cmd == "git":
                await self._handle_git_cmd(message, args)
            elif main_cmd == "container":
                await self._handle_container_cmd(message, args)
            elif main_cmd == "help":
                await self._handle_help_cmd(message, args)
            else:
                await message.channel.send(f"Unknown command: {main_cmd}")

    async def run_discord_bot(self, token):
        """
        실제 디스코드 봇을 실행하는 메서드
        """
        await self.client.start(token)

    # -------------------------------------------------------------------------
    # 1) $repo 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_repo_cmd(self, message, args):
        """
        예:
          $repo list
          $repo --name "repo_name" restart
          $repo --name "repo_name" start --arg "-some_args"
          $repo --name "repo_name" stop
          $repo --name "repo_name" kill
        """
        if not args:
            await message.channel.send("Usage: $repo [list|--name REPO (start|stop|restart|kill) ...]")
            return

        if args[0] == "list":
            # 레포 목록 반환
            repo_list = self.scriptService.get_repo_list()
            await message.channel.send(f"Repo list: {repo_list}")
            return

        # 그 외 --name 옵션 처리
        # ex) ['--name', 'repo_name', 'restart']
        repo_name = None
        action = None
        extra_arg = None

        i = 0
        while i < len(args):
            if args[i] == "--name":
                i += 1
                if i < len(args):
                    repo_name = args[i]
            elif args[i] in ["start", "stop", "restart", "kill", "status"]:
                action = args[i]
            elif args[i] == "--arg":
                i += 1
                if i < len(args):
                    extra_arg = args[i]
            i += 1

        if not repo_name and action != "list":
            await message.channel.send("Need to specify --name for this action.")
            return

        if action == "status":
            try:
                status = self.scriptService.status_repo(repo_name)
                await message.channel.send(f"Repo '{repo_name}' is {status}.")
            except ValueError as e:
                await message.channel.send(str(e))
        elif action == "start":
            self.scriptService.start_repo(repo_name, extra_arg)
            await message.channel.send(f"Started repo '{repo_name}' with arg {extra_arg}")
        elif action == "stop":
            self.scriptService.stop_repo(repo_name)
            await message.channel.send(f"Stopped repo '{repo_name}'.")
        elif action == "restart":
            self.scriptService.restart_repo(repo_name)
            await message.channel.send(f"Restarted repo '{repo_name}'.")
        elif action == "kill":
            self.scriptService.kill_repo(repo_name)
            await message.channel.send(f"Killed repo '{repo_name}'.")
        else:
            await message.channel.send("Unknown action. Try start/stop/restart/kill.")

    # -------------------------------------------------------------------------
    # 2) $log 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_log_cmd(self, message, args):
        """
        예:
          $log --all
          $log --today
          $log --list
          $log --repo "repo_name" --debug
        """
        if not args:
            await message.channel.send("Usage: $log --options (--all, --today, --repo, --debug, etc.)")
            return

        opts = set(args)
        if "--all" in opts:
            logs = self.scriptService.get_all_logs()
            await message.channel.send(f"All logs: {logs}")
        elif "--today" in opts:
            logs = self.scriptService.get_today_logs()
            await message.channel.send(f"Today logs: {logs}")
        else:
            await message.channel.send("No valid log option found.")

    # -------------------------------------------------------------------------
    # 3) $system 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_system_cmd(self, message, args):
        """
        예:
          $system restart --alert
          $system status --cpu --temp
        """
        if not args:
            await message.channel.send("Usage: $system [restart|status] [--alert] [--cpu] [--temp]")
            return

        cmd = args[0]
        flags = args[1:]

        if cmd == "restart":
            if "--alert" in flags:
                self.scriptService.restart_system(alert=True)
                await message.channel.send("System restarting... Alert mode on.")
            else:
                self.scriptService.restart_system(alert=False)
                await message.channel.send("System restarting...")

        elif cmd == "status":
            cpu_info = None
            temp_info = None

            if "--cpu" in flags:
                cpu_info = self.scriptService.get_cpu_usage()
            if "--temp" in flags:
                temp_info = self.scriptService.get_temp()

            msg = "System status:"
            if cpu_info is not None:
                msg += f"\n - CPU: {cpu_info}"
            if temp_info is not None:
                msg += f"\n - Temp: {temp_info}"
            await message.channel.send(msg)
        else:
            await message.channel.send(f"Unknown system command: {cmd}")

    # -------------------------------------------------------------------------
    # 4) $git 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_git_cmd(self, message, args):
        """
        예:
          $git fetch --all --repo "this_repo"
        """
        if not args:
            await message.channel.send("Usage: $git fetch [--all] [--repo REPO_NAME]")
            return

        sub_cmd = args[0]  # e.g. "fetch"
        flags = args[1:]

        if sub_cmd == "fetch":
            if "--all" in flags:
                self.scriptService.git_fetch_all()
                await message.channel.send("Fetched all repos.")
            else:
                repo_name = None
                for i, f in enumerate(flags):
                    if f == "--repo" and i + 1 < len(flags):
                        repo_name = flags[i + 1]
                if repo_name:
                    self.scriptService.git_fetch_repo(repo_name)
                    await message.channel.send(f"Fetched repo {repo_name}.")
                else:
                    await message.channel.send("No repo specified.")
        else:
            await message.channel.send(f"Unknown git command: {sub_cmd}")

    # -------------------------------------------------------------------------
    # 5) $container 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_container_cmd(self, message, args):
        """
        예:
          $container --list
          $container --name "container_name" --start
        """
        if not args:
            await message.channel.send("Usage: $container --list | --name NAME [--start|--stop|--restart]")
            return

        if "--list" in args:
            containers = self.scriptService.list_containers()
            await message.channel.send(f"Container list: {containers}")
            return

        cont_name = None
        action = None
        i = 0
        while i < len(args):
            if args[i] == "--name":
                i += 1
                if i < len(args):
                    cont_name = args[i]
            elif args[i] in ["--start", "--stop", "--restart"]:
                action = args[i][2:]  # '--start' -> 'start'
            i += 1

        if not cont_name:
            await message.channel.send("Please specify --name <container_name>.")
            return

        if action == "start":
            self.scriptService.container_start(cont_name)
            await message.channel.send(f"Container '{cont_name}' started.")
        elif action == "stop":
            self.scriptService.container_stop(cont_name)
            await message.channel.send(f"Container '{cont_name}' stopped.")
        elif action == "restart":
            self.scriptService.container_restart(cont_name)
            await message.channel.send(f"Container '{cont_name}' restarted.")
        else:
            await message.channel.send("Unknown container action. Use --start|--stop|--restart")

    # -------------------------------------------------------------------------
    # 6) $help 명령 처리
    # -------------------------------------------------------------------------
    async def _handle_help_cmd(self, message, args):
        help_msg = (
            "**Command list**\n"
            "$repo list\n"
            "$repo --name \"repo_name\" [start|stop|restart|kill] [--arg \"args\"]\n"
            "$log --all | --today | --repo \"repo_name\" | --debug ...\n"
            "$system restart [--alert]\n"
            "$system status [--cpu] [--temp]\n"
            "$git fetch --all | --repo \"repo_name\"\n"
            "$container --list | --name \"container_name\" --start\n"
            "$help (this message)\n"
        )
        await message.channel.send(help_msg)
