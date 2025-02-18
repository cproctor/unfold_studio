class BaseChoice:
    @classmethod
    def choices(cls):
        return [(value, value) for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(value)]