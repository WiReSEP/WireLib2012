# vim: set fileencoding=utf-8
class UnknownCategoryError(Exception):
    def __init__(self, cat):
        self.category = cat

class DuplicateKeyError(Exception):
    def __init__(self, message):
        self.reason = message

class LendingError(Exception):
    pass
