import re
from enum import IntEnum

from .converter import TextConverter, DefaultValueConverter, TextToValueConverter
from .log import debug_log

TAB_INT_IDENTIFIER = 'INT'
TAB_STRING_IDENTIFIER = 'STRING'

TAB_ARRAY_IDENTIFIER = '[]'
TAB_2D_ARRAY_IDENTIFIER = '[][]'
TAB_PRIMITIVE_IDENTIFIER = ''


class ElemClass(TextConverter, DefaultValueConverter, TextToValueConverter):
    def __str__(self):
        return self.to_client_csv_str()

    @staticmethod
    def to_int_identifier():
        return TAB_INT_IDENTIFIER

    @staticmethod
    def zero_value():
        return 0


class IntElemClass(ElemClass):
    def to_client_csv_str(self):
        return ElemClass.to_int_identifier()

    def to_server_csv_str(self):
        return ElemClass.to_int_identifier()

    def to_proto_str(self):
        return 'int32'

    def default_value(self):
        return ElemClass.zero_value()

    def parse_text_to_value(self, text):
        if '' == text:
            return False, 'int Value is empty'
        else:
            rs = False
            value_or_err = self.default_value()
            try:
                value_or_err = int(text)
            except ValueError as err:
                rs = False
                value_or_err = err
            finally:
                return rs, value_or_err


class StrElemClass(ElemClass):
    def to_client_csv_str(self):
        return TAB_STRING_IDENTIFIER

    def to_server_csv_str(self):
        return TAB_STRING_IDENTIFIER

    def to_proto_str(self):
        return 'string'

    def default_value(self):
        return ''

    def parse_text_to_value(self, text: str):
        if '' == text:
            return False, 'string value is empty'
        else:
            return True, text


class ElemClassParser:
    @staticmethod
    def parse(elem_type_str: str):
        return {
            TAB_INT_IDENTIFIER: IntElemClass,
            TAB_STRING_IDENTIFIER: StrElemClass,
        }.get(elem_type_str, lambda: None)()


class ElemOrganization(TextConverter):
    def __str__(self):
        return self.to_client_csv_str()


class TabPrimitive(ElemOrganization):
    def to_client_csv_str(self) -> str:
        return ''

    def to_server_csv_str(self) -> str:
        return ''

    def to_proto_str(self) -> str:
        return ''


class TabArray(ElemOrganization):
    def to_client_csv_str(self) -> str:
        return '[]'

    def to_server_csv_str(self) -> str:
        return '[]'

    def to_proto_str(self) -> str:
        return 'repeated'


class Tab2DArray(ElemOrganization):
    def to_client_csv_str(self) -> str:
        return '[][]'

    def to_server_csv_str(self) -> str:
        return '[][]'

    def to_proto_str(self) -> str:
        return 'repeated'


class ElemOrganizationParser:
    @staticmethod
    def parse(organization_str: str):
        return {
            TAB_PRIMITIVE_IDENTIFIER: TabPrimitive,
            TAB_ARRAY_IDENTIFIER: TabArray,
            TAB_2D_ARRAY_IDENTIFIER: Tab2DArray
        }.get(organization_str, lambda: None)()


class ElemAnalyzer:
    # +-0 | +-[1-9]\d*
    IntPattern = r'[+-]?(0|[1-9]\d*)'
    # [(Int(,Int)*)?]
    IntArrayPattern = fr'\[\s*(\s*{IntPattern}\s*(,\s*{IntPattern}\s*)*\s*)?]'
    # [()]
    Int2DArrayPattern = fr'\[(\s*{IntArrayPattern}\s*(,\s*{IntArrayPattern}\s*)*\s*)?]'
    QuotedStr = r'\".*"'
    # [(quoted_str(,quoted_str)*)*]
    QuotedStrArrayPattern = rf'\[\s*(\s*{QuotedStr}\s*(,\s*{QuotedStr})*\s*)?]'
    QuotedStr2DArrayPattern = rf'\[\s*({QuotedStrArrayPattern}\s*(,\s*{QuotedStrArrayPattern})*\s*)?]'
    # use , separate str array; , must between prev right \" and next left \"
    QuotedStrSepPattern = r"(?<=\")\s*,\s*(?=\")"

    @staticmethod
    def is_int_array(text: str):
        m = re.match(f'^{ElemAnalyzer.IntArrayPattern}$', text)
        return m is not None

    @staticmethod
    def is_str_array(text: str):
        m = re.match(f'^{ElemAnalyzer.QuotedStrArrayPattern}$', text)
        return m is not None

    @staticmethod
    def is_int(text: str):
        m = re.match(rf'^{ElemAnalyzer.IntPattern}$', text)
        return m is not None

    @staticmethod
    def is_int_2d_array(text: str):
        m = re.match(rf'^{ElemAnalyzer.Int2DArrayPattern}$', text)
        return m is not None

    @staticmethod
    def is_str_2d_array(text: str):
        m = re.match(rf'^{ElemAnalyzer.QuotedStr2DArrayPattern}$', text)
        return m is not None

    @staticmethod
    def pass_to_elem_checker(text: str):
        return [True, [text]]

    @staticmethod
    def int_array_disassembler(text: str):
        m = re.match(ElemAnalyzer.IntArrayPattern, text)
        if m is not None:
            return [True, m.group(1).split(',')]
        else:
            return [False, f'{text} can not parsed to int[]']

    @staticmethod
    def str_array_disassembler(text: str):
        m = re.match(ElemAnalyzer.QuotedStrArrayPattern, text)
        if m is not None:
            return [True, re.split("", m.group(1))]
        else:
            return [False, f'{text} can not parsed to string[]']

    class ElemType(IntEnum):
        Int = 0
        Str = 1
        IntArray = 2
        StrArray = 3
        Int2DArray = 4
        Str2DArray = 5

    Tools = {
        'checker': {
            ElemType.Int: lambda text: ElemAnalyzer.is_int(text),
            ElemType.Str: lambda text: True,
            ElemType.IntArray: lambda text: ElemAnalyzer.is_int_array(text),
            ElemType.StrArray: lambda text: ElemAnalyzer.is_str_array(text),
            ElemType.Int2DArray: lambda text: ElemAnalyzer.is_int_2d_array(text),
            ElemType.Str2DArray: lambda text: ElemAnalyzer.is_str_2d_array(text)
        },
        'disassembler': {
            ElemType.Int: pass_to_elem_checker,
            ElemType.Str: pass_to_elem_checker,
            ElemType.IntArray: int_array_disassembler,
            ElemType.StrArray: str_array_disassembler
        }
    }

    @staticmethod
    def to_elem_type(elem_class: ElemClass, elem_organ: ElemOrganization):
        if isinstance(elem_organ, TabPrimitive):
            if isinstance(elem_class, IntElemClass):
                return ElemAnalyzer.ElemType.Int
            elif isinstance(elem_class, StrElemClass):
                return ElemAnalyzer.ElemType.Str
            else:
                debug_log(f'Unknown Primitive Type {elem_class}')
                return None
        elif isinstance(elem_organ, TabArray):
            if isinstance(elem_class, IntElemClass):
                return ElemAnalyzer.ElemType.IntArray
            elif isinstance(elem_class, StrElemClass):
                return ElemAnalyzer.ElemType.StrArray
            else:
                debug_log(f'Unsupported Primitive Type {elem_class} in Array')
                return None
        elif isinstance(elem_organ, Tab2DArray):
            if isinstance(elem_class, IntElemClass):
                return ElemAnalyzer.ElemType.Int2DArray
            elif isinstance(elem_class, StrElemClass):
                return ElemAnalyzer.ElemType.Str2DArray
            else:
                debug_log(f'Unsupported Primitive Type {elem_class} in 2D Array')

        else:
            debug_log(f'Unknown Organization Type {elem_organ}')
            return None

    @staticmethod
    def get_disassembler(data_type):
        elem_type = ElemAnalyzer.to_elem_type(data_type.elem_type, data_type.organization)

        if elem_type is not None:
            return ElemAnalyzer.Tools.get('disassembler').get(elem_type)

        return None

    @staticmethod
    def get_checker(data_type):
        elem_type = ElemAnalyzer.to_elem_type(data_type.elem_type, data_type.organization)

        if elem_type is not None:
            return ElemAnalyzer.Tools.get('checker').get(elem_type)

        return None
