# my_django_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['manage.py'],
    pathex=['.', './API'],  # Ajout du chemin API pour qu'il soit trouvé pendant l'analyse
    binaries=[],
    datas=[
        ('djangoproject', 'djangoproject'),  # Inclure le dossier djangoproject
        ('db.sqlite', '.'),  # Inclure la base de données SQLite
        ('API', 'API'),  # Inclure le dossier API
        ('./mot_a_retire.txt', '.'),  # Inclure le fichier mot_a_retire.txt
    ],
    hiddenimports=[
        'API',  # Inclure le module API
        'API.views',  # Inclure les sous-modules nécessaires
        'API.import_csv',  # Inclure les sous-modules nécessaires

    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='test2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='test2',
)
