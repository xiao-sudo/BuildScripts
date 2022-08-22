import csv
from .field import Field


class Header:
    def __init__(self, name):
        self._fields = []
        self.name = name
        self.curr_index = 0

    def primary(self):
        return self._fields[0]

    def add_field(self, field: Field):
        field.update_field_index(self.curr_index)
        self._fields.append(field)
        self.curr_index += 1

    def get_fields(self):
        return self._fields

    def __repr__(self):
        return 'Header(%r)' % self.name


class Table:
    def __init__(self, name: str, xls: str):
        self.xls = xls
        self.name = name
        self.header = None
        self.body = []

    def set_header(self, header: Header):
        self.header = header

    def add_row(self, row: list):
        self.body.append(row)

    def set_body(self, body: list):
        self.body = body


class TableDataUtil:
    @staticmethod
    def to_csv(table: Table) -> list:
        csv_data = []
        csv_data.extend(TableDataUtil._header_csv(table.header))
        csv_data.extend(TableDataUtil._row_csv(table))
        return csv_data

    @staticmethod
    def export_csv(file_path, table: Table):
        # encoding is utf-8-sig (utf8-bom)
        # excel determine the file is utf8 encoding through bom,
        # without bom excel assumes the csv is encoded by current Windows codepage
        with open(file_path, 'wt', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(TableDataUtil.to_csv(table))

    @staticmethod
    def _header_csv(header: Header) -> list:
        names = []
        types = []
        tags = []

        for field in header.get_fields():
            names.append(field.field_name)
            types.append(field.data_type.to_client_csv_str())
            tags.append(field.tag.to_str())

        return [names, types, tags]

    @staticmethod
    def _row_csv(table: Table) -> list:
        return table.body
