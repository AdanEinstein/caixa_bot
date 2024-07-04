import os
from consolemenu import SelectionMenu
from src.constants import Constants, State
from tkinter.filedialog import asksaveasfilename


def get_state() -> State:
    options = map(
        lambda state: f'{state['uf']} - {state['nome']}', Constants.STATES)
    selection_menu = SelectionMenu(
        options, title='CAIXA BOT', subtitle='Selecione qual estado será mapeado:', clear_screen=True, exit_option_text='Sair')

    selection_menu.show()

    try:
        if int(selection_menu.selected_option) == len(Constants.STATES):
            exit()
        return Constants.STATES[int(selection_menu.selected_option)]
    except Exception as e:
        raise ValueError('estado inválido')


def get_answer(title='Deseja escolher o destino da planilha:') -> bool:
    options = ['SIM', 'NÃO']
    terminal_menu = SelectionMenu(
        options, title=title, clear_screen=True, exit_option_text='Sair')

    terminal_menu.show()

    try:
        if int(terminal_menu.selected_option) == len(options):
            exit()
        return options[int(terminal_menu.selected_option)] == 'SIM'
    except Exception as e:
        raise ValueError('opção inválida')


def get_output_path(ask: bool = True):
    if ask:
        path = asksaveasfilename(title='Destino da planilha', defaultextension='.xlsx')
        if not path: 
            raise ValueError('caminho inválido')
        return path
    if not os.path.exists(os.path.join(os.path.abspath(os.path.curdir), 'output')):
        os.mkdir(os.path.join(os.path.abspath(os.path.curdir), 'output'))
    return os.path.join(os.path.abspath(os.path.curdir), 'output', 'data.xlsx')


if __name__ == "__main__":
    # get_state()
    path = get_output_path()
    print(path)
