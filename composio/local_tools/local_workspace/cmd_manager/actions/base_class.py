from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from composio.local_tools.action import Action
from composio.local_tools.local_workspace.commons.get_logger import get_logger
from composio.local_tools.local_workspace.commons.history_processor import (
    HistoryProcessor,
    history_recorder,
)
from composio.local_tools.local_workspace.commons.local_docker_workspace import (
    KEY_CONTAINER_NAME,
    KEY_IMAGE_NAME,
    KEY_PARENT_PIDS,
    KEY_WORKSPACE_MANAGER,
    WorkspaceManagerFactory,
    get_container_process,
    get_workspace_meta_from_manager,
)
from composio.local_tools.local_workspace.commons.utils import (
    get_container_by_container_name,
)


logger = get_logger()


class BaseRequest(BaseModel):
    workspace_id: str = Field(
        ..., description="workspace-id to get the running workspace-manager"
    )


class BaseResponse(BaseModel):
    output: str = Field(..., description="output of the command")
    return_code: int = Field(
        ..., description="Any output or errors that occurred during the file edit."
    )


class BaseAction(Action, ABC):
    """
    Base class for all actions
    """

    _display_name = ""
    _request_schema = BaseRequest
    _response_schema = BaseResponse
    _tags = ["workspace"]
    _tool_name = "cmdmanagertool"
    script_file = ""
    command = ""
    workspace_factory: WorkspaceManagerFactory = None
    history_processor: HistoryProcessor = None

    def __init__(self):
        super().__init__()
        self.args = None
        self.workspace_id = ""
        self.image_name = ""
        self.container_name = ""
        self.container_process = None
        self.parent_pids = []
        self.container_obj = None
        self.logger = logger

    def set_workspace_and_history(
        self,
        workspace_factory: WorkspaceManagerFactory,
        history_processor: HistoryProcessor,
    ):
        self.workspace_factory = workspace_factory
        self.history_processor = history_processor

    def _setup(self, args: BaseRequest):
        self.args = args
        self.workspace_id = args.workspace_id
        workspace_meta = get_workspace_meta_from_manager(
            self.workspace_factory, self.workspace_id
        )
        self.image_name = workspace_meta[KEY_IMAGE_NAME]
        self.container_name = workspace_meta[KEY_CONTAINER_NAME]
        self.container_process = get_container_process(
            workspace_meta[KEY_WORKSPACE_MANAGER]
        )
        self.parent_pids = workspace_meta[KEY_PARENT_PIDS]
        self.container_obj = get_container_by_container_name(
            self.container_name, self.image_name
        )
        if not self.container_obj:
            raise ValueError(
                f"container-name {self.container_name} is not a valid docker-container"
            )

    def validate_file_name(self, file_name):
        if file_name is None or file_name.strip() == "":
            return "Exception: file-name can not be empty", 1
        return None, 0

    def process_output(self, output, return_code):
        if return_code is None:
            return_code = 1
            output = "Exception: " + output
        return output, return_code

    @abstractmethod
    def execute(
        self, request_data: BaseRequest, authorisation_data: dict
    ) -> BaseResponse:
        pass