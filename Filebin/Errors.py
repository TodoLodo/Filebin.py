class InvalidArchiveType(Exception):
    def __init__(self, _type:str):
        self.message = f"Invalid Archive Type, {_type!r}"
        super().__init__(self.message)
