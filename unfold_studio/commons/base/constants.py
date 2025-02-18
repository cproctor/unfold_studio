class BaseConstant:
    @classmethod
    def values(cls):
        return [v for k, v in vars(cls).items() if k.isupper() and not callable(v)]