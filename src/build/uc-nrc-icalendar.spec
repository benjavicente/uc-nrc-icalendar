# -*- mode: python -*-
# pylint: skip-file

from os import path

block_cipher = None

a = Analysis([path.join('..', 'gui.py')],
             pathex=['build'],
             binaries=[],
             datas=[(path.join('..', 'assets'), 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='uc-nrc-icalendar',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
