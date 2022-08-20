from .data import DataType
from .elem import ElemAnalyzer


class Field:
    def __init__(self, tag, field_name: str, sheet_col: int, field_index: int, data_type: DataType, primary=False):
        self.tag = tag
        self.field_name = field_name
        self.sheet_col = sheet_col
        self.field_index = field_index
        self.data_type = data_type
        self.primary = primary

    def __str__(self):
        return f'{self.field_name} tag: {self.tag}, sheet_col:{self.sheet_col}, ' \
               f'index: {self.field_index}, {self.data_type}'

    def update_field_index(self, new_index: int):
        self.field_index = new_index

    def check_text(self, text: str):
        checker = ElemAnalyzer.get_checker(self.data_type.elem_type, self.data_type.organization)
        return checker(text)
