import os
from pathlib import Path
from typing import Any

from actions.base_action import (
    BaseAction, ActionParameter, ActionCategory, ParameterType
)


class ExtractTextAction(BaseAction):
    name = "Extract Text"
    name_ja = "テキストを抽出"
    description = "Extract text from files (supports .txt, .md, .csv)"
    description_ja = "ファイルからテキストを抽出します（.txt, .md, .csv対応）"
    icon = "📝"
    category = ActionCategory.TEXT
    parameters = [
        ActionParameter("encoding", "Encoding", ParameterType.CHOICE, "utf-8",
                        choices=["utf-8", "shift_jis", "euc-jp", "utf-16", "ascii"],
                        label_ja="エンコーディング"),
        ActionParameter("combine_with", "Combine With", ParameterType.TEXT, "\n---\n",
                        label_ja="結合文字列"),
        ActionParameter("save_to_file", "Save to File", ParameterType.BOOLEAN, False,
                        label_ja="ファイルに保存"),
        ActionParameter("output_file", "Output File Path", ParameterType.FILE, "", required=False,
                        label_ja="出力ファイルパス"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_text_files(input_data)
        if not files:
            return ""
        encoding = self.config.get("encoding", "utf-8")
        separator = self.config.get("combine_with", "\n---\n")
        texts = []
        for fp in files:
            try:
                with open(fp, "r", encoding=encoding) as f:
                    texts.append(f.read())
            except Exception:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        texts.append(f.read())
                except Exception:
                    texts.append(f"[Error reading {fp}]")
        result = separator.join(texts)
        if self.config.get("save_to_file", False):
            out = self.config.get("output_file", "")
            if out:
                with open(out, "w", encoding="utf-8") as f:
                    f.write(result)
        return result

    def _get_text_files(self, input_data: Any) -> list[str]:
        text_exts = {".txt", ".md", ".csv", ".log", ".ini", ".cfg", ".xml", ".json", ".yaml", ".yml", ".py", ".js", ".html", ".css"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in text_exts]
        if isinstance(input_data, str):
            if os.path.isfile(input_data):
                if Path(input_data).suffix.lower() in text_exts:
                    return [input_data]
            return []
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "テキストを抽出" if is_japanese() else "Extract Text"


class ReplaceTextAction(BaseAction):
    name = "Replace Text in Files"
    name_ja = "テキストを置換"
    description = "Find and replace text in multiple files"
    description_ja = "複数ファイルのテキストを検索・置換します"
    icon = "🔧"
    category = ActionCategory.TEXT
    parameters = [
        ActionParameter("find_text", "Find Text", ParameterType.TEXT, "", label_ja="検索文字列"),
        ActionParameter("replace_text", "Replace With", ParameterType.TEXT, "", required=False,
                        label_ja="置換文字列"),
        ActionParameter("use_regex", "Use Regex", ParameterType.BOOLEAN, False, label_ja="正規表現を使用"),
        ActionParameter("encoding", "Encoding", ParameterType.CHOICE, "utf-8",
                        choices=["utf-8", "shift_jis", "utf-16", "ascii"],
                        label_ja="エンコーディング"),
        ActionParameter("create_backup", "Create Backup (.bak)", ParameterType.BOOLEAN, True,
                        label_ja="バックアップを作成"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_text_files(input_data)
        if not files:
            return ""
        find_text = self.config.get("find_text", "")
        replace_text = self.config.get("replace_text", "")
        use_regex = self.config.get("use_regex", False)
        encoding = self.config.get("encoding", "utf-8")
        backup = self.config.get("create_backup", True)
        if not find_text:
            return input_data
        import re as re_module
        for fp in files:
            try:
                with open(fp, "r", encoding=encoding) as f:
                    content = f.read()
            except Exception:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
            new_content = re_module.sub(find_text, replace_text, content) if use_regex else content.replace(find_text, replace_text)
            if content != new_content:
                if backup:
                    from shutil import copyfile
                    copyfile(fp, fp + ".bak")
                with open(fp, "w", encoding=encoding) as f:
                    f.write(new_content)
        return input_data

    def _get_text_files(self, input_data: Any) -> list[str]:
        text_exts = {".txt", ".md", ".csv", ".log", ".ini", ".cfg", ".xml", ".json", ".yaml", ".yml", ".py", ".js", ".html", ".css"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in text_exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in text_exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        find = self.config.get("find_text", "")
        repl = self.config.get("replace_text", "")
        if is_japanese():
            return f"置換: '{find}' → '{repl}'"
        return f"Replace: '{find}' → '{repl}'"


class MergeTextAction(BaseAction):
    name = "Merge Text Files"
    name_ja = "テキストを結合"
    description = "Merge multiple text files into one"
    description_ja = "複数のテキストファイルを1つに結合します"
    icon = "📄"
    category = ActionCategory.TEXT
    parameters = [
        ActionParameter("separator", "Separator", ParameterType.TEXT, "\n---\n", label_ja="区切り文字"),
        ActionParameter("output_file", "Output File", ParameterType.FILE, "", required=False,
                        label_ja="出力ファイル"),
        ActionParameter("encoding", "Encoding", ParameterType.CHOICE, "utf-8",
                        choices=["utf-8", "shift_jis", "utf-16", "ascii"],
                        label_ja="エンコーディング"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_text_files(input_data)
        if not files:
            return ""
        sep = self.config.get("separator", "\n---\n")
        out_file = self.config.get("output_file", "")
        encoding = self.config.get("encoding", "utf-8")
        texts = []
        for fp in files:
            try:
                with open(fp, "r", encoding=encoding) as f:
                    texts.append(f.read())
            except Exception:
                texts.append(f"[Error reading {fp}]")
        result = sep.join(texts)
        if out_file:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(result)
        return result

    def _get_text_files(self, input_data: Any) -> list[str]:
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f)]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        return "テキストを結合" if is_japanese() else "Merge Text Files"


class SplitTextAction(BaseAction):
    name = "Split Text File"
    name_ja = "テキストを分割"
    description = "Split a text file into multiple files by line count or delimiter"
    description_ja = "テキストファイルを行数または区切り文字で分割します"
    icon = "✂️"
    category = ActionCategory.TEXT
    parameters = [
        ActionParameter("mode", "Split Mode", ParameterType.CHOICE, "lines",
                        choices=["lines", "regex"], choices_ja=["行数", "正規表現"],
                        label_ja="分割モード"),
        ActionParameter("lines_per_file", "Lines Per File", ParameterType.NUMBER, 100,
                        label_ja="ファイルあたりの行数"),
        ActionParameter("delimiter_regex", "Delimiter (regex)", ParameterType.TEXT, "\n---\n", required=False,
                        label_ja="区切り文字（正規表現）"),
        ActionParameter("output_prefix", "Output Prefix", ParameterType.TEXT, "split_",
                        label_ja="出力ファイル接頭辞"),
        ActionParameter("encoding", "Encoding", ParameterType.CHOICE, "utf-8",
                        choices=["utf-8", "shift_jis", "utf-16", "ascii"],
                        label_ja="エンコーディング"),
    ]

    def run(self, input_data: Any) -> Any:
        content = ""
        if isinstance(input_data, str) and os.path.isfile(input_data):
            encoding = self.config.get("encoding", "utf-8")
            try:
                with open(input_data, "r", encoding=encoding) as f:
                    content = f.read()
            except Exception:
                return ""
        elif isinstance(input_data, str):
            content = input_data
        if not content:
            return ""
        mode = self.config.get("mode", "lines")
        prefix = self.config.get("output_prefix", "split_")
        out_dir = Path.cwd()
        results = []
        if mode == "lines":
            lines = content.splitlines(keepends=True)
            per_file = int(self.config.get("lines_per_file", 100))
            for i in range(0, len(lines), per_file):
                chunk = "".join(lines[i:i + per_file])
                out_path = out_dir / f"{prefix}{i // per_file + 1:03d}.txt"
                with open(str(out_path), "w", encoding="utf-8") as f:
                    f.write(chunk)
                results.append(str(out_path))
        elif mode == "regex":
            import re
            delim = self.config.get("delimiter_regex", "\n---\n")
            parts = re.split(delim, content)
            for i, part in enumerate(parts):
                out_path = out_dir / f"{prefix}{i + 1:03d}.txt"
                with open(str(out_path), "w", encoding="utf-8") as f:
                    f.write(part.strip())
                results.append(str(out_path))
        return results

    def summary(self) -> str:
        from i18n import is_japanese, CHOICES_JA
        mode = self.config.get("mode", "lines")
        if is_japanese():
            mode_label = CHOICES_JA.get(mode, mode)
            return f"分割: {mode_label}"
        return f"Split by {mode}"


class CreateTextFileAction(BaseAction):
    name = "Create Text File"
    name_ja = "テキストファイルを作成"
    description = "Create a text file with specified content"
    description_ja = "指定した内容のテキストファイルを作成します"
    icon = "📄"
    category = ActionCategory.TEXT
    parameters = [
        ActionParameter("file_path", "File Path", ParameterType.FILE, "", label_ja="ファイルパス"),
        ActionParameter("content", "Content", ParameterType.TEXT, "", required=False, label_ja="内容"),
        ActionParameter("encoding", "Encoding", ParameterType.CHOICE, "utf-8",
                        choices=["utf-8", "shift_jis", "utf-16"], label_ja="エンコーディング"),
        ActionParameter("overwrite", "Overwrite if exists", ParameterType.BOOLEAN, True, label_ja="上書き"),
        ActionParameter("append_mode", "Append Mode", ParameterType.BOOLEAN, False, label_ja="追記モード"),
        ActionParameter("insert_input", "Insert input data after content", ParameterType.BOOLEAN, False,
                        label_ja="入力データを挿入"),
    ]

    def run(self, input_data: Any) -> Any:
        fp = self.config.get("file_path", "")
        if not fp:
            return input_data
        content = self.config.get("content", "")
        encoding = self.config.get("encoding", "utf-8")
        overwrite = self.config.get("overwrite", True)
        append = self.config.get("append_mode", False)
        insert_input = self.config.get("insert_input", False)
        if insert_input:
            input_str = str(input_data) if input_data else ""
            if input_str:
                content = content + "\n" + input_str if content else input_str
        mode = "a" if append else ("w" if overwrite else "x")
        os.makedirs(os.path.dirname(os.path.abspath(fp)), exist_ok=True)
        try:
            with open(fp, mode, encoding=encoding) as f:
                f.write(content)
        except FileExistsError:
            pass
        return input_data

    def summary(self) -> str:
        from i18n import is_japanese
        name = Path(self.config.get("file_path", "")).name or 'file'
        if is_japanese():
            return f"作成: {name}"
        return f"Create: {name}"
