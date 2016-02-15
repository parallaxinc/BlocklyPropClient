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
          upx=True,
          console=False,
          windowed=True
          )
 # icon='blocklyprop.ico'
propeller_libs_and_tools = Tree('propeller-tools', prefix='propeller-tools', excludes=['*.pdf', 'windows', 'linux'])
propeller_libs_and_tools += [('about.txt', 'about.txt', 'About file')]
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               propeller_libs_and_tools,
               strip=None,
               upx=True,
               name='BlocklyPropClient.app',
               icon=None,
               bundle_identifier=None)

# Analysis
#             pathex=['D:\\Development\\python\\BlocklyPropClient'],
