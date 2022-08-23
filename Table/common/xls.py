import glob
import os.path
import re

from enum import IntEnum
from . import xlrd
from .table import Table, Header
from .data import DataType
from .field import Field
from .setting import TagFilterSetting
from .elem import ElemAnalyzer
from .cell_util import cell_str, cell_xls_coord_str
from .tag import Tag

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

    class FieldState(IntEnum):
        OK = 0,
        FieldTypeEmpty = 1,
        Error = 2

    def parse_one_sheet(self, xls_path, table_name):
        if not is_valid_xls_sheet(table_name):
            return [False, f'{table_name} is not a valid export table name']

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

    def parse_one_xls(self, xls_path) -> list:
        abs_xls = os.path.abspath(xls_path)
        book = xlrd.open_workbook(abs_xls)
        xls_tables = []
        for sheet in book.sheets():
            if is_valid_xls_sheet(sheet.name):
                rs, table_or_err = self.parse_xls_sheet(xls_path, sheet)
                xls_tables.append([rs, table_or_err])

        return xls_tables

    def parse_xls_sheet(self, xls_path, sheet):
        rs, header_or_err = self._parse_header(sheet)

        if rs:
            if len(header_or_err.get_fields()) > 0:
                tab = Table(sheet.name, xls_path)
                tab.set_header(header_or_err)
                rs, body_or_err = self._parse_body(sheet, tab.header.get_fields())

                if rs:
                    tab.set_body(body_or_err)
                    return [True, tab]
                else:
                    return [False, f'{xls_path}, {body_or_err}']
            else:
                return [False, f'{xls_path}, {sheet.name} has no valid export field']
        else:
            return [False, f'{xls_path}, {header_or_err}']

    def _parse_header(self, sheet):
        if 0 == sheet.ncols:
            return [False, f'sheet {sheet.name} is empty']

        header = Header(sheet.name)

        # first col is primary field
        rs, primary_field_or_err = self._parse_field(0, sheet)

        if rs is not XlsParser.FieldState.OK:
            return [False, f'primary field error, {primary_field_or_err}']

        header.add_field(primary_field_or_err)

        for col in range(1, sheet.ncols):
            rs, field_or_err = self._parse_field(col, sheet)

            if rs is XlsParser.FieldState.OK:
                header.add_field(field_or_err)
            elif rs is XlsParser.FieldState.Error:
                return [False, field_or_err]

        return [True, header]

    def _parse_field(self, col, sheet):

        field_name_str = cell_str(sheet, self.FieldNameRow, col).strip()

        if field_name_str:
            tag_str = cell_str(sheet, self.TagRow, col).strip()

            if not tag_str:
                return [XlsParser.FieldState.Error, f'sheet {sheet.name} Tag at {cell_xls_coord_str(self.TagRow, col)} '
                                                    f'{tag_str} Tag is empty']

            tag = Tag.from_str(tag_str)
            if tag is None:
                return [XlsParser.FieldState.Error, f'sheet {sheet.name} Tag at {cell_xls_coord_str(self.TagRow, col)} '
                                                    f'{tag_str} is invalid']

            data_type_str = cell_str(sheet, self.DataTypeRow, col).strip()
            data_type = DataType.parse(data_type_str)

            if data_type is None:
                return [XlsParser.FieldState.Error,
                        f'sheet {sheet.name} Type at {cell_xls_coord_str(self.DataTypeRow, col)} '
                        f'{data_type_str} is invalid']

            field = Field(tag, field_name_str, col, data_type, 0 == col)
            return [XlsParser.FieldState.OK, field]
        else:
            return [XlsParser.FieldState.FieldTypeEmpty, 'Field Type is Empty']

    def _parse_body(self, sheet, fields):
        body = []
        for row in range(self.ContentStartRow, sheet.nrows):
            rs, body_row_or_err = self._parse_row(sheet, fields, row)
            if rs:
                body.append(body_row_or_err)
            else:
                return [False, f'sheet : {sheet.name}, {body_row_or_err}']

        return [True, body]

    @staticmethod
    def _parse_row(sheet, fields, row):
        body_row = []
        primary = fields[0]

        primary_str = cell_str(sheet, row, primary.sheet_col).strip()

        check = True
        if not primary_str:
            check = False

        rs, value_or_err = XlsParser._check_value(primary, primary_str, check)
        if rs:
            body_row.append(primary_str)
        else:
            return [False, f'{primary.field_name} at {cell_xls_coord_str(row, primary.sheet_col)} value {primary_str} '
                           f'is not {primary.data_type.to_client_csv_str()}']

        for field in fields[1:]:
            value_str = cell_str(sheet, row, field.sheet_col).strip()
            rs, value_or_err = XlsParser._check_value(field, value_str, check)

            if rs:
                body_row.append(value_or_err)
            else:
                return [False, f'{field.field_name} at {cell_xls_coord_str(row, field.sheet_col)} value {value_str} '
                               f'is not {field.data_type.to_client_csv_str()}']

        return [True, body_row]

    @staticmethod
    def _check_value(field, value_str, check):
        if check:
            checker = ElemAnalyzer.get_checker(field.data_type)
            return [checker(value_str), value_str]
        else:
            return [True, value_str]
