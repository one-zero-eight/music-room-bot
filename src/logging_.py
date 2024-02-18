__all__ = ["logger"]

import logging.config
import os
from logging import LogRecord
from typing import Mapping

import yaml

import inspect


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.relativePath = os.path.relpath(record.pathname)
        return True


with open("logging.yaml", "r") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)


class LoggerFromCaller(logging.Logger):
    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args,
        exc_info,
        func: str | None = None,
        extra: Mapping[str, object] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        record = super().makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        if extra is not None:
            step_back = extra.get("step_back", 0)
            if step_back:
                step_back: int
                frame = inspect.currentframe()
                for _ in range(step_back):
                    frame = frame.f_back
                record.relativePath = os.path.relpath(frame.f_code.co_filename)
                record.pathname = frame.f_code.co_filename
                record.lineno = frame.f_lineno
        return record


logger = logging.getLogger("src")
logger.addFilter(RelativePathFilter())
logger.__class__ = LoggerFromCaller
