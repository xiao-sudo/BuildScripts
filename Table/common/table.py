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


class ElemType(Enum):
    Int = 0
    SInt = 1
    Fixed = 2
    Float = 3
    Str = 4
    Bool = 5
    Unknown = 6

    @staticmethod
    def from_str(type_str: str, object_type: ObjectType):
        elem_type_str = ElemType._strip_array(type_str, object_type)

        if 'INT' == elem_type_str:
            return ElemType.Int

        if 'SINT' == elem_type_str:
            return ElemType.SInt

        if 'FIXED' == elem_type_str:
            return ElemType.Fixed

        if 'FLOAT' == elem_type_str:
            return ElemType.Float

        if 'STRING' == elem_type_str:
            return ElemType.Str

        if 'BOOL' == elem_type_str:
            return ElemType.Bool

        return ElemType.Unknown

    @staticmethod
    def _strip_array(type_str, object_type: ObjectType):
        if ObjectType.Primitive == object_type:
            return type_str
        else:
            if ObjectType.Array == object_type:
                return type_str[:-2]
            else:
                return type_str[:-4]


class FieldType:
    def __init__(self, field_type_str: str):
        self.field_type_str = field_type_str.strip()
        self._parse()

    def _parse(self):
        self.object_type = ObjectType.from_str(self.field_type_str)
        self.elem_type = ElemType.from_str(self.field_type_str, self.object_type)

    def __repr__(self):
        return 'FieldType(%r)' % self.field_type_str


class Field:
    def __init__(self, name, col=None, tag=None):
        self.field_type = None
        self.col = col
        self.field_index = 0
        self.tag = tag
        self.name = name

    def __repr__(self):
        return 'Field(%r, %r, %r)' % (self.name, self.col, self.tag)

    def to_value(self, v):
        if ObjectType.Primitive == self.field_type.object_type:
            if ElemType.Int == self.field_type.elem_type:
                return self._to_int(v)

        return True, v, ''

    @staticmethod
    def _to_int(v):
        rs = True
        value = 0
        err = ''
        try:
            value = int(v)
        except ValueError as value_err:
            rs = False
            err = value_err

        finally:
            return rs, value, err


class Header:
    def __init__(self, name):
        self._fields = []
        self.name = name

    def add_field(self, field: Field):
        self._fields.append(field)

    def get_fields(self):
        return self._fields

    # def get_csv(self):
    #     tags = []
    #     types = []
    #     names = []
    #
    #     for field in self._fields:
    #         tags.append(field.tag.to_str())
    #         types.append(field.field_type.field_type_str)
    #         names.append(field.name)
    #
    #     return [tags, types, names]

    def extract_csv(self, tag_filter):
        """
        extract csv fields with filter
        :param tag_filter: filter tag, client or sever
        :return: [rs, fields], has filtered info when rs = True
        """
        rs = False
        fields = []

        for field in self._fields:
            if tag_filter(field.tag):
                rs = True
                fields.append(field)

        return [rs, fields]

    def __repr__(self):
        return 'Header(%r)' % self.name


class Table:
    def __init__(self, name: str, xls: str):
        self.xls = xls
        self.name = name
        self.header = None
        self.rows = []

    def set_header(self, header: Header):
        self.header = header

    def add_row(self, row: list):
        self.rows.append(row)

    def export_csv(self, csv_dir: str, tag_filter=lambda tag: True):
        target_csv_path = f"{csv_dir}/{self.name}.csv"

        rs, filtered_fields = self.header.extract_csv(tag_filter)

        if not rs:
            return False
        else:
            # encoding is utf-8-sig (utf8-bom)
            # excel determine the file is utf8 encoding through bom,
            # without bom excel assumes the csv is encoded by current Windows codepage
            with open(target_csv_path, 'wt', encoding='utf-8-sig') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([self.xls, self.name])
                writer.writerows(Table._header_csv(filtered_fields))
                writer.writerows(self._content_csv(filtered_fields))

            return True

    @staticmethod
    def _header_csv(filtered_fields: list):
        tags = []
        types = []
        names = []

        for field in filtered_fields:
            tags.append(field.tag.to_str())
            types.append(field.field_type.field_type_str)
            names.append(field.name)

        return [tags, types, names]

    def _content_csv(self, filtered_fields: list):
        field_indices = []
        for field in filtered_fields:
            field_indices.append(field.field_index)

        filtered_rows = []
        for row in self.rows:
            filtered_row = []
            for field_index in field_indices:
                if field_index < len(row):
                    filtered_row.append(row[field_index])
                else:
                    print(f'{field_index} in {self.name} out of range')

            filtered_rows.append(filtered_row)

        return filtered_rows
