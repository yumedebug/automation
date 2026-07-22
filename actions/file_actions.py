import os
import shutil
import re
import glob as glob_module
from pathlib import Path
from typing import Any

from actions.base_action import (
    BaseAction, ActionParameter, ActionCategory, ParameterType
)


class AskForFilesAction(BaseAction):
    name = "Ask for Files"
    name_ja = "ファイルを選択"
    description = "Show a dialog to select files or folders"
    description_ja = "ファイル選択ダイアログを表示します"
    icon = "📂"
    category = ActionCategory.INPUT_OUTPUT
    parameters = [
        ActionParameter("title", "Dialog Title", ParameterType.TEXT, "Select Files", label_ja="ダイアログタイトル"),
        ActionParameter("file_types", "File Types (e.g. *.txt,*.jpg)", ParameterType.TEXT, "*.*", label_ja="ファイル種類"),
        ActionParameter("allow_multiple", "Allow Multiple Selection", ParameterType.BOOLEAN, True, label_ja="複数選択を許可"),
    ]

    def run(self, input_data: Any) -> Any:
        return input_data

    def summary(self) -> str:
        from i18n import is_japanese
        title = self.config.get("title", "Select Files")
        if is_japanese():
            return f"ファイル選択: {title}"
        return f"Ask for Files: {title}"


class RenameFilesAction(BaseAction):
    name = "Rename Files"
    name_ja = "ファイル名を変更"
    description = "Rename files using patterns (e.g. prefix_{counter}{ext})"
    description_ja = "パターンを使ってファイル名を一括変更します"
    icon = "✏️"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("pattern", "Pattern", ParameterType.TEXT, "file_{counter}", label_ja="パターン"),
        ActionParameter("counter_start", "Counter Start", ParameterType.NUMBER, 1, label_ja="カウンタ開始値"),
        ActionParameter("digits", "Zero Padding (digits)", ParameterType.NUMBER, 3, label_ja="ゼロ埋め桁数"),
        ActionParameter("find_text", "Find Text (replace mode)", ParameterType.TEXT, "", required=False, label_ja="検索文字列"),
        ActionParameter("replace_text", "Replace With", ParameterType.TEXT, "", required=False, label_ja="置換文字列"),
        ActionParameter("mode", "Mode", ParameterType.CHOICE, "counter",
                        choices=["counter", "replace", "lowercase", "uppercase", "prefix_suffix"],
                        choices_ja=["連番", "置換", "小文字", "大文字", "接頭辞/接尾辞"],
                        label_ja="モード"),
        ActionParameter("prefix", "Prefix", ParameterType.TEXT, "", required=False, label_ja="接頭辞"),
        ActionParameter("suffix", "Suffix", ParameterType.TEXT, "", required=False, label_ja="接尾辞"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_files(input_data)
        if not files:
            return []
        mode = self.config.get("mode", "counter")
        results = []
        for i, fp in enumerate(files):
            path = Path(fp)
            parent = path.parent
            stem = path.stem
            ext = path.suffix
            new_name = stem
            if mode == "counter":
                start = int(self.config.get("counter_start", 1))
                digits = int(self.config.get("digits", 3))
                pat = self.config.get("pattern", "file_{counter}")
                counter = str(start + i).zfill(digits)
                new_stem = pat.replace("{counter}", counter).replace("{ext}", ext)
                new_name = new_stem
            elif mode == "replace":
                find = self.config.get("find_text", "")
                repl = self.config.get("replace_text", "")
                new_stem = stem.replace(find, repl)
                new_name = new_stem + ext
            elif mode == "lowercase":
                new_name = stem.lower() + ext
            elif mode == "uppercase":
                new_name = stem.upper() + ext
            elif mode == "prefix_suffix":
                prefix = self.config.get("prefix", "")
                suffix = self.config.get("suffix", "")
                new_name = prefix + stem + suffix + ext
            new_path = parent / new_name
            os.rename(fp, str(new_path))
            results.append(str(new_path))
        return results

    def _get_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese, CHOICES_JA
        mode = self.config.get("mode", "counter")
        if is_japanese():
            mode_label = CHOICES_JA.get(mode, mode)
            if mode == "counter":
                return f"名前変更: {self.config.get('pattern', 'file_{counter}')}"
            elif mode == "replace":
                return f"置換: '{self.config.get('find_text')}' → '{self.config.get('replace_text')}'"
            return f"名前変更: {mode_label}"
        if mode == "counter":
            return f"Rename: {self.config.get('pattern', 'file_{counter}')}"
        elif mode == "replace":
            return f"Rename: '{self.config.get('find_text')}' -> '{self.config.get('replace_text')}'"
        return f"Rename: {mode}"


class CopyFilesAction(BaseAction):
    name = "Copy Files"
    name_ja = "ファイルをコピー"
    description = "Copy files to a destination folder"
    description_ja = "ファイルを指定フォルダにコピーします"
    icon = "📋"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("destination", "Destination Folder", ParameterType.FOLDER, "", label_ja="コピー先フォルダ"),
        ActionParameter("overwrite", "Overwrite Existing", ParameterType.BOOLEAN, False, label_ja="上書きを許可"),
        ActionParameter("flatten", "Flatten (no subfolders)", ParameterType.BOOLEAN, False, label_ja="フラットにする"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_files(input_data)
        dest = self.config.get("destination", "")
        if not files or not dest or not os.path.isdir(dest):
            return files
        overwrite = self.config.get("overwrite", False)
        flatten = self.config.get("flatten", False)
        results = []
        for fp in files:
            path = Path(fp)
            if flatten:
                target = Path(dest) / path.name
            else:
                rel = os.path.relpath(str(path.parent), start=self._common_parent(files))
                target = Path(dest) / rel / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fp, str(target))
            results.append(str(target))
        return results

    def _get_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str):
            if os.path.isfile(input_data):
                return [input_data]
        return []

    def _common_parent(self, files: list[str]) -> str:
        if not files:
            return ""
        paths = [Path(f).parent for f in files]
        common = os.path.commonpath([str(p) for p in paths])
        return common

    def summary(self) -> str:
        from i18n import is_japanese
        dest = self.config.get("destination", "")
        if is_japanese():
            return f"コピー → {dest}" if dest else "ファイルをコピー"
        return f"Copy → {dest}" if dest else "Copy Files"


class MoveFilesAction(BaseAction):
    name = "Move Files"
    name_ja = "ファイルを移動"
    description = "Move files to a destination folder"
    description_ja = "ファイルを指定フォルダに移動します"
    icon = "✂️"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("destination", "Destination Folder", ParameterType.FOLDER, "", label_ja="移動先フォルダ"),
        ActionParameter("overwrite", "Overwrite Existing", ParameterType.BOOLEAN, False, label_ja="上書きを許可"),
        ActionParameter("flatten", "Flatten (no subfolders)", ParameterType.BOOLEAN, False, label_ja="フラットにする"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_files(input_data)
        dest = self.config.get("destination", "")
        if not files or not dest or not os.path.isdir(dest):
            return files
        overwrite = self.config.get("overwrite", False)
        flatten = self.config.get("flatten", False)
        results = []
        for fp in files:
            path = Path(fp)
            if flatten:
                target = Path(dest) / path.name
            else:
                rel = os.path.relpath(str(path.parent), start=self._common_parent(files))
                target = Path(dest) / rel / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(fp, str(target))
            results.append(str(target))
        return results

    def _get_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            return [input_data]
        return []

    def _common_parent(self, files: list[str]) -> str:
        if not files:
            return ""
        paths = [Path(f).parent for f in files]
        common = os.path.commonpath([str(p) for p in paths])
        return common

    def summary(self) -> str:
        from i18n import is_japanese
        dest = self.config.get("destination", "")
        if is_japanese():
            return f"移動 → {dest}" if dest else "ファイルを移動"
        return f"Move → {dest}" if dest else "Move Files"


class DeleteFilesAction(BaseAction):
    name = "Delete Files"
    name_ja = "ファイルを削除"
    description = "Delete files (move to Recycle Bin)"
    description_ja = "ファイルを削除します"
    icon = "🗑️"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("use_recycle_bin", "Move to Recycle Bin", ParameterType.BOOLEAN, True, label_ja="ゴミ箱に入れる"),
        ActionParameter("confirm", "Confirm before deleting", ParameterType.BOOLEAN, True, label_ja="削除前に確認"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_files(input_data)
        if not files:
            return []
        for fp in files:
            try:
                os.remove(fp)
            except Exception:
                pass
        return []

    def _get_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "ファイルを削除" if is_japanese() else "Delete Files"


class FilterFilesAction(BaseAction):
    name = "Filter Files"
    name_ja = "ファイルをフィルタ"
    description = "Filter files by name pattern, size, or date"
    description_ja = "ファイルを名前・サイズ・日付でフィルタします"
    icon = "🔍"
    category = ActionCategory.FILTER
    parameters = [
        ActionParameter("pattern", "Name Pattern (glob)", ParameterType.TEXT, "*", label_ja="名前パターン"),
        ActionParameter("min_size", "Min Size (bytes, 0=no limit)", ParameterType.NUMBER, 0, label_ja="最小サイズ（バイト）"),
        ActionParameter("max_size", "Max Size (bytes, 0=no limit)", ParameterType.NUMBER, 0, label_ja="最大サイズ（バイト）"),
        ActionParameter("extensions", "Extensions filter (comma: .jpg,.png)", ParameterType.TEXT, "", required=False, label_ja="拡張子フィルタ"),
    ]

    def run(self, input_data: Any) -> Any:
        items = self._get_items(input_data)
        pat = self.config.get("pattern", "*")
        min_s = int(self.config.get("min_size", 0))
        max_s = int(self.config.get("max_size", 0))
        exts = self.config.get("extensions", "").strip()
        ext_list = [e.strip().lower() for e in exts.split(",") if e.strip()] if exts else []
        results = []
        for item in items:
            p = Path(item)
            if not p.exists():
                continue
            if pat != "*" and not glob_module.fnmatch.fnmatch(p.name, pat):
                continue
            if p.is_file():
                sz = p.stat().st_size
                if min_s > 0 and sz < min_s:
                    continue
                if max_s > 0 and sz > max_s:
                    continue
            if ext_list and p.suffix.lower() not in ext_list:
                continue
            results.append(item)
        return results

    def _get_items(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return input_data
        if isinstance(input_data, str):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        pat = self.config.get("pattern", "*")
        if is_japanese():
            return f"フィルタ: {pat}"
        return f"Filter: {pat}"


class GetFileInfoAction(BaseAction):
    name = "Get File Info"
    name_ja = "ファイル情報を取得"
    description = "Get file metadata (name, size, date, etc.) as text"
    description_ja = "ファイルのメタデータ（名前・サイズ・日付等）を取得します"
    icon = "ℹ️"
    category = ActionCategory.FILES_FOLDERS
    parameters = [
        ActionParameter("include_size", "Include Size", ParameterType.BOOLEAN, True, label_ja="サイズを含める"),
        ActionParameter("include_date", "Include Date", ParameterType.BOOLEAN, True, label_ja="日付を含める"),
        ActionParameter("format", "Output Format", ParameterType.CHOICE, "text",
                        choices=["text", "csv"], choices_ja=["テキスト", "CSV"],
                        label_ja="出力形式"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_files(input_data)
        if not files:
            return ""
        lines = []
        for fp in files:
            p = Path(fp)
            parts = [f"Name: {p.name}"]
            if self.config.get("include_size", True):
                parts.append(f"Size: {p.stat().st_size} bytes")
            if self.config.get("include_date", True):
                from datetime import datetime
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                parts.append(f"Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            if self.config.get("format") == "csv":
                lines.append(",".join(part.split(": ", 1)[1] for part in parts))
            else:
                lines.append(" | ".join(parts))
        return "\n".join(lines)

    def _get_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "ファイル情報を取得" if is_japanese() else "Get File Info"


class OpenFilesAction(BaseAction):
    name = "Open Files"
    name_ja = "ファイルを開く"
    description = "Open files with the default application"
    description_ja = "既定のアプリケーションでファイルを開きます"
    icon = "🚀"
    category = ActionCategory.FILES_FOLDERS
    parameters = []

    def run(self, input_data: Any) -> Any:
        items = self._get_items(input_data)
        for item in items:
            os.startfile(item)
        return input_data

    def _get_items(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return input_data
        if isinstance(input_data, str):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "ファイルを開く" if is_japanese() else "Open Files"
