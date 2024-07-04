from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': ['fitz', 'pytesseract', 'PIL', 'pandas', 'numpy', 'openpyxl', 'consolemenu', 'requests', 'progress', 'pymupdf'],
    'excludes': [],
    'build_exe': 'build/caixa_bot',
    'include_files': ['resources/', '.env.ini', 'LICENSE'],
    'include_msvcr': True
}

base = 'console'

executables = [
    Executable('src/main.py', base=base, target_name='caixa_bot')
]

setup(name='caixa_bot',
      version='1.0',
      description='RPA que exporta uma planilha com as informações dos editais do banco CAIXA dos proprietários que estão pendentes em financiamento',
      options={'build_exe': build_options},
      executables=executables)
