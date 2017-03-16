# -*- mode: python -*-

block_cipher = None


a = Analysis(['BlocklyPropClient.py'],
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
          exclude_binaries=True,
          name='BlocklyPropClient',
          debug=False,
          strip=False,
          upx=False,
          console=False , icon='BlocklyPropClient.ico')

#Propeller Tools
propeller_libs_and_tools = Tree('propeller-tools', prefix='propeller-tools', excludes=['*.pdf', 'windows', 'mac'])
propeller_libs_and_tools += [('about.txt', 'about.txt', 'About file')]

#Collection (edited to include Propeller Tools)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               propeller_libs_and_tools,
               strip=False,
               upx=False,
               name='BlocklyPropClient')

# Analysis
#             pathex=['/home/developer/Projects/BlocklyPropClient'],

