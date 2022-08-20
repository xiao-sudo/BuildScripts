import glob
import os.path
import re
from . import xlrd
from .table import Table, Tag, Header
from .data import DataType
from .field import Field
from .setting import TagFilterSetting

from typing import List
from typing import Dict

TagFilterSettingList = List[TagFilterSetting]
TableList = List[Table]
TableDict = Dict[Tag, TableList]


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
    TagRow = 2
    DataTypeRow = 3
    FieldNameRow = 4
    ContentStartRow = 8

    def __init__(self):
        self.tables = []

    def parse_one_table(self, xls_path, table_name):
        abs_xls = os.path.abspath(xls_path)
        rs = True
        table_or_err = None

        try:
            book = xlrd.open_workbook(abs_xls)
            sheet = book.sheet_by_name(table_name)
            rs, table_or_err = self.parse_xls_sheet(sheet)
        except Exception as err:
            rs = False
            table_or_err = err
        finally:
            return rs, table_or_err

    def parse(self, xls_path) -> TableList:

        abs_xls = os.path.abspath(xls_path)
        book = xlrd.open_workbook(abs_xls)
        for sheet in book.sheets():
            if is_valid_xls_sheet(sheet.name):
                rs, header_or_err = self._parse_header(sheet)

                if rs:
                    tab = Table(sheet.name, xls_path)
                    tab.set_header(header_or_err)
                    self.tables.append(tab)
                else:
                    print(f'{xls_path} : {sheet.name} parse error => {header_or_err}')

        return self.tables

    def parse_xls_sheet(self, sheet):
        if is_valid_xls_sheet(sheet.name):
            rs, header_or_err = self._parse_header(sheet)
            # TODO : parse header and parse Body

        else:
            return [False, f'{sheet.name} is not a valid export sheet name']

    def _parse_header(self, sheet):
        header = Header(sheet.name)
        curr_index = 0
        for col in range(sheet.ncols):

            tag_cell = sheet.cell(self.TagRow, col)
            tag_str = tag_cell.value.strip()

            if '' != tag_str:
                name_cell = sheet.cell(self.FieldNameRow, col)
                name_value = name_cell.value.strip()

                if '' == name_value:
                    return False, f'field name at ({self.FieldNameRow}, {col}) is Empty'

                type_cell = sheet.cell(self.DataTypeRow, col)
                type_str = type_cell.value.strip()
                data_type = DataType.parse(type_str)

                if data_type is None:
                    return False, f'type {type_str} is invalid'

                tag = Tag.from_str(tag_str)

                if tag is None:
                    return False, f'tag {tag} is invalid'

                field = Field(tag, name_value, col, curr_index, data_type)
                curr_index += 1

                header.add_field(field)

        return True, header

    def _parse_rows(self, sheet, table):
        fields = table.header.get_fields()
        for row in range(self.ContentStartRow, sheet.nrows):
            row_content = []
            for field in fields:
                content_cell = sheet.cell(row, field.sheet_col)
                rs, value, err = field.parse_text_to_value(content_cell.value)

                if not rs:
                    print(f'{table.xls} => {table.name}, ({row},{field.col}) to_value error : {err}')

                row_content.append(value)

            table.add_row(row_content)
