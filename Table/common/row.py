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

    def add_value(self, value: str):
        self.content.append(value)
