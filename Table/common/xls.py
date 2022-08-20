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
            rs, table_or_err = self.parse_xls_sheet(xls_path, sheet)
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

    def parse_xls_sheet(self, xls_path, sheet):
        if is_valid_xls_sheet(sheet.name):
            rs, header_or_err = self._parse_header(sheet)

            if rs:
                if len(header_or_err.get_fields()) > 0:
                    tab = Table(sheet.name, xls_path)
                    tab.set_header(header_or_err)
                    # TODO : parse body
                else:
                    return [False, f'{sheet.name} has no valid export field']
            else:
                return [False, header_or_err]

        else:
            return [False, f'{sheet.name} is not a valid export sheet name']

    def _parse_header(self, sheet):

        curr_index = 0
        header = Header(sheet.name)

        for col in range(sheet.ncols):
            field_name_str = sheet.cell(self.FieldNameRow, col).value.strip()

            if field_name_str:
                tag_str = sheet.cell(self.TagRow, col).value.strip()

                if not tag_str:
                    return [False, f'Column {col} Tag is empty']

                tag = Tag.from_str(tag_str)
                if tag is None:
                    return [False, f'Tag {tag_str} is invalid']

                data_type_str = sheet.cell(self.DataTypeRow, col).value.strip()
                data_type = DataType.parse(data_type_str)

                if data_type is None:
                    return [False, f'Type {data_type_str} is invalid']

                field = Field(tag, field_name_str, col, curr_index, data_type, 0 == curr_index)
                header.add_field(field)
                curr_index += 1

        return [True, header]

    # def _parse_rows(self, sheet, table):
    # fields = table.header.get_fields()
    # for row in range(self.ContentStartRow, sheet.nrows):
    #     row_content = []
    #     for field in fields:
    #         primary = field.primary
    #         content_str = sheet.cell(row, field.sheet_col).value.strip()
    #         rs = field.check_text(content_str)
    #
    #         if not rs:
    #             print(f'{table.xls} => {table.name}, ({row},{field.col}) to_value error : {err}')
    #
    #         row_content.append(content_str)
    #
    #     table.add_row(row_content)

    def _parse_body(self, sheet, fields):
        pass
