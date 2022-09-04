import os
import sys
import time
from multiprocessing import Pool
from multiprocessing import cpu_count

from . import xls
from .elem import TabPrimitive, TabArray, StrElemClass
from .log import debug_log
from .log import info_log
from .proto_type_assembler import ProtoTypeAssembler
from .row import Row, RowSemantic
from .table import Header, Table, TableDataUtil

tab_proto_prefix = 'Tab_'


class Stage:
    def __init__(self, name):
        self.name = name

    def execute(self, param):
        pass


class SingleXlsStage(Stage):
    def __init__(self):
        super().__init__('SingleXls')

    def execute(self, xls_path):
        if os.path.exists(xls_path):
            return [xls_path]
        else:
            debug_log(f'xls file {xls_path} is not exists')
            return []


class ParseSingleSheetStage(Stage):
    def __init__(self, sheet_name):
        super().__init__('ParseSingleXlsSheet')
        self.sheet_name = sheet_name

    def execute(self, single_xls_list: list):
        """
        parse a xls sheet
        :param single_xls_list: list only have single xls path
        :return: parsed single sheet table list, elem [bool, table_or_err]
        """
        if len(single_xls_list) > 0:
            parser = xls.XlsParser()
            xls_path = single_xls_list[0]
            rs, table_or_err = parser.parse_one_sheet(xls_path, self.sheet_name)
            if rs:
                return [[True, table_or_err]]
            else:
                debug_log(f'parse single sheet failed, {table_or_err}')
                return [[False, table_or_err]]
        else:
            return []


class CollectXlsStage(Stage):
    def __init__(self, xls_file_pattern):
        super().__init__('Collect Xls')
        self.xls_file_pattern = xls_file_pattern

    def execute(self, xls_dir):
        """
        collect all xls files with self.xls_file_patterns
        :param xls_dir: search dir
        :return: all filtered xls files
        """
        return xls.collect_xls_files(xls_dir, self.xls_file_pattern)


class ParseXlsStage(Stage):
    def __init__(self):
        super().__init__('ParseXlsArray')
        self._tables = []

    def execute(self, xls_list) -> list:
        """
        Parse xls file sheet to Table
        :param xls_list: input xls files' path
        :return: all Tables list of [bool, table_or_err]
        """
        start_time = time.time()
        parsed_tables = []

        xls_list_len = len(xls_list)

        if xls_list_len > 1:
            parsed_tables = self._multi_process_parse_xls_files(xls_list)
        elif 1 == xls_list_len:
            single_xls_path = xls_list[0]
            parsed_tables = self.parse_one_xls(single_xls_path)

        info_log(f'parse all xls elapse {time.time() - start_time} seconds')
        return parsed_tables

    def _multi_process_parse_xls_files(self, xls_list):
        thread_count = cpu_count()

        with Pool(thread_count) as pool:
            rs = pool.map(self.parse_one_xls, xls_list)

        parsed_tables = []

        for one_xls_result in rs:
            for sheet_result in one_xls_result:
                rs, table_or_err = sheet_result
                if rs:
                    parsed_tables.append(table_or_err)
                else:
                    info_log(table_or_err)

        return parsed_tables

    @staticmethod
    def parse_one_xls(xls_file_path: str) -> list:
        parser = xls.XlsParser()
        return parser.parse_one_xls(xls_file_path)


class CSVExportStage(Stage):
    def __init__(self, out_dir: str):
        """
        Export csv to target dir
        :param out_dir: target dir
        """
        super().__init__('CSVExport')
        self.out_dir = out_dir

    def execute(self, all_table_results):
        tables = []
        for table_rs in all_table_results:
            rs, table_or_err = table_rs
            if rs:
                tables.append(table_or_err)
                TableDataUtil.export_csv(f'{self.out_dir}/{table_or_err.name}.csv', table_or_err)
            else:
                debug_log(table_or_err)

        return tables


class TagFilterStage(Stage):
    def __init__(self, target_tag, tag_filter=lambda target_tag, input_tag: True):
        super().__init__('TagFilter')
        self.target_tag = target_tag
        self.tag_filter = tag_filter

    def execute(self, all_tables):
        filtered_tables = []
        for tab in all_tables:
            filtered_tab = self._filter_table(tab)
            if filtered_tab:
                filtered_tables.append(filtered_tab)

        return filtered_tables

    def _filter_table(self, source_tab):
        filtered_fields = self._filter_header_fields(source_tab)
        if len(filtered_fields):
            filtered_table = Table(source_tab.name, source_tab.xls)

            filtered_header = self._filter_header(filtered_fields, source_tab.header.name)
            filtered_body = self._filter_body(filtered_fields, source_tab)

            filtered_table.set_header(filtered_header)
            filtered_table.set_body(filtered_body)

            return filtered_table
        else:
            return None

    def _filter_header_fields(self, table):
        filtered_fields = []
        for field in table.header.get_fields():
            if self.tag_filter(self.target_tag, field.tag):
                filtered_fields.append(field)

        return filtered_fields

    @staticmethod
    def _filter_header(filtered_fields: list, name):
        new_header = Header(name)
        for field in filtered_fields:
            new_header.add_field(field)

        return new_header

    @staticmethod
    def _filter_body(filtered_fields: list, table: Table):
        filtered_body = []
        for row in table.body:
            if RowSemantic.DesignSpec == row.semantic:
                continue

            filtered_row = Row()
            for field in filtered_fields:
                csv_value = row.content[field.field_index]
                parsed_value = row.values[field.field_index]
                filtered_row.add_csv(csv_value)
                filtered_row.add_value(parsed_value)

            filtered_body.append(filtered_row)

        return filtered_body


class ParseProtoStage(Stage):
    proto_template = 'syntax = "proto3";\n' \
                     '{}' \
                     '\n' \
                     'message Row_{} {{\n' \
                     '{}' \
                     '}}\n' \
                     '\n' \
                     'message Tab_{} {{\n' \
                     '\trepeated Row_{} rows = 1;\n' \
                     '}}\n'

    def __init__(self, proto_dir):
        super().__init__('Parse Proto')
        self.proto_dir = proto_dir

    def execute(self, filtered_tables):
        assembler = ProtoTypeAssembler()
        for tab in filtered_tables:
            header = tab.header
            proto_body = []
            index = 1
            import_message_set = set()
            for field in header.get_fields():
                import_message_type, proto_field_str = assembler.assemble(field.data_type)

                if import_message_type and import_message_type not in import_message_set:
                    import_message_set.add(import_message_type)

                proto_body.append(f'\t{proto_field_str} {field.field_name} = {index};\n')
                index += 1

            import_message_text = '\n'
            for import_message_type in import_message_set:
                message = assembler.builtin_repeated_messages[import_message_type]
                import_message_text += f'{message}\n'

            row_message = ''
            for proto_field in proto_body:
                row_message += f'{proto_field}'

            with open(f'{self.proto_dir}/{tab_proto_prefix}{header.name}.proto', 'w') as proto_file:
                proto_file.write(self._format_proto(header.name, import_message_text, row_message))

        return filtered_tables

    def _format_proto(self, tab_name, import_proto, fields):
        return self.proto_template.format(import_proto, tab_name, fields, tab_name, tab_name)


class ProtoPythonGenStage(Stage):
    def __init__(self, proto_dir, proto_exe, proto_python_dir, pb_dir):
        super(ProtoPythonGenStage, self).__init__('ProtoPythonGen')
        self.proto_dir = proto_dir
        self.proto_exe = proto_exe
        self.proto_python_dir = proto_python_dir
        self.pb_dir = pb_dir

    def execute(self, filtered_tables):
        for tab in filtered_tables:
            proto_file = f'{self.proto_dir}/{tab_proto_prefix}{tab.header.name}.proto'
            if os.path.exists(proto_file):
                cmd = f'{self.proto_exe} {proto_file} --proto_path={self.proto_dir} ' \
                      f'--python_out={self.proto_python_dir} ' \
                      f'--descriptor_set_out={self.pb_dir}/{tab_proto_prefix}{tab.header.name}.pb'

                os.system(cmd)
            else:
                debug_log(f'{proto_file} not exists')
        return filtered_tables


class ParseBytesStage(Stage):
    def __init__(self, bytes_dir, proto_python_dir):
        super(ParseBytesStage, self).__init__('ParseProtoBytes')
        self.bytes_dir = bytes_dir
        self.proto_python_dir = proto_python_dir

    def execute(self, filtered_tables):
        # insert import path
        sys.path.insert(0, self.proto_python_dir)
        for tab in filtered_tables:
            header = tab.header
            # import protobuf py
            module_name = f'{tab_proto_prefix}{header.name}_pb2'
            module = __import__(module_name, locals(), globals())

            rs = {}
            cmd = f'{header.name}_message = module.{tab_proto_prefix}{header.name}()\n' \
                  f'rows = {header.name}_message.rows\n' \
                  f'self._fill_table_data(rows, tab, header)\n' \
                  f'rs[\'msg\'] = {header.name}_message\n'

            try:
                exec(cmd)
                with open(f'{self.bytes_dir}/{header.name}.bytes', 'wb') as bytes_file:
                    bytes_file.write(rs['msg'].SerializeToString())

            except Exception as err:
                debug_log(f'Xls : {tab.xls}, sheet : {tab.name}, {str(err)}')

    @staticmethod
    def _import(module):
        return __import__(module, locals(), globals())

    @staticmethod
    def _fill_table_data(rows, table: Table, header: Header):
        for tab_row in table.body:
            # for exec cmd
            data_row = rows.add()
            # content = tab_row.content
            values = tab_row.values
            index = 0
            for field in header.get_fields():
                if isinstance(field.data_type.organization, TabPrimitive):
                    if isinstance(field.data_type.elem_type, StrElemClass):
                        cmd = f'data_row.{field.field_name} = "{values[index]}"\n'
                    else:  # int
                        cmd = f'data_row.{field.field_name} = {values[index]}\n'
                elif isinstance(field.data_type.organization, TabArray):
                    cmd = f'data_row.{field.field_name}.extend({values[index]})\n'
                else:
                    cmd = ''
                    arr_2d = values[index]
                    for arr in arr_2d:
                        cmd += f'arr_2d_row = data_row.{field.field_name}.add()\n' \
                               f'arr_2d_row.arr_row.extend({arr})\n'

                index += 1
                exec(cmd)


class GenProtoStage(Stage):
    def __init__(self, pb_dir):
        super().__init__('Gen Proto')
        self.pb_dir = pb_dir

    def execute(self, proto_gen_tables):
        for table in proto_gen_tables:
            print(f'---{table.name}---')
            header = table.header
            for field in header.get_fields():
                print(f'{field.data_type.to_client_csv_str()}')


def _format_print_table(table):
    csv_info = TableDataUtil.to_csv(table)
    info_log(f'Table ({table.xls} => {table.name})')
    for row in csv_info:
        info_log(f'\t{row}')


class PrintParsedResultTableStage(Stage):
    def __init__(self):
        super().__init__('PrintParsedResultTable')

    def execute(self, parsed_tables):
        for parsed_tab in parsed_tables:
            rs, tab_or_err = parsed_tab
            if rs:
                _format_print_table(tab_or_err)
            else:
                info_log(tab_or_err)

        return parsed_tables


class PrintTableStage(Stage):
    def __init__(self):
        super().__init__('PrintTable')

    def execute(self, all_tables):
        for t in all_tables:
            _format_print_table(t)
