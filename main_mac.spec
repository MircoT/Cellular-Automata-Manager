# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='cam.sh',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               Tree(os.path.abspath('assets'), prefix='assets'),
               Tree(os.path.abspath('examples'), prefix='examples'),
               Tree(os.path.abspath('doc'), prefix='doc'),
               strip=None,
               upx=True,
               name='cam')
app = BUNDLE(coll,
             name='cam.app',
             icon='./new_cam.ico',
             bundle_identifier=None)