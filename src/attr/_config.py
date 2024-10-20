# mypy: ignore-errors
# SPDX-License-Identifier: MIT

__all__ = ["set_run_validators", "get_run_validators"]

_run_validators = True


def set_run_validators(run):
    """
    设置是否运行验证器。默认情况下，它们是运行的。

    .. deprecated:: 21.3.0 不会被移除，但也不会迁移到新的 ``attrs`` 命名空间。请改用 `attrs.validators.set_disabled()`
        。
    """
    if not isinstance(run, bool):
        msg = "'run' 必须是布尔值。"
        raise TypeError(msg)
    global _run_validators
    _run_validators = run


def get_run_validators():
    """
    返回验证器是否运行。

    .. deprecated:: 21.3.0 不会被移除，但也不会迁移到新的 ``attrs`` 命名空间。请改用 `attrs.validators.get_disabled()`
        。
    """
    return _run_validators
