import os.path
import time

from . import xls
from .setting import TagFilterSetting
from .table import Table, Tag, TableDataUtil
from multiprocessing import cpu_count
from multiprocessing import Pool

from typing import List
from typing import Dict

TagFilterSettingList = List[TagFilterSetting]
TableList = List[Table]
TableDict = Dict[Tag, TableList]


class Stage:
    def __init__(self, name):
        self.name = name

    def execute(self, param):
        pass


class CollectXlsStage(Stage):
    def __init__(self, name, xls_file_pattern):
        super().__init__(name)
        self.xls_file_pattern = xls_file_pattern

    def execute(self, xls_dir):
        """
        collect all xls files with self.xls_file_patterns
        :param xls_dir: search dir
        :return: all filtered xls files
        """
        return xls.collect_xls_files(xls_dir, self.xls_file_pattern)


class ParseXlsStage(Stage):
    def __init__(self, name):
        super().__init__(name)
        self._tables = []

    def execute(self, xls_list) -> TableList:
        """
        Parse xls file sheet to Table
        :param xls_list: input xls files' path
        :return: all Tables
        """
        start_time = time.time()
        self._multi_process_parse_xls_files(xls_list)
        # self._single_thread_parse_xls_files(xls_list)
        print(f'parse all xls elapse {time.time() - start_time} seconds')
        return self._tables

    def _multi_process_parse_xls_files(self, xls_list):
        thread_count = cpu_count()

        with Pool(thread_count) as pool:
            result_tables = pool.map(self.parse_table, xls_list)

        for tables in result_tables:
            if tables:
                self._tables.extend(tables)

    def _single_thread_parse_xls_files(self, xls_list):
        parser = xls.XlsParser()
        for xls_path in xls_list:
            parser.parse(xls_path)

        self._tables = parser.tables

    @staticmethod
    def parse_table(xls_file_path: str):
        parser = xls.XlsParser()
        parser.parse(xls_file_path)

        if parser.tables:
            return parser.tables
        else:
            return []


class FilterStage(Stage):
    def __init__(self, name, tag_filter_settings: TagFilterSettingList):
        super().__init__(name)
        self.tag_filter_settings = tag_filter_settings

    def execute(self, all_parsed_tables: TableList) -> TableDict:
        filtered_tables = TableDict()

        for setting in self.tag_filter_settings:
            filtered_tables[setting.target_tag] = TableList()

        for table in all_parsed_tables:
            for setting in self.tag_filter_settings:
                filtered_tab = self._filter_table(table, setting)
                if filtered_tab is not None:
                    filtered_tables[setting.target_tag].append(filtered_tab)

        return filtered_tables

    def _filter_table(self, table: Table, setting: TagFilterSetting) -> Table:
        pass


class CSVExportSetting:
    def __init__(self, name: str, export_dir: str, target_tag, tag_filter: lambda target_tag, input_tag: True):
        self.name = name
        self.export_dir = export_dir
        self.target_tag = target_tag
        self.tag_filter = tag_filter

    def filter_tag(self, tag):
        return self.tag_filter(self.target_tag, tag)


class CSVExportStage(Stage):
    def __init__(self, name: str, out_dir: str):
        """
        Export csv with different settings
        :param name:
        """
        super().__init__(name)
        self.out_dir = out_dir

    def execute(self, all_tables):
        for table in all_tables:
            data = TableDataUtil.to_csv(table)
            for row in data:
                print(row)


class GenProtoStage(Stage):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, exported_tables):
        for tag in exported_tables:
            tables = exported_tables[tag]
            for table in tables:
                print(f'---{table.name}---')
                header = table.header
                for field in header.get_fields():
                    print(f'{field.data_type.to_client_csv_str()}')


class PrintStage(Stage):
    def execute(self, all_tables):
        for t in all_tables:
            print(f'table : {t.xls} => {t.name}')
            header = t.header
            for field in header.get_fields():
                print(field)
