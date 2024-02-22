import asyncio
import functools


def log_exception(logger):
    """Декоратор логирования ошибок."""
    def log_decorator(func_: callable):
        @functools.wraps(func_)
        async def wrapper(*args, **kwargs):
            try:
                return await func_(*args, **kwargs)
            except Exception as e:
                logger.error(f'{func_.__name__} ({args ,kwargs}) : {e}')
        return wrapper
    return log_decorator


def log_exceptions_db_methods(logger):
    """Обернуть в декоратор логирования ошибок все методы класса."""
    def log_decorator_cls(cls_):
        for attr_name, attr_value in cls_.__dict__.items():
            if asyncio.iscoroutinefunction(attr_value):
                setattr(cls_, attr_name, log_exception(logger)(attr_value))
        return cls_
    return log_decorator_cls
