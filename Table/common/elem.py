import re
from enum import IntEnum

from .converter import TypeToCSVStr, TypeToProtoStr
from .log import debug_log
from .proto_type_literals import INT, STR

TAB_INT_IDENTIFIER = 'INT'
TAB_STRING_IDENTIFIER = 'STRING'

TAB_ARRAY_IDENTIFIER = '[]'
TAB_2D_ARRAY_IDENTIFIER = '[][]'
TAB_PRIMITIVE_IDENTIFIER = ''


class ElemClass(TypeToCSVStr, TypeToProtoStr):

    @staticmethod
    def to_int_identifier():
        return TAB_INT_IDENTIFIER

    @staticmethod
    def zero_value():
        return 0


class IntElemClass(ElemClass):
    def to_csv_str(self):
        return ElemClass.to_int_identifier()

    def to_proto_str(self):
        return INT


class StrElemClass(ElemClass):
    def to_csv_str(self):
        return TAB_STRING_IDENTIFIER

    def to_proto_str(self) -> str:
        return STR


class ElemClassParser:
    @staticmethod
    def parse(elem_type_str: str):
        return {
            TAB_INT_IDENTIFIER: IntElemClass,
            TAB_STRING_IDENTIFIER: StrElemClass,
        }.get(elem_type_str, lambda: None)()


class ElemOrganization(TypeToCSVStr, TypeToProtoStr):
    pass


class TabPrimitive(ElemOrganization):
    def to_csv_str(self) -> str:
        return ''

    def to_proto_str(self) -> str:
        return ''


class TabArray(ElemOrganization):
    def to_csv_str(self) -> str:
        return '[]'

    def to_proto_str(self) -> str:
        return 'repeated '


class Tab2DArray(ElemOrganization):
    def to_csv_str(self) -> str:
        return '[][]'

    def to_proto_str(self) -> str:
        return 'repeated '


class ElemOrganizationParser:
    @staticmethod
    def parse(organization_str: str):
        return {
            TAB_PRIMITIVE_IDENTIFIER: TabPrimitive,
            TAB_ARRAY_IDENTIFIER: TabArray,
            TAB_2D_ARRAY_IDENTIFIER: Tab2DArray
        }.get(organization_str, lambda: None)()


class ElemAnalyzer:
    EmptyStrHolder = 'Nan'

    # +-0 | +-[1-9]\d*
    IntPattern = r'[+-]?(0|[1-9]\d*)'
    # [(Int(,Int)*)?]
    IntArrayPattern = fr'\[\s*(\s*{IntPattern}\s*(,\s*{IntPattern}\s*)*\s*)?]'
    # [(IntArray(,IntArray)*)?]
    Int2DArrayPattern = fr'\[(\s*{IntArrayPattern}\s*(,\s*{IntArrayPattern}\s*)*\s*)?]'
    # separate array, use , between ] and [
    ArraySepPattern = r'(?<=\])\s*,\s*(?=\[)'
    QuotedStr = r'\".*"'
    # [(quoted_str(,quoted_str)*)*]
    QuotedStrArrayPattern = rf'\[\s*(\s*{QuotedStr}\s*(,\s*{QuotedStr})*\s*)?]'
    QuotedStr2DArrayPattern = rf'\[\s*({QuotedStrArrayPattern}\s*(,\s*{QuotedStrArrayPattern})*\s*)?]'
    # use , separate str array; , must between prev right \" and next left \"
    QuotedStrSepPattern = r"(?<=\")\s*,\s*(?=\")"

    @staticmethod
    def parse_int_array(text: str):
        m = re.match(f'^{ElemAnalyzer.IntArrayPattern}$', text)
        if m is not None:
            rs, parsed_values_or_err = ElemAnalyzer._parse_int_array_impl(m.group(1))
            if rs:
                return [True, text, parsed_values_or_err]
            else:
                return [False, parsed_values_or_err, '']
        else:
            return [False, f'{text} is not int array', '']

    @staticmethod
    def _parse_int_array_impl(text: str):
        # empty array
        if text is None:
            return [True, []]

        segments = text.split(',')
        ints = []
        for seg in segments:
            rs, int_or_err = ElemAnalyzer._parse_int_impl(seg)
            if rs:
                ints.append(int_or_err)
            else:
                return [False, f'{int_or_err} in {text}']

        return [True, ints]

    @staticmethod
    def parse_str_array(text: str):
        m = re.match(f'^{ElemAnalyzer.QuotedStrArrayPattern}$', text)
        if m is not None:
            rs, parsed_values_or_err = ElemAnalyzer._parse_str_array_impl(m.group(1))
            if rs:
                return [True, text, parsed_values_or_err]
            else:
                return [False, parsed_values_or_err, '']
        else:
            return [False, f'{text} is not string array', '']

    @staticmethod
    def _parse_str_array_impl(text: str):
        if text is None:
            return [True, []]

        segments = re.split(ElemAnalyzer.QuotedStrSepPattern, text)
        parsed_values = []
        for seg in segments:
            rs, ori_text_or_err, parsed_text = ElemAnalyzer._parse_quoted_str(seg)
            if rs:
                parsed_values.append(parsed_text)
            else:
                return [False, f'{ori_text_or_err} in {text}']

        return [True, parsed_values]

    @staticmethod
    def _parse_quoted_str(text: str):
        m = re.match(rf'^"(.*)"$', text.strip())
        if m is not None:
            rs, text, parsed_str = ElemAnalyzer.parse_str(m.group(1))
            if rs:
                return [True, text, parsed_str]
            else:
                return [False, text, '']

        return [False, f'{text} is not quoted str', '']

    @staticmethod
    def parse_int(text: str):
        m = re.match(rf'^{ElemAnalyzer.IntPattern}$', text)
        if m is not None:
            rs, int_or_err = ElemAnalyzer._parse_int_impl(text)
            if rs:
                return [True, text, int_or_err]
            else:
                return [False, int_or_err, '']
        else:
            return [False, f'{text} can not parse to int', '']

    @staticmethod
    def _parse_int_impl(text: str):
        try:
            int_value = int(text)
            return [True, int_value]
        except ValueError as err:
            return [False, f'{text} to int error, {err}']

    @staticmethod
    def parse_str(text: str):
        if re.match(r'^\s*$', text):
            return [False, f'{text} is empty string, use Nan', '']

        value_text = str(text)
        if ElemAnalyzer.EmptyStrHolder == text.strip():
            value_text = ''

        return [True, text, value_text]

    @staticmethod
    def parse_int_2d_array(text: str):
        m = re.match(rf'^{ElemAnalyzer.Int2DArrayPattern}$', text)
        if m is not None:
            rs, parsed_ints_or_err = ElemAnalyzer._parse_int_2d_array_impl(m.group(1))
            if rs:
                return [True, text, parsed_ints_or_err]
            else:
                return [False, parsed_ints_or_err, '']

        return [False, f'{text} is not int 2d array', '']

    @staticmethod
    def _parse_int_2d_array_impl(text: str):
        if text is None:
            return [True, []]

        arrays = re.split(ElemAnalyzer.ArraySepPattern, text)
        parsed_2d_arr = []
        for arr in arrays:
            rs, csv_arr_or_err, parsed_arr = ElemAnalyzer.parse_int_array(arr)
            if rs:
                parsed_2d_arr.append(parsed_arr)
            else:
                return [False, csv_arr_or_err]

        return [True, parsed_2d_arr]

    @staticmethod
    def parse_str_2d_array(text: str):
        m = re.match(rf'^{ElemAnalyzer.QuotedStr2DArrayPattern}$', text)
        if m is not None:
            rs, parsed_str_2d_arr_or_err = ElemAnalyzer._parse_str_2d_array_impl(m.group(1))
            if rs:
                return [True, text, parsed_str_2d_arr_or_err]
            else:
                return [False, parsed_str_2d_arr_or_err, '']

        return [False, f'{text} is not str 2d array', '']

    @staticmethod
    def _parse_str_2d_array_impl(text: str):
        if text is None:
            return [True, []]

        str_arrays = re.split(ElemAnalyzer.ArraySepPattern, text)
        parsed_2d_str_arr = []
        for str_array in str_arrays:
            rs, csv_arr_or_err, parsed_str_arr = ElemAnalyzer.parse_str_array(str_array)
            if rs:
                parsed_2d_str_arr.append(parsed_str_arr)
            else:
                return [False, csv_arr_or_err]

        return [True, parsed_2d_str_arr]

    # @staticmethod
    # def int_array_disassembler(text: str):
    #     m = re.match(ElemAnalyzer.IntArrayPattern, text)
    #     if m is not None:
    #         return [True, m.group(1).split(',')]
    #     else:
    #         return [False, f'{text} can not parsed to int[]']
    #
    # @staticmethod
    # def str_array_disassembler(text: str):
    #     m = re.match(ElemAnalyzer.QuotedStrArrayPattern, text)
    #     if m is not None:
    #         return [True, re.split("", m.group(1))]
    #     else:
    #         return [False, f'{text} can not parsed to string[]']

    class ElemType(IntEnum):
        Int = 0
        Str = 1
        IntArray = 2
        StrArray = 3
        Int2DArray = 4
        Str2DArray = 5

    Tools = {
        'checker': {
            ElemType.Int: lambda text: ElemAnalyzer.parse_int(text),
            ElemType.Str: lambda text: ElemAnalyzer.parse_str(text),
            ElemType.IntArray: lambda text: ElemAnalyzer.parse_int_array(text),
            ElemType.StrArray: lambda text: ElemAnalyzer.parse_str_array(text),
            ElemType.Int2DArray: lambda text: ElemAnalyzer.parse_int_2d_array(text),
            ElemType.Str2DArray: lambda text: ElemAnalyzer.parse_str_2d_array(text)
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
