"""
Перехват логов Python и отправка в GUI через очередь.
"""
import logging
import queue


class QueueLogHandler(logging.Handler):
    """Handler, который пишет логи в queue.Queue — GUI читает из неё."""

    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.log_queue.put_nowait(msg)
        except Exception:
            pass