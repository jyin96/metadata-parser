from kivy.deps import sdl2, glew
# -*- mode: python -*-

block_cipher = None


a = Analysis(['test.py'],
             pathex=["F:\\Jeff's Stuff\\python\\pytests\\avast_testing"],
             binaries=[('./opencv_ffmpeg344_64.dll','.')],
             datas=[('./kv','.'),('./res','.')],
             hiddenimports=['win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,Tree('../metadata_reader/'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='Metadata Reader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon='glimpse.ico' )
