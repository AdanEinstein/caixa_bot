import os
from simple_term_menu import TerminalMenu
from src.constants import Constants, State
from tkinter.filedialog import asksaveasfilename


def get_state() -> State:
    options = map(
        lambda state: f'{state['uf']} - {state['nome']}', Constants.STATES)
    terminal_menu = TerminalMenu(
        options, title='Selecione qual estado será mapeado:', clear_screen=True)
    menu_entry_index = terminal_menu.show()
    if type(menu_entry_index) != int:
        raise ValueError('estado inválido')

    return Constants.STATES[menu_entry_index]


def get_answer(title='Deseja escolher o destino da planilha:') -> bool:
    options = ['SIM', 'NÃO']
    terminal_menu = TerminalMenu(options, title=title, clear_screen=True)

    menu_entry_index = terminal_menu.show()
    if type(menu_entry_index) != int:
        raise ValueError('opção inválida')

    return options[menu_entry_index] == 'SIM'


def get_output_path(ask: bool = True):
    if ask:
        return asksaveasfilename(title='Destino da planilha', defaultextension='.xlsx')
    return os.path.join(os.path.abspath(os.path.curdir), 'output', 'data.xlsx')


if __name__ == "__main__":
    # get_state()
    path = get_output_path()
    print(path)
