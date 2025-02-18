# main.py
import asyncio
import os
import logging
from src.infra.process_manager import ProcessManager
from src.cli.discord_bot import DiscordBot

# Logger 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_discord_token(token_file="token.txt"):
    """
    token_file에서 디스코드 봇 토큰을 읽어온 뒤 반환.
    """
    file_path = os.path.join(os.path.dirname(__file__), token_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        token = f.read().strip()
    return token

def main():
    logger.info("[Controller] Starting pyscript-controller...")
    manager = ProcessManager(exec_repo_path="executive-repository")  # or absolute path
    bot = DiscordBot(manager=manager)
    
    # 1) Discord 봇 구동(비동기로 이벤트 루프)
    loop = asyncio.get_event_loop()

    # 별도 함수로부터 토큰을 로드
    token = load_discord_token("token.txt")

    # Discord Bot 구동
    loop.create_task(bot.run_discord_bot(token=token))
    
    # 2) 레포의 main.py 실행
    manager.start_all()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("[Controller] Shutting down...")
    finally:
        manager.stop_all()
        loop.stop()

if __name__ == "__main__":
    main()
