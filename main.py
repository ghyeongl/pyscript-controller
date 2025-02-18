# main.py
import asyncio
from lib.process_manager import ProcessManager
from lib.discord_bot import DiscordBot

def main():
    print("[Controller] Starting pyscript-controller...")
    manager = ProcessManager(exec_repo_path="executive-repository")  # or absolute path
    bot = DiscordBot(manager=manager)
    
    # 1) 레포의 main.py 실행
    manager.start_all()
    
    # 2) Discord 봇 구동(비동기로 이벤트 루프)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run_discord_bot(token="YOUR_DISCORD_BOT_TOKEN"))  
    # 주: 실제 토큰은 별도 파일/환경변수에서 로드 권장

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("[Controller] Shutting down...")
    finally:
        manager.stop_all()
        loop.stop()

if __name__ == "__main__":
    main()
