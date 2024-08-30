from pathlib import Path
from typing import Dict, Optional, Type

from pydantic import BaseModel, Field

from composio.tools.base.local import LocalAction
from composio.tools.local.codeanalysis.actions.base_action import MethodAnalysisAction


class GetMethodSignatureRequest(BaseModel):
    repo_name: str = Field(
        ...,
        description="Name of the repository. It should be the last part of valid github repository name. It should not contain any '/'.",
    )
    class_name: Optional[str] = Field(
        None,
        description="Name of the class containing the target method",
    )
    method_name: str = Field(
        ..., description="Name of the method whose signature is to be retrieved"
    )


class GetMethodSignatureResponse(BaseModel):
    result: str = Field(
        ...,
        description="Retrieved method signature as a string, including return type and parameters",
    )


class GetMethodSignature(
    LocalAction[GetMethodSignatureRequest, GetMethodSignatureResponse],
    MethodAnalysisAction,
):
    """
    This tool retrieves the signature of a specified method from a given repository.

    Use this action when you need to:
    1. Obtain the signature of a specific method without its implementation.
    2. Extract method signature details for documentation or API analysis.

    This action can retrieve the method signature in two scenarios:
    1. If a class name is provided, it retrieves the method from within that class.
    2. If no class name is provided, it retrieves the method from the global scope.

    Usage example:
    repo_name: django
    class_name: Field
    method_name: run_validators
    """

    display_name = "Get Method Signature"
    _tags = ["index"]

    def execute(
        self, request: GetMethodSignatureRequest, metadata: Dict
    ) -> GetMethodSignatureResponse:
        try:
            repo_path = request.repo_name
            if "/" in repo_path:
                repo_path = repo_path.split("/")[-1]
            repo_path = Path.home() / repo_path
            self.load_fqdn_cache(repo_path)
            method_artefacts = self.get_method_artefacts(
                request.class_name,
                request.method_name,
                repo_path,
            )
            return GetMethodSignatureResponse(result=method_artefacts["signature_ans"])
        except Exception as e:
            raise RuntimeError(f"Failed to execute {self.__class__.__name__}: {e}")
