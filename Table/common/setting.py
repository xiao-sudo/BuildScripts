from .tag import Tag


class TagFilterSetting:
    def __init__(self, target_tag: Tag, tag_filter=lambda target_tag, input_tag: True):
        self.target_tag = target_tag
        self.tag_filter = tag_filter

    def filter(self, tag):
        return self.tag_filter(self.target_tag, tag)
