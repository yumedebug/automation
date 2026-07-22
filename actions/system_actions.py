import os
import subprocess
from pathlib import Path
from typing import Any

from actions.base_action import (
    BaseAction, ActionParameter, ActionCategory, ParameterType
)


class RunScriptAction(BaseAction):
    name = "Run Script"
    name_ja = "スクリプトを実行"
    description = "Run a Python or batch script"
    description_ja = "Pythonスクリプトまたはバッチファイルを実行します"
    icon = "⚡"
    category = ActionCategory.SYSTEM
    parameters = [
        ActionParameter("script_path", "Script Path", ParameterType.FILE, "", label_ja="スクリプトパス"),
        ActionParameter("script_type", "Script Type", ParameterType.CHOICE, "auto",
                        choices=["auto", "python", "batch", "powershell"],
                        choices_ja=["自動判別", "Python", "バッチ", "PowerShell"],
                        label_ja="スクリプト種類"),
        ActionParameter("arguments", "Arguments", ParameterType.TEXT, "", required=False, label_ja="引数"),
        ActionParameter("wait_for_exit", "Wait for completion", ParameterType.BOOLEAN, True,
                        label_ja="完了を待つ"),
        ActionParameter("pass_files_as_args", "Pass input files as arguments", ParameterType.BOOLEAN, False,
                        label_ja="ファイルを引数として渡す"),
    ]

    def run(self, input_data: Any) -> Any:
        sp = self.config.get("script_path", "")
        if not sp or not os.path.isfile(sp):
            return input_data
        st = self.config.get("script_type", "auto")
        args = self.config.get("arguments", "")
        wait = self.config.get("wait_for_exit", True)
        pass_files = self.config.get("pass_files_as_args", False)
        if st == "auto":
            ext = Path(sp).suffix.lower()
            if ext in (".py",):
                st = "python"
            elif ext in (".bat", ".cmd"):
                st = "batch"
            elif ext in (".ps1",):
                st = "powershell"
            else:
                st = "batch"
        cmd = []
        if st == "python":
            cmd = ["python", sp]
        elif st == "batch":
            cmd = [sp]
        elif st == "powershell":
            cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", sp]
        if args:
            cmd.extend(args.split())
        if pass_files and isinstance(input_data, list):
            cmd.extend(input_data)
        try:
            if wait:
                subprocess.run(cmd, capture_output=True, text=True)
            else:
                subprocess.Popen(cmd, shell=True)
        except Exception:
            pass
        return input_data

    def summary(self) -> str:
        from i18n import is_japanese
        name = Path(self.config.get("script_path", "")).name or 'script'
        if is_japanese():
            return f"実行: {name}"
        return f"Run: {name}"


class ShowMessageAction(BaseAction):
    name = "Show Message"
    name_ja = "メッセージを表示"
    description = "Display a message dialog"
    description_ja = "メッセージダイアログを表示します"
    icon = "💬"
    category = ActionCategory.SYSTEM
    parameters = [
        ActionParameter("title", "Title", ParameterType.TEXT, "Automator", label_ja="タイトル"),
        ActionParameter("message", "Message", ParameterType.TEXT, "Workflow completed!", label_ja="メッセージ"),
        ActionParameter("icon", "Icon", ParameterType.CHOICE, "info",
                        choices=["info", "warning", "error", "question"],
                        choices_ja=["情報", "警告", "エラー", "質問"],
                        label_ja="アイコン"),
        ActionParameter("include_input_summary", "Include input summary", ParameterType.BOOLEAN, False,
                        label_ja="入力を含める"),
    ]

    def run(self, input_data: Any) -> Any:
        title = self.config.get("title", "Automator")
        msg = self.config.get("message", "Workflow completed!")
        icon = self.config.get("icon", "info")
        include = self.config.get("include_input_summary", False)
        if include and input_data:
            data_str = str(input_data)
            if len(data_str) > 500:
                data_str = data_str[:500] + "..."
            msg = f"{msg}\n\nInput:\n{data_str}"
        import tkinter.messagebox as mb
        if icon == "info":
            mb.showinfo(title, msg)
        elif icon == "warning":
            mb.showwarning(title, msg)
        elif icon == "error":
            mb.showerror(title, msg)
        elif icon == "question":
            mb.showinfo(title, msg)
        return input_data

    def summary(self) -> str:
        from i18n import is_japanese
        msg = self.config.get("message", "Workflow completed!")[:30]
        if is_japanese():
            return f"メッセージ: {msg}"
        return f"Message: {msg}"


class OpenApplicationAction(BaseAction):
    name = "Open Application"
    name_ja = "アプリを起動"
    description = "Launch an application or document"
    description_ja = "アプリケーションを起動します"
    icon = "🚀"
    category = ActionCategory.SYSTEM
    parameters = [
        ActionParameter("app_path", "Application Path", ParameterType.FILE, "", label_ja="アプリケーションパス"),
        ActionParameter("arguments", "Arguments", ParameterType.TEXT, "", required=False, label_ja="引数"),
        ActionParameter("working_directory", "Working Directory", ParameterType.FOLDER, "", required=False,
                        label_ja="作業ディレクトリ"),
        ActionParameter("run_as_admin", "Run as Administrator", ParameterType.BOOLEAN, False,
                        label_ja="管理者として実行"),
    ]

    def run(self, input_data: Any) -> Any:
        app = self.config.get("app_path", "")
        if not app or not os.path.isfile(app):
            return input_data
        args = self.config.get("arguments", "")
        wd = self.config.get("working_directory", "")
        as_admin = self.config.get("run_as_admin", False)
        cmd = [app]
        if args:
            cmd.extend(args.split())
        try:
            if as_admin:
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{app}' -Verb RunAs"], shell=True)
            else:
                subprocess.Popen(cmd, cwd=wd if wd and os.path.isdir(wd) else None)
        except Exception:
            pass
        return input_data

    def summary(self) -> str:
        from i18n import is_japanese
        name = Path(self.config.get("app_path", "")).name or 'app'
        if is_japanese():
            return f"起動: {name}"
        return f"Open: {name}"


class ShowInExplorerAction(BaseAction):
    name = "Show in Explorer"
    name_ja = "エクスプローラで表示"
    description = "Reveal files/folders in Windows Explorer"
    description_ja = "ファイル/フォルダをエクスプローラで表示します"
    icon = "📁"
    category = ActionCategory.SYSTEM
    parameters = [
        ActionParameter("select_files", "Select files in Explorer", ParameterType.BOOLEAN, True,
                        label_ja="エクスプローラで選択"),
    ]

    def run(self, input_data: Any) -> Any:
        items = self._get_items(input_data)
        if not items:
            return input_data
        select = self.config.get("select_files", True)
        for item in items:
            if os.path.exists(item):
                if select and os.path.isfile(item):
                    subprocess.Popen(["explorer", "/select,", os.path.abspath(item)])
                else:
                    subprocess.Popen(["explorer", os.path.abspath(item)])
                break
        return input_data

    def _get_items(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return input_data
        if isinstance(input_data, str):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "エクスプローラで表示" if is_japanese() else "Show in Explorer"


class CreateFolderAction(BaseAction):
    name = "Create Folder"
    name_ja = "フォルダを作成"
    description = "Create a new folder"
    description_ja = "新しいフォルダを作成します"
    icon = "📁"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("folder_path", "Folder Path", ParameterType.FOLDER, "", label_ja="フォルダパス"),
        ActionParameter("create_subfolder_per_file", "Create subfolder per input file", ParameterType.BOOLEAN, False,
                        label_ja="ファイルごとにサブフォルダを作成"),
    ]

    def run(self, input_data: Any) -> Any:
        fp = self.config.get("folder_path", "")
        if fp:
            os.makedirs(fp, exist_ok=True)
        if self.config.get("create_subfolder_per_file", False):
            items = self._get_items(input_data)
            for item in items:
                p = Path(item)
                sub = p.parent / p.stem
                sub.mkdir(exist_ok=True)
        return input_data

    def _get_items(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return input_data
        if isinstance(input_data, str):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        name = Path(self.config.get("folder_path", "")).name or 'folder'
        if is_japanese():
            return f"作成: {name}"
        return f"Create: {name}"
