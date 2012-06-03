# vim: set fileencoding=utf-8
class UnknownCategoryError(Exception):
    def __init__(self, cat):
        self.category = cat
