import glob
import os.path
import re
from . import xlrd
from .table import Table, Tag, Header, Field, ElemType, FieldType


def collect_xls_files(src_dir, xls_patterns):
    all_xls_files = []
    for xls_pattern in xls_patterns:
        xls_files = (glob.glob(f'{src_dir}/{xls_pattern}'))
        for xls_file in xls_files:
            # skip the temp opening excel
            if -1 == xls_file.find("~$"):
                all_xls_files.append(xls_file)

    return all_xls_files


def is_valid_xls_sheet(sheet_name):
    return re.search("^[a-zA-Z]+=$", sheet_name)


class XlsParser:
    _tag_row = 2
    _type_row = 3
    _name_row = 4
    _content_start_row = 8

    def __init__(self):
        self.tables = []

    def parse(self, xls_path):
        abs_xls = os.path.abspath(xls_path)
        book = xlrd.open_workbook(abs_xls)
        for sheet in book.sheets():
            if is_valid_xls_sheet(sheet.name):
                tab = Table(sheet.name, xls_path)
                rs, header_or_err = self._parse_header(sheet)

                if rs:
                    tab.set_header(header_or_err)
                    self._parse_rows(sheet, tab)
                    self.tables.append(tab)
                else:
                    print(f'{xls_path} : {sheet.name} parse error => {header_or_err}')

    def _parse_header(self, sheet):
        header = Header(sheet.name)
        for col in range(sheet.ncols):
            type_cell = sheet.cell(self._type_row, col)
            type_value = type_cell.value.strip()

            if '' != type_value:
                name_cell = sheet.cell(self._name_row, col)
                name_value = name_cell.value.strip()

                if '' == name_value:
                    return False, f'field name at ({self._name_row}, {col}) is Empty'

                field = Field(name_value)
                field.index = col
                field.field_type = FieldType(type_cell.value)

                if ElemType.Unknown == field.field_type.elem_type:
                    return False, f'field element type at ({self._type_row}, {col}) is Known'

                tag_cell = sheet.cell(self._tag_row, col)
                field.tag = Tag.from_str(tag_cell.value)
                header.add_field(field)

        return True, header

    def _parse_rows(self, sheet, table):
        fields = table.header.get_fields()
        for row in range(self._content_start_row, sheet.nrows):
            row_content = []
            for field in fields:
                content_cell = sheet.cell(row, field.index)
                rs, value, err = field.to_value(content_cell.value)

                if not rs:
                    print(f'{table.xls} => {table.name}, ({row},{field.index}) to_value error : {err}')

                row_content.append(value)

            table.add_row(row_content)
