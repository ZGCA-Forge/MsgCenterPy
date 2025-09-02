import functools
import warnings
from typing import Any, Callable


def experimental(
    reason: str = "This API is experimental and may change or be removed in future.",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    装饰器：标记函数为实验性。
    调用时会发出 RuntimeWarning。

    :param reason: 警告信息，可以自定义说明原因
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"Call to experimental function '{func.__name__}': {reason}",
                category=RuntimeWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        wrapper.__experimental__ = True  # type: ignore[attr-defined] # 给函数打个标记，方便外部检测
        return wrapper

    return decorator
