from pathlib import Path
from typing import Dict, Type

from pydantic import BaseModel, Field

from composio.tools.base.local import LocalAction
from composio.tools.local.codeanalysis import embedder


class GetRelevantCodeRequest(BaseModel):
    repo_name: str = Field(
        ...,
        description="Name of the repository. It should be the last part of valid github repository name. It should not contain any '/'.",
    )
    query: str = Field(
        ...,
        description="Query to retrieve relevant code from the repository",
    )


class GetRelevantCodeResponse(BaseModel):
    result: str = Field(
        ...,
        description="Retrieved method body as a string, including any decorators and comments",
    )


class GetRelevantCode(LocalAction[GetRelevantCodeRequest, GetRelevantCodeResponse]):
    """
    Retrieves relevant code snippets from a repository based on a given query.

    Use this action when you need to:
    1. Find code snippets related to a specific topic or functionality.
    2. Search for implementations of particular features across the codebase.
    3. Gather context-specific code examples for analysis or reference.

    Usage example:
    repo_name: django
    query: "database connection pooling"

    The relevance of retrieved code snippets depends on the quality and specificity of the provided query.
    """

    display_name = "Get Relevant Code"
    _tags = ["index"]

    def execute(
        self, request: GetRelevantCodeRequest, metadata: Dict
    ) -> GetRelevantCodeResponse:
        try:
            repo_path = request.repo_name
            if "/" in repo_path:
                repo_path = repo_path.split("/")[-1]
            repo_path = Path.home() / repo_path
            vector_store = embedder.get_vector_store(repo_path, overwrite=False)
            query = request.query
            results = embedder.get_topn_chunks_from_query(vector_store, query, top_n=5)
            sep = "\n" + "=" * 100 + "\n"
            result_string = "Query: " + query + sep
            for i, metadata in enumerate(results["metadata"]):
                result_string += f"Chunk {i + 1}: \n" + str(metadata["chunk"]) + sep
            return GetRelevantCodeResponse(result=result_string)
        except Exception as e:
            raise RuntimeError(f"Failed to execute GetRelevantCode: {e}")
