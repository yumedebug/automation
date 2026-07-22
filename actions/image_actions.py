import os
from pathlib import Path
from typing import Any

from PIL import Image

from actions.base_action import (
    BaseAction, ActionParameter, ActionCategory, ParameterType
)


class ConvertImageAction(BaseAction):
    name = "Convert Images"
    name_ja = "画像を変換"
    description = "Convert images between formats (PNG, JPEG, BMP, GIF, WEBP)"
    description_ja = "画像形式を変換します（PNG, JPEG, BMP, GIF, WEBP）"
    icon = "🖼️"
    category = ActionCategory.IMAGES
    parameters = [
        ActionParameter("target_format", "Target Format", ParameterType.CHOICE, "PNG",
                        choices=["PNG", "JPEG", "BMP", "GIF", "WEBP", "TIFF"],
                        label_ja="変換先形式"),
        ActionParameter("quality", "Quality (1-100)", ParameterType.NUMBER, 90, label_ja="品質"),
        ActionParameter("output_folder", "Output Folder (leave empty = same folder)", ParameterType.FOLDER, "",
                        required=False, label_ja="出力フォルダ"),
        ActionParameter("create_subfolder", "Create subfolder 'converted'", ParameterType.BOOLEAN, True,
                        label_ja="'converted'サブフォルダを作成"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_images(input_data)
        if not files:
            return []
        target_fmt = self.config.get("target_format", "PNG").lower()
        quality = int(self.config.get("quality", 90))
        out_folder = self.config.get("output_folder", "")
        create_sub = self.config.get("create_subfolder", True)
        results = []
        for fp in files:
            img = Image.open(fp)
            p = Path(fp)
            if out_folder and os.path.isdir(out_folder):
                out_dir = Path(out_folder)
            elif create_sub:
                out_dir = p.parent / "converted"
            else:
                out_dir = p.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{p.stem}.{target_fmt}"
            if target_fmt == "jpeg":
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(str(out_path), format=target_fmt.upper(), quality=quality)
            elif target_fmt == "webp":
                img.save(str(out_path), format="WEBP", quality=quality)
            else:
                img.save(str(out_path), format=target_fmt.upper())
            results.append(str(out_path))
            img.close()
        return results

    def _get_images(self, input_data: Any) -> list[str]:
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        fmt = self.config.get("target_format", "PNG")
        if is_japanese():
            return f"{fmt}に変換"
        return f"Convert to {fmt}"


class ResizeImageAction(BaseAction):
    name = "Resize Images"
    name_ja = "画像をリサイズ"
    description = "Resize images by dimensions or percentage"
    description_ja = "画像を指定サイズまたはパーセントでリサイズします"
    icon = "📐"
    category = ActionCategory.IMAGES
    parameters = [
        ActionParameter("width", "Width (px, 0=auto)", ParameterType.NUMBER, 800, label_ja="幅（px）"),
        ActionParameter("height", "Height (px, 0=auto)", ParameterType.NUMBER, 0, label_ja="高さ（px）"),
        ActionParameter("mode", "Resize Mode", ParameterType.CHOICE, "fit",
                        choices=["fit", "stretch", "pad", "crop"],
                        choices_ja=["フィット", "引き伸ばし", "パディング", "切り抜き"],
                        label_ja="リサイズモード"),
        ActionParameter("percentage", "Scale by % (0=use dimensions)", ParameterType.NUMBER, 0, label_ja="倍率（%）"),
        ActionParameter("output_format", "Output Format", ParameterType.CHOICE, "same",
                        choices=["same", "PNG", "JPEG", "WEBP"],
                        choices_ja=["元のまま", "PNG", "JPEG", "WEBP"],
                        label_ja="出力形式"),
        ActionParameter("output_folder", "Output Folder", ParameterType.FOLDER, "", required=False,
                        label_ja="出力フォルダ"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_images(input_data)
        if not files:
            return []
        pct = int(self.config.get("percentage", 0))
        w = int(self.config.get("width", 800))
        h = int(self.config.get("height", 0))
        mode = self.config.get("mode", "fit")
        out_fmt = self.config.get("output_format", "same")
        out_folder = self.config.get("output_folder", "")
        results = []
        for fp in files:
            img = Image.open(fp)
            orig_w, orig_h = img.size
            if pct > 0:
                nw = int(orig_w * pct / 100)
                nh = int(orig_h * pct / 100)
            else:
                nw = w if w > 0 else orig_w
                nh = h if h > 0 else orig_h
            if mode == "fit":
                ratio = min(nw / orig_w, nh / orig_h)
                nw = int(orig_w * ratio)
                nh = int(orig_h * ratio)
                resized = img.resize((nw, nh), Image.LANCZOS)
            elif mode == "stretch":
                resized = img.resize((nw, nh), Image.LANCZOS)
            elif mode == "pad":
                ratio = min(nw / orig_w, nh / orig_h)
                tw = int(orig_w * ratio)
                th = int(orig_h * ratio)
                resized = Image.new("RGBA" if img.mode in ("RGBA", "P") else img.mode, (nw, nh), (255, 255, 255, 0))
                temp = img.resize((tw, th), Image.LANCZOS)
                resized.paste(temp, ((nw - tw) // 2, (nh - th) // 2))
            elif mode == "crop":
                ratio = max(nw / orig_w, nh / orig_h)
                tw = int(orig_w * ratio)
                th = int(orig_h * ratio)
                temp = img.resize((tw, th), Image.LANCZOS)
                left = (tw - nw) // 2
                top = (th - nh) // 2
                resized = temp.crop((left, top, left + nw, top + nh))
            p = Path(fp)
            if out_folder and os.path.isdir(out_folder):
                out_dir = Path(out_folder)
            else:
                out_dir = p.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            suffix = f".{out_fmt.lower()}" if out_fmt != "same" else p.suffix
            out_path = out_dir / f"{p.stem}_resized{suffix}"
            save_kw = {}
            if out_fmt != "same":
                fmt = out_fmt
                if fmt == "JPEG":
                    save_kw["quality"] = 90
                    if resized.mode in ("RGBA", "P"):
                        resized = resized.convert("RGB")
            else:
                fmt = p.suffix.lstrip(".").upper() or "PNG"
                if fmt in ("JPG",):
                    fmt = "JPEG"
            resized.save(str(out_path), format=fmt, **save_kw)
            results.append(str(out_path))
            img.close()
        return results

    def _get_images(self, input_data: Any) -> list[str]:
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        w = self.config.get("width", 800)
        h = self.config.get("height", 0)
        pct = self.config.get("percentage", 0)
        if pct > 0:
            if is_japanese():
                return f"リサイズ: {pct}%"
            return f"Resize: {pct}%"
        if is_japanese():
            return f"リサイズ: {w}x{h}"
        return f"Resize: {w}x{h}"


class RotateImageAction(BaseAction):
    name = "Rotate / Flip Images"
    name_ja = "回転／反転"
    description = "Rotate or flip images"
    description_ja = "画像を回転または反転します"
    icon = "🔄"
    category = ActionCategory.IMAGES
    parameters = [
        ActionParameter("operation", "Operation", ParameterType.CHOICE, "rotate_90",
                        choices=["rotate_90", "rotate_180", "rotate_270", "flip_h", "flip_v"],
                        choices_ja=["90°回転", "180°回転", "270°回転", "水平反転", "垂直反転"],
                        label_ja="操作"),
        ActionParameter("output_folder", "Output Folder", ParameterType.FOLDER, "", required=False,
                        label_ja="出力フォルダ"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_images(input_data)
        if not files:
            return []
        op = self.config.get("operation", "rotate_90")
        out_folder = self.config.get("output_folder", "")
        results = []
        for fp in files:
            img = Image.open(fp)
            if op == "rotate_90":
                result = img.rotate(-90, expand=True)
            elif op == "rotate_180":
                result = img.rotate(180, expand=True)
            elif op == "rotate_270":
                result = img.rotate(90, expand=True)
            elif op == "flip_h":
                result = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif op == "flip_v":
                result = img.transpose(Image.FLIP_TOP_BOTTOM)
            p = Path(fp)
            if out_folder and os.path.isdir(out_folder):
                out_dir = Path(out_folder)
            else:
                out_dir = p.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{p.stem}_{op}{p.suffix}"
            result.save(str(out_path))
            results.append(str(out_path))
            img.close()
        return results

    def _get_images(self, input_data: Any) -> list[str]:
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        op = self.config.get("operation", "rotate_90")
        labels = {"rotate_90": "Rotate 90°", "rotate_180": "Rotate 180°", "rotate_270": "Rotate 270°",
                  "flip_h": "Flip H", "flip_v": "Flip V"}
        ja_labels = {"rotate_90": "90°回転", "rotate_180": "180°回転", "rotate_270": "270°回転",
                     "flip_h": "水平反転", "flip_v": "垂直反転"}
        return ja_labels.get(op, op) if is_japanese() else labels.get(op, op)


class WatermarkImageAction(BaseAction):
    name = "Add Watermark"
    name_ja = "透かしを追加"
    description = "Add text watermark to images"
    description_ja = "画像にテキストの透かしを追加します"
    icon = "💧"
    category = ActionCategory.IMAGES
    parameters = [
        ActionParameter("text", "Watermark Text", ParameterType.TEXT, "Watermark", label_ja="透かしテキスト"),
        ActionParameter("position", "Position", ParameterType.CHOICE, "bottom_right",
                        choices=["top_left", "top_right", "bottom_left", "bottom_right", "center"],
                        choices_ja=["左上", "右上", "左下", "右下", "中央"],
                        label_ja="位置"),
        ActionParameter("opacity", "Opacity (0-255)", ParameterType.NUMBER, 100, label_ja="不透明度"),
        ActionParameter("output_folder", "Output Folder", ParameterType.FOLDER, "", required=False,
                        label_ja="出力フォルダ"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_images(input_data)
        if not files:
            return []
        text = self.config.get("text", "Watermark")
        pos = self.config.get("position", "bottom_right")
        opacity = int(self.config.get("opacity", 100))
        out_folder = self.config.get("output_folder", "")
        results = []
        for fp in files:
            img = Image.open(fp).convert("RGBA")
            txt_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(txt_layer)
            font_size = max(img.width, img.height) // 20
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            margin = 20
            positions = {
                "top_left": (margin, margin),
                "top_right": (img.width - tw - margin, margin),
                "bottom_left": (margin, img.height - th - margin),
                "bottom_right": (img.width - tw - margin, img.height - th - margin),
                "center": ((img.width - tw) // 2, (img.height - th) // 2),
            }
            xy = positions.get(pos, positions["bottom_right"])
            draw.text(xy, text, font=font, fill=(255, 255, 255, min(255, max(0, opacity))))
            watermarked = Image.alpha_composite(img, txt_layer)
            p = Path(fp)
            if out_folder and os.path.isdir(out_folder):
                out_dir = Path(out_folder)
            else:
                out_dir = p.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{p.stem}_watermarked{p.suffix}"
            final = watermarked.convert("RGB") if p.suffix.lower() in (".jpg", ".jpeg") else watermarked
            final.save(str(out_path))
            results.append(str(out_path))
            img.close()
        return results

    def _get_images(self, input_data: Any) -> list[str]:
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        txt = self.config.get("text", "Watermark")
        if is_japanese():
            return f"透かし: '{txt}'"
        return f"Watermark: '{txt}'"


class RenameImageSequenceAction(BaseAction):
    name = "Rename Image Sequence"
    name_ja = "画像に連番を付ける"
    description = "Renames image files in sequential order (IMG_001, IMG_002, ...)"
    description_ja = "画像ファイルに連番を付けてリネームします"
    icon = "🔢"
    category = ActionCategory.IMAGES
    parameters = [
        ActionParameter("prefix", "Prefix", ParameterType.TEXT, "IMG_", label_ja="接頭辞"),
        ActionParameter("start", "Start Number", ParameterType.NUMBER, 1, label_ja="開始番号"),
        ActionParameter("digits", "Digits", ParameterType.NUMBER, 3, label_ja="桁数"),
        ActionParameter("sort_by", "Sort By", ParameterType.CHOICE, "name",
                        choices=["name", "date", "size"],
                        choices_ja=["名前", "日付", "サイズ"],
                        label_ja="並び順"),
    ]

    def run(self, input_data: Any) -> Any:
        files = self._get_images(input_data)
        if not files:
            return []
        prefix = self.config.get("prefix", "IMG_")
        start = int(self.config.get("start", 1))
        digits = int(self.config.get("digits", 3))
        sort_by = self.config.get("sort_by", "name")
        if sort_by == "name":
            files.sort()
        elif sort_by == "date":
            files.sort(key=lambda f: os.path.getmtime(f))
        elif sort_by == "size":
            files.sort(key=lambda f: os.path.getsize(f))
        results = []
        for i, fp in enumerate(files):
            p = Path(fp)
            num = str(start + i).zfill(digits)
            new_name = f"{prefix}{num}{p.suffix}"
            new_path = p.parent / new_name
            os.rename(fp, str(new_path))
            results.append(str(new_path))
        return results

    def _get_images(self, input_data: Any) -> list[str]:
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        if isinstance(input_data, list):
            return [f for f in input_data if os.path.isfile(f) and Path(f).suffix.lower() in exts]
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if Path(input_data).suffix.lower() in exts:
                return [input_data]
        return []

    def summary(self) -> str:
        from i18n import is_japanese
        prefix = self.config.get("prefix", "IMG_")
        if is_japanese():
            return f"連番: {prefix}XXX"
        return f"Sequence: {prefix}XXX"
