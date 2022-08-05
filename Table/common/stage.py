import time

from . import xls
from multiprocessing import cpu_count
from multiprocessing import Pool


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

    def execute(self, xls_list):
        """
        Parse xls file sheet to Table
        :param xls_list: input xls files' path
        :return: all Tables
        """
        start_time = time.time()
        self._multi_thread_parse_xls_files(xls_list)
        # self._single_thread_parse_xls_files(xls_list)
        print(f'parse all xls elapse {time.time() - start_time} seconds')
        return self._tables

    def _multi_thread_parse_xls_files(self, xls_list):
        thread_count = cpu_count()

        with Pool(thread_count) as pool:
            result_tables = pool.map(ParseXlsStage.parse_table, xls_list)

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


class PrintStage(Stage):
    def execute(self, all_tables):
        for t in all_tables:
            print(f'table : {t.xls} => {t.name}')
            header = t.header
            for field in header.get_fields():
                print(field)
