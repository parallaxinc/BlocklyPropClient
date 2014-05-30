# -*- mode: python -*-
a = Analysis(['BlocklyServer.py'],

             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BlocklyPropClient',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='blocklyprop.ico' )
propeller_libs_and_tools = Tree('propeller-tools', prefix='propeller-tools', excludes=['*.pdf'])
propeller_libs_and_tools += Tree('propeller-lib', prefix='propeller-lib')
propeller_libs_and_tools += Tree('propeller-c-lib', prefix='propeller-c-lib', excludes=['*.html', 'html', '*.doxyfile', '*.side', '*.c'])
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               propeller_libs_and_tools,
               strip=None,
               upx=True,
               name='linux')

# Analysis
#             pathex=['D:\\Development\\python\\BlocklyPropClient'],
