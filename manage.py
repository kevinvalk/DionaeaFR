#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DionaeaFR.settings")

    from django.core.management import execute_from_command_line
    from django.conf import settings

    pid = str(os.getpid())
    file(settings.PID_PATH, 'w').write(pid)

    execute_from_command_line(sys.argv)
