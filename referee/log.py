"""
Module:
    ``log.py``

Purpose:
    Logs to keep track of activities from players by the referee.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. This includes log coloring on console, log stream, etc.
    Various modifications were made to produce better logs, visually, by The Duy Nguyen (1100548).
"""

from enum import Enum
from time import time
from typing import Any, Callable


# Define simple logging utility/helpers for the referee.

class LogColor(Enum):
    """
    Enumerated class representing the color of log string. Log colors are ansi-formatted.
    The following are the currently available colors.
    """
    RED       = "\033[31m"
    GREEN     = "\033[32m"
    YELLOW    = "\033[33m"
    BLUE      = "\033[34m"
    MAGENTA   = "\033[35m"
    WHITE     = "\033[37m"
    GREY      = "\033[90m"
    CYAN      = "\033[96m"
    BOLD      = "\033[1m"
    RESET_ALL = "\033[0m"

    def __str__(self):
        return self.value

    def __value__(self):
        return self.value


class LogLevel(Enum):
    """
    Log level class representing the type of log. The log can either be:
        <li>DEBUG   : debug mode log
        <li>INFO    : helper
        <li>WARNING : warning log
        <li>ERROR   : error log (which stops the program)
        <li>CRITICAL: fatal error (thread errors, etc.)
    """
    DEBUG    = 0
    INFO     = 1
    WARNING  = 2
    ERROR    = 3
    CRITICAL = 4

    def __int__(self):
        return self.value

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)


class LogStream:
    """
    Log stream which represents a stream of actual log. It is the class responsible for
    displaying and handling log's logic.
    """
    _start_time = None
    _max_namespace_length = 0
    _global_settings = {
        "level"            : LogLevel.DEBUG,
        "handlers"         : [print],
        "ansi"             : True,
        "unicode"          : True,
        "color"            : LogColor.RESET_ALL,
        "output_time"      : False,
        "output_namespace" : True,
        "output_level"     : True,
    }

    def __init__(self,
                 namespace        : str,
                 color            : LogColor | None = None,
                 level            : LogLevel | None = None,
                 handlers         : list[Callable] | None = None,
                 unicode          : bool | None = None,
                 ansi             : bool | None = None,
                 output_time      : bool | None = None,
                 output_namespace : bool | None = None,
                 output_level     : bool | None = None,
                 ):
        """
        Log stream constructor.
        """
        self._namespace = namespace
        if color is not None:
            self._color = color
        if level is not None:
            self._level = level
        if handlers is not None:
            self._handlers = handlers
        if unicode is not None:
            self._unicode = unicode
        if ansi is not None:
            self._ansi = ansi
        if output_time is not None:
            self._output_time = output_time
        if output_namespace is not None:
            self._output_namespace = output_namespace
        if output_level is not None:
            self._output_level = output_level

        # Consistent start time for all log streams
        LogStream._start_time = LogStream._start_time or time()

        # Consistent namespace length for all log streams
        LogStream._max_namespace_length = max(
            LogStream._max_namespace_length,
            len(self._namespace)
        )

    @classmethod
    def set_global_setting(cls, key: str, value: Any):
        """
        Setting log's global setting for common use.

        Args:
            key   : the global setting's key
            value : its value to be set to
        """
        cls._global_settings[key] = value

    def setting(self, key: str) -> Any:
        """
        Return local settings (or global if local does not exist) by specified key.

        Args:
            key: the specified key

        Returns:
            if existed, return the local settings,
            otherwise return global settings
        """
        return getattr(self, f"_{key}", LogStream._global_settings[key])

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Write the log.

        Args:
            message : specified log message
            level   : log's type
        """
        message_lines = message.splitlines()
        for line in message_lines:
            self._out(
                f"{self._s_color_start()}"
                f"{self._s_namespace()}"
                f"{self._s_time()}"
                f"{self._s_level(level)}"
                f"{self._s_color_end()}"
                f"{line}"
            )

    def _out(self, message: str):
        """
        Output log.
        Args:
            message: specified message
        """
        # Optionally strip unicode symbols
        if not self.setting("unicode"):
            message = message.encode("ascii", "ignore").decode()
        for handler in self.setting("handlers"):
            handler(message)

    def debug(self, message=""):
        """
        Debug log.
        Args:
            message: the debug message
        """
        if self.setting("level") <= LogLevel.DEBUG:
            self.log(message, LogLevel.DEBUG)

    def info(self, message="\n"):
        """
        Information log.
        Args:
            message: the information message
        """
        if self.setting("level") <= LogLevel.INFO:
            self.log(message, LogLevel.INFO)

    def warning(self, message=""):
        """
        Warning log.
        Args:
            message: the warning message
        """
        if self.setting("level") <= LogLevel.WARNING:
            self.log(message, LogLevel.WARNING)

    def error(self, message=""):
        """
        Error log.
        Args:
            message: the error message
        """
        if self.setting("level") <= LogLevel.ERROR:
            self.log(message, LogLevel.ERROR)

    def critical(self, message=""):
        """
        Critical log. Note that we always print critical messages.
        Args:
            message: the critical message
        """
        self.log(message, LogLevel.CRITICAL)

    def _s_time(self) -> str:
        """
        Get the current time (wrt starting the game).
        """
        if not self.setting("output_time"):
            return ""
        update_time = time() - (LogStream._start_time or 0)
        return f"T{update_time:06.2f} "

    def _s_namespace(self) -> str:
        """
        Get the current namespace.
        """
        if not self.setting("output_namespace"):
            return ""
        return f"* {self._namespace:<{LogStream._max_namespace_length}} "

    def _s_level(self, level=LogLevel.INFO) -> str:
        """
        Get the current log level for referee.

        Args:
            level: the log level
        Returns:
            encoded string for corresponding log level
        """
        if not self.setting("output_level"):
            return ""
        return {
            LogLevel.DEBUG    : "~",
            LogLevel.INFO     : ":",
            LogLevel.WARNING  : "#",
            LogLevel.ERROR    : "!",
            LogLevel.CRITICAL : "@"
        }[level] + " "

    def _s_color_start(self) -> str:
        """
        Get the color of the start player (maybe I really don't know actually, there
        were minimal documentations).
        """
        if not self.setting("ansi"):
            return ""
        return f"{self.setting('color')}"

    def _s_color_end(self) -> str:
        """
        Get the color of end player (??).
        """
        if not self.setting("ansi"):
            return ""
        return f"{LogColor.RESET_ALL}"


class NullLogger(LogStream):
    """
    Null logger class represents a log that does not do anything.
    """
    def __init__(self):
        super().__init__("null", None, LogLevel.ERROR)

    def log(self, *_):
        pass
