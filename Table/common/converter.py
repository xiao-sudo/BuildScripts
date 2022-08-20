class TextConverter:
    def to_client_csv_str(self) -> str:
        """
        convert to client csv str
        :return: str
        """
        pass

    def to_server_csv_str(self) -> str:
        """
        convert to server csv str
        :return:
        """
        pass

    def to_proto_str(self) -> str:
        """
        convert to protocol buffer str
        :return:
        """
        pass


class DefaultValueConverter:
    def default_value(self):
        pass


class TextToValueConverter:
    def parse_text_to_value(self, text: str):
        """
        parse text to value
        :param text: input text
        :return: [bool, value_or_err]
        """
        pass
