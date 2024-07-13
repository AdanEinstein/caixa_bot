import os
import re
from typing import Callable, Self
import pandas as pd
from contextlib import AbstractContextManager

from src.types import Data


class DataTransform(AbstractContextManager):

    def __init__(self, output: str = os.path.join(os.path.abspath(os.path.curdir), 'output', 'data.csv')):
        self.output_path = output
        if os.path.exists(self.output_path):
            if os.path.basename(self.output_path).endswith('.csv'):
                self.df = pd.read_csv(self.output_path)
            elif os.path.basename(self.output_path).endswith('.xlsx'):
                self.df = pd.read_excel(self.output_path)
            else:
                raise Exception("Extensão do arquivo inválida")
        else:
            self.df = pd.DataFrame(columns=['nome',
                                            'cpf',
                                            'edital',
                                            'endereco',
                                            'item',
                                            'valor',
                                            'data'])

    def append_data(self, data: Data):
        new_row = pd.Series(data)  # type: ignore
        self.df = pd.concat([self.df, pd.DataFrame([new_row])],
                            ignore_index=True)  # type: ignore
        os.system('cls')
        print(self.df.tail())

    def contains(self, word: str) -> bool:
        has_word: Callable[[pd.Series], bool] = lambda r: r.astype(
            str).str.contains(re.escape(word)).any()
        result = self.df.apply(has_word, axis=1).any()
        return result

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print(f'! Exportando...')
        if os.path.basename(self.output_path).endswith('.csv'):
            self.df.to_csv(self.output_path, index=False)
        elif os.path.basename(self.output_path).endswith('.xlsx'):
            self.df.to_excel(self.output_path, index=False)
        print('> Exportado com sucesso!')


if __name__ == '__main__':
    ...
