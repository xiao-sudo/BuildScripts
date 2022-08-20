from .converter import TextConverter
from .elem import ElemClass, ElemOrganization, ElemClassParser, ElemOrganizationParser
import re


class DataType(TextConverter):
    def __init__(self, elem_type: ElemClass, organization: ElemOrganization):
        self.elem_type = elem_type
        self.organization = organization

    def __str__(self):
        return self.to_client_csv_str()

    def to_client_csv_str(self) -> str:
        return f'{self.elem_type.to_client_csv_str()}{self.organization.to_client_csv_str()}'

    def to_server_csv_str(self) -> str:
        return f'{self.elem_type.to_server_csv_str()}{self.organization.to_server_csv_str()}'

    def to_proto_str(self) -> str:
        return f'{self.organization.to_proto_str()} {self.elem_type.to_proto_str()}'

    def check_text(self, text: str):
        pass

    @staticmethod
    def parse(excel_raw_type_str):
        matches = re.search(r"^([a-zA-Z]+)((\[])*)$", excel_raw_type_str)
        elem_type_str = matches[1]
        organization_str = matches[2]

        elem_type = ElemClassParser.parse(elem_type_str)
        organization = ElemOrganizationParser.parse(organization_str)

        if elem_type is None or organization is None:
            return None
        else:
            return DataType(elem_type, organization)
