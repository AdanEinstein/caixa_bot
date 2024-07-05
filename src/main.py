import os
from src.robots.data_transform import DataTransform
from src.input import choice_notice, get_answer, get_output_path, get_state
from src.robots.web_scrapper import WebScrapper


def main():
    checkpoint = False
    state = get_state()
    choice_output = get_answer('Deseja escolher o destino da planilha:')
    path = get_output_path(choice_output)
    choice = choice_notice(state)
    print(f'[Escolhido]: {choice}')
    print(f'Caminho do arquivo: {path}')
    print(f'Iniciando scraping para o estado {state["nome"]}')
    print('Aguarde, esse processo pode demorar um pouco...')
    with DataTransform(output=path) as dt:
        with WebScrapper() as ws:
            ws = ws.access_page()\
                .select_state(state)
            for notice in ws.iterate_notices():
                if choice == notice['name']:
                    checkpoint = True
                if not checkpoint:
                    continue
                for prop in ws.iterate_all_properties(notice['open_notice_cmd']):
                    data = ws.open_property(prop, dt.contains)
                    if data:
                        dt.append_data(data)
                    prop['bar'].next()
    os.system(f'explorer "{os.path.dirname(path)}"')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
