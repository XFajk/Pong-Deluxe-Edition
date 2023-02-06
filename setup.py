from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base, target_name = 'pong_deluxe')
]

setup(name='pong_deluxe_edition',
      version = '1.0',
      description = 'a better version of pong',
      options = {'build_exe': build_options},
      executables = executables)

