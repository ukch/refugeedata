#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "refugeedata.app.settings")

    try:
        from refugeedata.app import local_settings
    except ImportError:
        pass
    else:
        os.environ.update(local_settings.SETTINGS_DICT)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
