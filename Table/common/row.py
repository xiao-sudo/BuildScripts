from enum import IntEnum


class RowSemantic(IntEnum):
    # Content Row
    Content = 0
    # Design Spec Row, not be exported to client lua
    DesignSpec = 1


class Row:
    def __init__(self):
        self.semantic = RowSemantic.Content
        self.content = []
        self.values = []

    def add_csv(self, value: str):
        self.content.append(value)

    def add_value(self, value):
        self.values.append(value)
