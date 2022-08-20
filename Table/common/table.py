import csv
from .field import Field
from .tag import Tag


class Header:
    def __init__(self, name):
        self._fields = []
        self.name = name

    def add_field(self, field: Field):
        self._fields.append(field)

    def get_fields(self):
        return self._fields

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

    def export_csv(self, csv_dir: str, setting):
        target_csv_path = f"{csv_dir}/{self.name}.csv"

        rs, filtered_fields = self.header.extract_csv(setting)

        if not rs:
            return False
        else:
            # encoding is utf-8-sig (utf8-bom)
            # excel determine the file is utf8 encoding through bom,
            # without bom excel assumes the csv is encoded by current Windows codepage
            with open(target_csv_path, 'wt', encoding='utf-8-sig') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([self.xls, self.name])
                writer.writerows(Table._header_csv(filtered_fields, setting.target_tag))
                # writer.writerows(self._content_csv(filtered_fields))

            return True

    @staticmethod
    def _header_csv(filtered_fields: list, target_tag):
        tags = []
        types = []
        names = []

        for field in filtered_fields:
            tags.append(field.tag.to_str())
            types.append(Table._to_csv_type(field.data_type, target_tag))
            names.append(field.field_name)

        return [tags, types, names]

    @staticmethod
    def _to_csv_type(data_type, target_tag):
        if Tag.Client == target_tag:
            return data_type.to_client_csv_str()

        return data_type.to_server_csv_str()

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


class TableDataUtil:
    @staticmethod
    def to_csv(table: Table) -> list:
        csv_data = []
        csv_data.extend(TableDataUtil._header_csv(table.header))
        csv_data.extend(TableDataUtil._row_csv(table))
        return csv_data

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
        pass
