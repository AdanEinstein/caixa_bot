from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ['cv2', 'fitz', 'pytesseract', 'PIL', 'pandas', 'openpyxl'], 'excludes': []}

base = 'console'

executables = [
    Executable('main.py', base=base, target_name = 'caixa_bot')
]

setup(name='caixa_bot',
      version = '1.0',
      description = 'RPA que exporta uma panilha com as informações dos editais do banco CAIXA dos proprietários que estão pendentes em financiamento',
      options = {'build_exe': build_options},
      executables = executables)
