from .data import DataType


class Field:
    def __init__(self, tag, field_name: str, sheet_col: int, data_type: DataType, primary=False):
        self.tag = tag
        self.field_name = field_name
        self.sheet_col = sheet_col
        self.data_type = data_type
        self.primary = primary
        self.field_index = -1

    def __str__(self):
        return f'{self.field_name} tag: {self.tag}, sheet_col:{self.sheet_col}, ' \
               f'index: {self.field_index}, {self.data_type}'

    def update_field_index(self, new_index: int):
        self.field_index = new_index
