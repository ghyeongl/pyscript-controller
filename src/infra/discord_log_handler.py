import logging
from queue import Queue

class DiscordLogHandler(logging.Handler):
    """
    레벨≥ERROR 로그가 발생하면 이 핸들러가 큐에 메시지를 쌓는다.
    DiscordBot이 별도 태스크로 큐를 모니터링하고, 채널에 전송.
    """

    def __init__(self, level=logging.ERROR):
        super().__init__(level=level)
        self.queue = Queue()

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.queue.put(msg)
        except Exception:
            self.handleError(record)

    def get_queue(self):
        return self.queue
