# -*- mode: python -*-
a = Analysis(['BlocklyPropClient.py'],

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
          upx=false,
          console=True,
          icon='blocklyprop.ico' )
propeller_libs_and_tools = Tree('propeller-tools', prefix='propeller-tools', excludes=['*.pdf', 'windows', 'mac'])
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               propeller_libs_and_tools,
               strip=None,
               upx=True,
               name='BlocklyPropClient.linux')

# Analysis
#             pathex=['D:\\Development\\python\\BlocklyPropClient'],
