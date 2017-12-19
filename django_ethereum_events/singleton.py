class Singleton(type):
    """Simple singleton implementation."""

    _instances = {}

    def __call__(cls, *args, **kwargs):   # noqa: N805
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
