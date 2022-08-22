import re
from enum import IntEnum

from .converter import TextConverter, DefaultValueConverter, TextToValueConverter

TAB_INT_IDENTIFIER = 'INT'
TAB_SINT_IDENTIFIER = 'SINT'
TAB_FIXED_IDENTIFIER = 'FIXED'
TAB_FLOAT_IDENTIFIER = 'FLOAT'
TAB_STRING_IDENTIFIER = 'STRING'
TAB_BOOL_IDENTIFIER = 'BOOL'

TAB_ARRAY_IDENTIFIER = '[]'
TAB_PRIMITIVE_IDENTIFIER = ''


class ElemClass(TextConverter, DefaultValueConverter, TextToValueConverter):
    def __str__(self):
        return self.to_client_csv_str()

    @staticmethod
    def to_int_identifier():
        return TAB_INT_IDENTIFIER

    @staticmethod
    def to_float_identifier():
        return TAB_FLOAT_IDENTIFIER

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


class SIntElemClass(ElemClass):
    def to_client_csv_str(self):
        return TAB_SINT_IDENTIFIER

    def to_server_csv_str(self):
        return ElemClass.to_int_identifier()

    def to_proto_str(self):
        return 'sint32'

    def default_value(self):
        return ElemClass.zero_value()


class FixedIntElemClass(ElemClass):
    def to_client_csv_str(self):
        return TAB_FIXED_IDENTIFIER

    def to_server_csv_str(self):
        return ElemClass.to_int_identifier()

    def to_proto_str(self):
        return 'fixed32'

    def default_value(self):
        return ElemClass.zero_value()


class FloatElemClass(ElemClass):
    def to_client_csv_str(self):
        return ElemClass.to_float_identifier()

    def to_server_csv_str(self):
        return ElemClass.to_float_identifier()

    def to_proto_str(self):
        return 'float'

    def default_value(self):
        ElemClass.zero_value()


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


class BoolElemClass(ElemClass):
    def to_client_csv_str(self):
        return TAB_BOOL_IDENTIFIER

    def to_server_csv_str(self):
        return TAB_BOOL_IDENTIFIER

    def to_proto_str(self):
        return 'bool'

    def default_value(self):
        return False


class ElemClassParser:
    @staticmethod
    def parse(elem_type_str: str):
        return {
            TAB_INT_IDENTIFIER: IntElemClass,
            TAB_SINT_IDENTIFIER: SIntElemClass,
            TAB_FIXED_IDENTIFIER: FixedIntElemClass,
            TAB_STRING_IDENTIFIER: StrElemClass,
            TAB_FLOAT_IDENTIFIER: FloatElemClass,
            TAB_BOOL_IDENTIFIER: BoolElemClass
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
            TAB_ARRAY_IDENTIFIER: TabArray
        }.get(organization_str, lambda: None)()


class ElemAnalyzer:
    # +-0 | +-[1-9]\d*
    IntPattern = r'[+-]?(0|[1-9]\d*)'
    # [(Int(,Int)*)*]
    IntArrayPattern = fr'^\[(\s*{IntPattern}\s*(,\s*{IntPattern}\s*)*\s*)?]$'
    QuotedStr = r'\".*"'
    # [(quoted_str(,quoted_str)*)*]
    QuotedStrArrayPattern = rf'^\[(\s*{QuotedStr}\s*(,\s*{QuotedStr})*\s*)?]$'
    # , must between " and "
    QuotedStrSepPattern = r"(?<=\")\s*,\s*(?=\")"

    @staticmethod
    def is_int_array(text: str):
        m = re.match(ElemAnalyzer.IntArrayPattern, text)
        return m is not None

    @staticmethod
    def is_str_array(text: str):
        m = re.match(ElemAnalyzer.QuotedStrArrayPattern, text)
        return m is not None

    @staticmethod
    def is_int(text: str):
        m = re.match(rf'^{ElemAnalyzer.IntPattern}$', text)
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
            ElemType.StrArray: lambda text: ElemAnalyzer.is_str_array(text)
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
            else:
                return ElemAnalyzer.ElemType.Str
        else:
            if isinstance(elem_class, IntElemClass):
                return ElemAnalyzer.ElemType.IntArray
            else:
                return ElemAnalyzer.ElemType.StrArray

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
