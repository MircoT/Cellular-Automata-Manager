# -*- mode: python -*-

a = Analysis(['.\\main.py'],
             pathex=['E:\\Projects\\PyScintillae'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='cam.exe',
          debug=False,
          strip=None,
          upx=True,
          icon=".\\new_cam.ico",
          console=True )
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
             name='cam')