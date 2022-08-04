import glob
import os.path
import re
from . import xlrd
from .table import Table, Header, ObjectType, ElemType, FieldType


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

    def __init__(self):
        self.tables = []

    def parse(self, xls_path):
        abs_xls = os.path.abspath(xls_path)
        book = xlrd.open_workbook(abs_xls)
        for sheet in book.sheets():
            if is_valid_xls_sheet(sheet.name):
                tab = Table(sheet.name)
                self.tables.append(f"{xls_path}->{sheet.name}")

    def _parse_header(self, sheet):
        pass

    def _parse_rows(self, sheet):
        pass
