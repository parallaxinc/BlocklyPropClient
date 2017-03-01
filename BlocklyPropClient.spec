# -*- mode: python -*-

block_cipher = None


a = Analysis(['BlocklyPropClient.py'],
             pathex=['/Users/jmartin/PythonProjects/BlocklyPropClient'],
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
          upx=True,
          console=False , icon='package/mac-resources/BlocklyPropClient.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='BlocklyPropClient')
app = BUNDLE(coll,
             name='BlocklyPropClient.app',
             icon='./package/mac-resources/BlocklyPropClient.icns',
             bundle_identifier=None)
