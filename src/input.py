import os
from pick import pick
from src.constants import Constants, State
from tkinter.filedialog import asksaveasfilename

from src.robots.web_scrapper import WebScrapper


def get_state() -> State:
    options = list(map(
        lambda state: f'{state['uf']} - {state['nome']}', Constants.STATES))
    
    _, index = pick(
        title='Selecione qual estado será mapeado',
        options=options,
        min_selection_count=1
    )

    return Constants.STATES[index] # type: ignore


def get_confirm(title='Deseja escolher o destino da planilha:') -> bool:
    options = ['SIM', 'NÃO']

    option, _ = pick(
        title=title,
        options=options
    )

    return option == 'SIM'


def get_output_path(ask: bool = True):
    if ask:
        path = asksaveasfilename(title='Destino da planilha', defaultextension='.xlsx')
        if not path: 
            raise ValueError('caminho inválido')
        return path
    if not os.path.exists(os.path.join(os.path.abspath(os.path.curdir), 'output')):
        os.mkdir(os.path.join(os.path.abspath(os.path.curdir), 'output'))
    return os.path.join(os.path.abspath(os.path.curdir), 'output', 'data.xlsx')


def notices_choired(state: State):
    options: list[str] = []
    with WebScrapper() as ws:
        ws = ws.access_page()\
            .select_state(state)
        for notice in ws.iterate_notices():
            options.append(notice['name'])

    choices = pick(
        title='Selecione os editais a serem processados',
        options=options,
        min_selection_count=1,
        multiselect=True,
    )

    return [choice[0] for choice in choices] # type: ignore
    

if __name__ == "__main__":
    state = get_state()
    path_export = get_confirm()
    path = notices_choired(state)
    print(f'{state=}')
    print(f'{path_export=}')
    print(f'{path=}')
