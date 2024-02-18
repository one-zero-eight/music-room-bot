import sys
import os
import time

if sys.platform != "win32":  # unix only
    os.environ["TZ"] = "Europe/Moscow"
    time.tzset()
