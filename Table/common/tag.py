from enum import IntEnum


class Tag(IntEnum):
    Client = 1
    Server = 2
    CS = 3

    def to_str(self):
        return tag_str_dict[self]

    @staticmethod
    def from_str(tag_str: str):
        return str_tag_dict.get(tag_str.lower(), None)


tag_str_dict = {
    Tag.Client: 'c',
    Tag.Server: 's',
    Tag.CS: 'cs'
}

str_tag_dict = {
    'c': Tag.Client,
    's': Tag.Server,
    'cs': Tag.CS,
    'all': Tag.CS
}


def is_client_compatible_tag(tag: Tag):
    return Tag.Client == tag or Tag.CS == tag


def is_server_compatible_tag(tag: Tag):
    return Tag.Server == tag or Tag.CS == tag


def is_client_only_tag(tag: Tag):
    return Tag.Client == tag


def is_server_only_tag(tag: Tag):
    return Tag.Server == tag
