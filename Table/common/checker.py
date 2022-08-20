from typing import Tuple

OrganizationTextCheckResult = Tuple[bool, list]
ElemTextCheckResult = Tuple[bool, str]


class OrganizationTextChecker:
    def organization_check_text(self, text: str) -> OrganizationTextCheckResult:
        """
        check text
        :param text:
        :return: [check_result:bool, [remain_value_text_to_check:str]]
        """
        pass


class ElemTextChecker:
    def elem_check_text(self, text_list: list) -> ElemTextCheckResult:
        """
        check text list
        :param text_list:
        :return: [bool, err_msg]
        """
        pass
