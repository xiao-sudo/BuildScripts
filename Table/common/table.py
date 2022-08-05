import csv
from enum import Enum


class Tag(Enum):
    Client = 0
    Server = 1
    CS = 2

    def to_str(self):
        return tag_str_dict[self]

    @staticmethod
    def from_str(tag_str: str):
        return str_tag_dict[tag_str]


tag_str_dict = {
    Tag.Client: 'C',
    Tag.Server: 'S',
    Tag.CS: 'CS'
}

str_tag_dict = {
    'c': Tag.Client,
    'C': Tag.Client,
    's': Tag.Server,
    'S': Tag.Server,
    '': Tag.CS,
    'cs': Tag.CS,
    'CS': Tag.CS
}


def is_client_compatible_tag(tag: Tag):
    return Tag.Client == tag or Tag.CS == tag


def is_server_compatible_tag(tag: Tag):
    return Tag.Server == tag or Tag.CS == tag


def is_client_only_tag(tag: Tag):
    return Tag.Client == tag


def is_server_only_tag(tag: Tag):
    return Tag.Server == tag


class ElemType(Enum):
    Int = 0
    Float = 1
    Str = 2
    Bool = 3
    Unknown = 4

    @staticmethod
    def from_str(type_str: str):
        elem_type_str = type_str[:3]

        if 'INT' == elem_type_str:
            return ElemType.Int

        if 'FLO' == elem_type_str:
            return ElemType.Float

        if 'STR' == elem_type_str:
            return ElemType.Str

        if 'BOO' == elem_type_str:
            return ElemType.Bool

        return ElemType.Unknown


class ObjectType(Enum):
    Primitive = 0
    Array = 1
    Array2D = 2

    @staticmethod
    def from_str(obj_type_str: str):
        if '[]' != obj_type_str[-2:]:
            return ObjectType.Primitive

        if '[][]' == obj_type_str[-4:]:
            return ObjectType.Array2D

        return ObjectType.Array


class FieldType:
    def __init__(self, field_type_str: str):
        self.field_type_str = field_type_str.strip()
        self._parse()

    def _parse(self):
        self.object_type = ObjectType.from_str(self.field_type_str)
        self.elem_type = ElemType.from_str(self.field_type_str)

    def __str__(self):
        return self.field_type_str


class Field:
    def __init__(self, name):
        self.field_type = None
        self.index = None
        self.tag = None
        self.name = name

    def set_index(self, index: int):
        self.index = index

    def set_field_type(self, field_type: FieldType):
        self.field_type = field_type

    def set_field_tag(self, tag: Tag):
        self.tag = tag

    def __str__(self):
        return f'index : {self.index}, name: {self.name}, tag : {self.tag}, field type : {self.field_type}'


class Header:
    def __init__(self):
        self._fields = []

    def add_field(self, field: Field):
        self._fields.append(field)

    def get_fields(self):
        return self._fields

    def get_csv(self):
        tags = []
        types = []
        names = []

        for field in self._fields:
            tags.append(field.tag.to_str())
            types.append(field.field_type.field_type_str)
            names.append(field.name)

        return [tags, types, names]


class Table:
    def __init__(self, name: str, xls: str):
        self.xls = xls
        self.name = name
        self.header = None
        self.rows = []

        self._dialect = csv.unix_dialect
        self._dialect.quoting = csv.QUOTE_MINIMAL

    def set_header(self, header: Header):
        self.header = header

    def add_row(self, row: list):
        self.rows.append(row)

    def export_csv(self, csv_dir: str):
        target_csv_path = f"{csv_dir}/{self.name}.csv"
        with open(target_csv_path, 'wt') as csv_file:
            writer = csv.writer(csv_file, dialect=self._dialect)
            self.__export_header(writer)
            writer.writerows(self.rows)

    def __export_header(self, writer):
        writer.writerows(self.header.get_csv())
