from typing import TypedDict


class Data(TypedDict):
    nome: str | None
    cpf: str | None
    item: str | None
    edital: str | None
    endereco: str | None
    valor: float | None
