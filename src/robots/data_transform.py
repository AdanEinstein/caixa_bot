import os
import re
from typing import Callable, Self
import pandas as pd
from contextlib import AbstractContextManager

from src.types import Data


class DataTransform(AbstractContextManager):

    def __init__(self, output: str = os.path.join(os.path.abspath(os.path.curdir), 'output', 'data.xlsx')):
        self.output_path = output
        if os.path.exists(self.output_path):
            self.df = pd.read_excel(self.output_path)
        else:
            self.df = pd.DataFrame(columns=['nome',
                                            'cpf',
                                            'edital',
                                            'endereco',
                                            'item',
                                            'valor',
                                            'data'])

    def append_data(self, data: Data):
        self.df.loc[len(self.df)] = data # type: ignore

    def contains(self, word: str) -> bool:
        has_word: Callable[[pd.Series], bool] = lambda r: r.astype(str).str.contains(re.escape(word)).any()
        result = self.df.apply(has_word, axis=1).any()
        return result

    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.df.to_excel(self.output_path, index=False)


if __name__ == '__main__':
    ...