import typing as t

from composio.tools.base.local import LocalAction, LocalTool

from .actions import (
    CreateCodeMap,
    GetClassInfo,
    GetMethodBody,
    GetMethodSignature,
    GetRelevantCode,
)


class CodeAnalysisTool(LocalTool, autoload=True):
    """Code index tool."""

    @classmethod
    def actions(cls) -> t.List[t.Type[LocalAction]]:
        """Return the list of actions."""
        return [
            CreateCodeMap,
            GetClassInfo,
            GetMethodBody,
            GetMethodSignature,
            GetRelevantCode,
        ]
