from actions.base_action import BaseAction, ActionParameter, ActionCategory, ParameterType
from actions.file_actions import (
    AskForFilesAction, RenameFilesAction, CopyFilesAction,
    MoveFilesAction, DeleteFilesAction, FilterFilesAction,
    GetFileInfoAction, OpenFilesAction
)
from actions.image_actions import (
    ConvertImageAction, ResizeImageAction, RotateImageAction,
    WatermarkImageAction, RenameImageSequenceAction
)
from actions.text_actions import (
    ExtractTextAction, ReplaceTextAction, MergeTextAction,
    SplitTextAction, CreateTextFileAction
)
from actions.system_actions import (
    RunScriptAction, ShowMessageAction, OpenApplicationAction,
    ShowInExplorerAction, CreateFolderAction
)

ALL_ACTIONS = [
    AskForFilesAction,
    RenameFilesAction,
    CopyFilesAction,
    MoveFilesAction,
    DeleteFilesAction,
    FilterFilesAction,
    GetFileInfoAction,
    OpenFilesAction,
    ConvertImageAction,
    ResizeImageAction,
    RotateImageAction,
    WatermarkImageAction,
    RenameImageSequenceAction,
    ExtractTextAction,
    ReplaceTextAction,
    MergeTextAction,
    SplitTextAction,
    CreateTextFileAction,
    RunScriptAction,
    ShowMessageAction,
    OpenApplicationAction,
    ShowInExplorerAction,
    CreateFolderAction,
]
