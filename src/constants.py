import os
from typing import TypedDict
from configparser import ConfigParser

basedir = os.path.abspath(os.curdir)
config = ConfigParser()
config.read(os.path.join(basedir, '.env.ini'))

class State(TypedDict):
    nome: str
    uf: str

class Constants:
    STATES: list[State] = [
        {"nome": "Acre", "uf": "AC"},
        {"nome": "Alagoas", "uf": "AL"},
        {"nome": "Amapá", "uf": "AP"},
        {"nome": "Amazonas", "uf": "AM"},
        {"nome": "Bahia", "uf": "BA"},
        {"nome": "Ceará", "uf": "CE"},
        {"nome": "Distrito Federal", "uf": "DF"},
        {"nome": "Espírito Santo", "uf": "ES"},
        {"nome": "Goiás", "uf": "GO"},
        {"nome": "Maranhão", "uf": "MA"},
        {"nome": "Mato Grosso", "uf": "MT"},
        {"nome": "Mato Grosso do Sul", "uf": "MS"},
        {"nome": "Minas Gerais", "uf": "MG"},
        {"nome": "Pará", "uf": "PA"},
        {"nome": "Paraíba", "uf": "PB"},
        {"nome": "Paraná", "uf": "PR"},
        {"nome": "Pernambuco", "uf": "PE"},
        {"nome": "Piauí", "uf": "PI"},
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Rio Grande do Norte", "uf": "RN"},
        {"nome": "Rio Grande do Sul", "uf": "RS"},
        {"nome": "Rondônia", "uf": "RO"},
        {"nome": "Roraima", "uf": "RR"},
        {"nome": "Santa Catarina", "uf": "SC"},
        {"nome": "São Paulo", "uf": "SP"},
        {"nome": "Sergipe", "uf": "SE"},
        {"nome": "Tocantins", "uf": "TO"}
    ]
    URL_CAIXA_PAGE = 'https://venda-imoveis.caixa.gov.br/sistema/busca-licitacoes.asp?sltTipoBusca=licitacoes'
    OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']
    OPENAI_API_CONTEXT = config['OPENAI']['OPENAI_API_CONTEXT']

if __name__ == '__main__':
    print(Constants.OPENAI_API_KEY)