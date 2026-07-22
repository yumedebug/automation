import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional

import customtkinter as ctk

from actions import ALL_ACTIONS
from actions.base_action import BaseAction, ActionParameter, ParameterType, ActionCategory
from workflow_engine import Workflow, WorkflowEngine, create_action
from i18n import t, CATEGORY_JA, UI, CHOICES_JA, is_japanese
import fonts

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SAVED_DIR = Path(__file__).parent / "saved_workflows"
SAVED_DIR.mkdir(parents=True, exist_ok=True)


class ActionConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, action: BaseAction, index: int):
        super().__init__(parent)
        self.action = action
        self.index = index
        self.result = None
        self.title(t("Configure: {}", "設定: {}").format(action.display_name()))
        self.geometry("520x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.widgets = {}
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(self, text=self.action.display_name(), font=fonts.FONT_HEADING_BIG)
        title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        desc = ctk.CTkLabel(self, text=self.action.display_description(), font=fonts.FONT_BODY, text_color="gray")
        desc.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        canvas = ctk.CTkScrollableFrame(self, height=300)
        canvas.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        canvas.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        for i, p in enumerate(self.action.parameters):
            label = ctk.CTkLabel(canvas, text=p.display_label(), anchor="w", font=fonts.FONT_BODY)
            label.grid(row=i, column=0, padx=(10, 5), pady=6, sticky="w")
            widget = self._create_param_widget(canvas, p)
            widget.grid(row=i, column=1, padx=(5, 10), pady=3, sticky="ew")
            self.widgets[p.name] = widget
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=(10, 15))
        ctk.CTkButton(btn_frame, text="OK", command=self._ok, width=100,
                       font=fonts.FONT_BUTTON).pack(side="left", padx=5)
        cancel_text = t("Cancel", "キャンセル")
        ctk.CTkButton(btn_frame, text=cancel_text, command=self.destroy, width=100,
                       font=fonts.FONT_BUTTON).pack(side="left", padx=5)

    def _create_param_widget(self, parent, p: ActionParameter):
        val = self.action.get_config(p.name)
        browse_text = t("Browse", "参照")
        if p.param_type == ParameterType.BOOLEAN:
            var = ctk.BooleanVar(value=bool(val))
            w = ctk.CTkSwitch(parent, text="", variable=var)
            w.var = var
            w.get_val = lambda: var.get()
            return w
        elif p.param_type == ParameterType.CHOICE:
            choices = p.display_choices()
            current = str(val) if val else (choices[0] if choices else "")
            var = ctk.StringVar(value=current)
            w = ctk.CTkOptionMenu(parent, values=choices, variable=var, dynamic_resizing=False,
                                    font=fonts.FONT_BODY)
            w.var = var
            w.get_val = lambda: var.get()
            return w
        elif p.param_type == ParameterType.TEXT:
            w = ctk.CTkEntry(parent, placeholder_text=p.display_label())
            if val:
                w.insert(0, str(val))
            w.get_val = lambda: w.get()
            return w
        elif p.param_type == ParameterType.NUMBER:
            w = ctk.CTkEntry(parent, placeholder_text=p.display_label())
            if val is not None:
                w.insert(0, str(val))
            w.get_val = lambda: w.get()
            return w
        elif p.param_type in (ParameterType.FILE, ParameterType.FOLDER):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid_columnconfigure(0, weight=1)
            entry = ctk.CTkEntry(frame)
            if val:
                entry.insert(0, str(val))
            entry.grid(row=0, column=0, sticky="ew")
            is_folder = p.param_type == ParameterType.FOLDER
            btn = ctk.CTkButton(frame, text=browse_text, width=60, font=fonts.FONT_BODY,
                                command=lambda e=entry, f=is_folder: self._browse(e, f))
            btn.grid(row=0, column=1, padx=(5, 0))
            frame.get_val = lambda: entry.get()
            return frame
        elif p.param_type == ParameterType.FILES:
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid_columnconfigure(0, weight=1)
            entry = ctk.CTkEntry(frame)
            if val:
                if isinstance(val, list):
                    entry.insert(0, "; ".join(val))
                else:
                    entry.insert(0, str(val))
            entry.grid(row=0, column=0, sticky="ew")
            btn = ctk.CTkButton(frame, text=browse_text, width=60, font=fonts.FONT_BODY,
                                command=lambda e=entry: self._browse_files(e))
            btn.grid(row=0, column=1, padx=(5, 0))
            frame.get_val = lambda: entry.get().split("; ")
            return frame
        w = ctk.CTkEntry(parent, placeholder_text=p.display_label())
        w.get_val = lambda: w.get()
        return w

    def _browse(self, entry, is_folder):
        if is_folder:
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def _browse_files(self, entry):
        paths = filedialog.askopenfilenames()
        if paths:
            entry.delete(0, "end")
            entry.insert(0, "; ".join(paths))

    def _ok(self):
        for p in self.action.parameters:
            w = self.widgets.get(p.name)
            if w is None:
                continue
            val = w.get_val()
            if p.param_type == ParameterType.NUMBER:
                try:
                    val = int(val) if val else p.default
                except ValueError:
                    val = p.default
            self.action.set_config(p.name, val)
        self.result = True
        self.destroy()


class ActionCard(ctk.CTkFrame):
    def __init__(self, parent, action: BaseAction, index: int,
                 on_edit=None, on_delete=None, on_move_up=None, on_move_down=None):
        super().__init__(parent, corner_radius=8, border_width=1, border_color="#333333")
        self.action = action
        self.action_index = index
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.grid_columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self):
        icon = self.action.icon or "⚙"
        num_label = ctk.CTkLabel(self, text=str(self.action_index + 1), width=28,
                                 font=fonts.FONT_SMALL, text_color="gray")
        num_label.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="nw")
        icon_label = ctk.CTkLabel(self, text=icon, font=fonts.FONT_HEADING_BIG, width=30)
        icon_label.grid(row=0, column=1, padx=(0, 5), pady=8, sticky="w")
        name_label = ctk.CTkLabel(self, text=self.action.display_name(), font=fonts.FONT_TITLE_BOLD)
        name_label.grid(row=0, column=2, padx=(0, 5), pady=8, sticky="w")
        summary = self.action.display_summary()
        summary_label = ctk.CTkLabel(self, text=summary, font=fonts.FONT_SMALL, text_color="gray")
        summary_label.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        self.grid_columnconfigure(3, weight=1)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=(5, 8), pady=5, sticky="e")
        up_btn = ctk.CTkButton(btn_frame, text="▲", width=28, height=24, font=fonts.FONT_TINY,
                                command=lambda: self.on_move_up and self.on_move_up(self.action_index))
        up_btn.pack(side="left", padx=1)
        down_btn = ctk.CTkButton(btn_frame, text="▼", width=28, height=24, font=fonts.FONT_TINY,
                                  command=lambda: self.on_move_down and self.on_move_down(self.action_index))
        down_btn.pack(side="left", padx=1)
        edit_btn = ctk.CTkButton(btn_frame, text="⚙", width=28, height=24, font=fonts.FONT_BUTTON,
                                  command=lambda: self.on_edit and self.on_edit(self.action_index))
        edit_btn.pack(side="left", padx=1)
        del_btn = ctk.CTkButton(btn_frame, text="✕", width=28, height=24, font=fonts.FONT_TINY,
                                 fg_color="#5a2020", hover_color="#8a3030",
                                 command=lambda: self.on_delete and self.on_delete(self.action_index))
        del_btn.pack(side="left", padx=1)


class AutomatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        fonts.init_fonts()
        self.title(t("Automator - Workflow Automation", "Automator - ワークフロー自動化"))
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.current_workflow = Workflow()
        self.workflow_path: Optional[str] = None
        self.engine = WorkflowEngine()
        self.engine.set_log_callback(self._on_log)
        self._build_ui()
        self._refresh_workflow_display()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_toolbar()
        self._build_palette()
        self._build_workflow_area()
        self._build_log_panel()

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=48, corner_radius=0)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        toolbar.grid_columnconfigure(10, weight=1)
        ctk.CTkLabel(toolbar, text="  Automator", font=fonts.FONT_HEADING_BIG).grid(row=0, column=0, padx=(15, 10), pady=8)
        sep = ctk.CTkLabel(toolbar, text="|", text_color="gray").grid(row=0, column=1, padx=5)
        run_text = t("  ▶ Run  ", "  ▶ 実行  ")
        run_btn = ctk.CTkButton(toolbar, text=run_text, command=self._run_workflow,
                                 fg_color="#2d7a3a", hover_color="#3a9a4a", font=fonts.FONT_BUTTON_RUN)
        run_btn.grid(row=0, column=2, padx=4, pady=8)
        stop_text = t("  ■ Stop  ", "  ■ 停止  ")
        stop_btn = ctk.CTkButton(toolbar, text=stop_text, command=self._stop_workflow,
                                  fg_color="#7a2d2d", hover_color="#9a3a3a", font=fonts.FONT_BUTTON)
        stop_btn.grid(row=0, column=3, padx=4, pady=8)
        ctk.CTkLabel(toolbar, text="|", text_color="gray").grid(row=0, column=4, padx=5)
        save_text = t("  💾 Save  ", "  💾 保存  ")
        save_btn = ctk.CTkButton(toolbar, text=save_text, command=self._save_workflow,
                                  font=fonts.FONT_BUTTON)
        save_btn.grid(row=0, column=5, padx=4, pady=8)
        open_text = t("  📂 Open  ", "  📂 開く  ")
        open_btn = ctk.CTkButton(toolbar, text=open_text, command=self._open_workflow,
                                  font=fonts.FONT_BUTTON)
        open_btn.grid(row=0, column=6, padx=4, pady=8)
        ctk.CTkLabel(toolbar, text="|", text_color="gray").grid(row=0, column=7, padx=5)
        sched_text = t("  ⏰ Schedule  ", "  ⏰ スケジュール  ")
        sched_btn = ctk.CTkButton(toolbar, text=sched_text, command=self._schedule_workflow,
                                   font=fonts.FONT_BUTTON)
        sched_btn.grid(row=0, column=8, padx=4, pady=8)
        ctk.CTkLabel(toolbar, text="|", text_color="gray").grid(row=0, column=9, padx=2)
        help_text = t("  ❓ Help  ", "  ❓ ヘルプ  ")
        help_btn = ctk.CTkButton(toolbar, text=help_text, command=self._show_help,
                                  fg_color="#2a2a5a", hover_color="#3a3a7a", font=fonts.FONT_BUTTON)
        help_btn.grid(row=0, column=10, padx=4, pady=8)
        tools_values = [
            t("Tools", "ツール"),
            t("Install Context Menu", "右クリックメニューをインストール"),
            t("Remove Context Menu", "右クリックメニューを削除"),
            t("Clear Workflow", "ワークフローをクリア"),
        ]
        tools_menu = ctk.CTkOptionMenu(toolbar, values=tools_values,
                                        command=self._tools_handler, width=180,
                                        font=fonts.FONT_BODY, dropdown_font=fonts.FONT_BODY)
        tools_menu.grid(row=0, column=11, padx=8, pady=8, sticky="e")

    def _build_palette(self):
        palette = ctk.CTkScrollableFrame(self, width=200, corner_radius=0, border_width=0)
        palette.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=0, pady=(5, 0))
        ctk.CTkLabel(palette, text=t("ACTIONS", "アクション"), font=fonts.FONT_BODY_BOLD,
                      text_color="gray").pack(anchor="w", padx=12, pady=(8, 5))
        cats = {}
        for cls in ALL_ACTIONS:
            cat = cls.category.value
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(cls)
        for cat_name, actions in cats.items():
            section = ctk.CTkFrame(palette, fg_color="transparent")
            section.pack(fill="x", padx=5, pady=2)
            display_cat = CATEGORY_JA.get(cat_name, cat_name) if is_japanese() else cat_name
            header = ctk.CTkLabel(section, text=f"▸ {display_cat}", font=fonts.FONT_BODY_BOLD,
                                   anchor="w", cursor="hand2")
            header.pack(fill="x", padx=5, pady=(5, 0))
            for cls in actions:
                btn_label = f"  {cls.icon}  {cls.name_ja}" if (is_japanese() and cls.name_ja) else f"  {cls.icon}  {cls.name}"
                btn = ctk.CTkButton(section, text=btn_label,
                                      anchor="w", height=30, font=fonts.FONT_SMALL, fg_color="transparent",
                                     hover_color="#2a2a2a", border_width=0,
                                     command=lambda c=cls: self._add_action_to_workflow(c))
                btn.pack(fill="x", padx=(15, 5), pady=1)

    def _build_workflow_area(self):
        container = ctk.CTkFrame(self, corner_radius=8)
        container.grid(row=1, column=1, sticky="nsew", padx=(10, 10), pady=(10, 0))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.workflow_header = ctk.CTkLabel(container, text=t("Workflow: {}", "ワークフロー: {}").format("Untitled"),
                                              font=fonts.FONT_HEADING, anchor="w")
        self.workflow_header.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
        self.workflow_canvas = ctk.CTkScrollableFrame(container, corner_radius=6)
        self.workflow_canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        self.workflow_canvas.grid_columnconfigure(0, weight=1)
        add_text = t("  + Add Action  ", "  + アクションを追加  ")
        add_btn = ctk.CTkButton(container, text=add_text, command=self._show_add_action_menu,
                                 font=fonts.FONT_BUTTON)
        add_btn.grid(row=2, column=0, padx=10, pady=(5, 10))

    def _build_log_panel(self):
        log_frame = ctk.CTkFrame(self, corner_radius=8, height=120)
        log_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 10), pady=(5, 10))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        log_header = ctk.CTkLabel(log_frame, text="  Log", font=fonts.FONT_BODY_BOLD, anchor="w")
        log_header.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="ew")
        self.log_text = ctk.CTkTextbox(log_frame, font=fonts.FONT_MONO, wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(2, 8))
        self.log_text.insert("0.0", t("Ready. Add actions to build your workflow.\n",
                                      "準備完了。アクションを追加してください。\n"))

    def _on_log(self, message: str):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.update_idletasks()

    def _add_action_to_workflow(self, action_class):
        action = action_class()
        dlg = ActionConfigDialog(self, action, len(self.current_workflow.actions))
        self.wait_window(dlg)
        if dlg.result:
            self.current_workflow.add_action(action)
            self._on_log(t("Added: {}", "追加: {}").format(action.display_name()))
            self._refresh_workflow_display()

    def _show_add_action_menu(self):
        menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white",
                       activebackground="#3a3a3a", activeforeground="white",
                       font=fonts.FONT_BODY)
        cats = {}
        for cls in ALL_ACTIONS:
            cat = cls.category.value
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(cls)
        for cat_name, actions in cats.items():
            sub = tk.Menu(menu, tearoff=0, bg="#2b2b2b", fg="white",
                          activebackground="#3a3a3a", activeforeground="white",
                          font=fonts.FONT_BODY)
            display_cat = CATEGORY_JA.get(cat_name, cat_name) if is_japanese() else cat_name
            is_jp = is_japanese()
            for cls in actions:
                label = f"{cls.icon} {cls.name_ja}" if is_jp and cls.name_ja else f"{cls.icon} {cls.name}"
                sub.add_command(label=label,
                                command=lambda c=cls: self._add_action_to_workflow(c))
            menu.add_cascade(label=display_cat, menu=sub)
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def _edit_action(self, index: int):
        if 0 <= index < len(self.current_workflow.actions):
            dlg = ActionConfigDialog(self, self.current_workflow.actions[index], index)
            self.wait_window(dlg)
            if dlg.result:
                self._refresh_workflow_display()

    def _delete_action(self, index: int):
        if 0 <= index < len(self.current_workflow.actions):
            action = self.current_workflow.actions[index]
            confirm_msg = t("Delete '{}'?", "'{}' を削除しますか？").format(action.display_name())
            if messagebox.askyesno(t("Confirm", "確認"), confirm_msg):
                self.current_workflow.remove_action(index)
                self._on_log(t("Deleted: {}", "削除: {}").format(action.display_name()))
                self._refresh_workflow_display()

    def _move_action_up(self, index: int):
        if index > 0:
            self.current_workflow.move_action(index, index - 1)
            self._refresh_workflow_display()

    def _move_action_down(self, index: int):
        if index < len(self.current_workflow.actions) - 1:
            self.current_workflow.move_action(index, index + 1)
            self._refresh_workflow_display()

    def _refresh_workflow_display(self):
        for w in self.workflow_canvas.winfo_children():
            w.destroy()
        name = self.current_workflow.name or "Untitled"
        self.workflow_header.configure(
            text=t("Workflow: {}", "ワークフロー: {}").format(name))
        if not self.current_workflow.actions:
            lbl = ctk.CTkLabel(self.workflow_canvas,
                                text=t("Drag actions from the left panel\nor click '+ Add Action'",
                                       "左パネルからアクションをドラッグするか\n「+ アクションを追加」をクリック"),
                                font=fonts.FONT_BODY, text_color="gray")
            lbl.pack(expand=True, fill="both", padx=20, pady=40)
            return
        for i, action in enumerate(self.current_workflow.actions):
            card = ActionCard(
                self.workflow_canvas, action, i,
                on_edit=self._edit_action,
                on_delete=self._delete_action,
                on_move_up=self._move_action_up,
                on_move_down=self._move_action_down,
            )
            card.pack(fill="x", padx=5, pady=3)

    def _run_workflow(self):
        from i18n import UI
        if not self.current_workflow.actions:
            empty_title = t("Empty Workflow", "空のワークフロー")
            empty_msg = t("Add at least one action to the workflow.",
                          "少なくとも1つのアクションを追加してください。")
            messagebox.showinfo(empty_title, empty_msg)
            return
        select_title = t("Select Input", "入力ファイルを選択")
        select_msg = t("Do you want to select input files?", "入力ファイルを選択しますか？")
        if messagebox.askyesno(select_title, select_msg):
            files_title = t("Select Input Files", "入力ファイルを選択")
            paths = filedialog.askopenfilenames(title=files_title)
            initial_input = list(paths) if paths else []
        else:
            initial_input = []
        self.log_text.delete("0.0", "end")
        self._on_log(t("Running workflow...", "ワークフローを実行中..."))
        self.update_idletasks()
        success, result = self.engine.run(self.current_workflow, initial_input)
        if success:
            self._on_log(t("Workflow completed!", "ワークフローが完了しました！"))
        else:
            msg = t("Workflow failed: ", "ワークフローが失敗しました: ")
            self._on_log(f"{msg}{result}")

    def _stop_workflow(self):
        self._on_log(t("Stop requested (not implemented in this version)",
                       "停止が要求されました（このバージョンでは未実装）"))

    def _save_workflow(self):
        wf_filter = t("Automator Workflow", "Automator ワークフロー")
        path = filedialog.asksaveasfilename(
            initialdir=str(SAVED_DIR),
            defaultextension=".awf",
            filetypes=[(wf_filter, "*.awf"), ("All Files", "*.*")],
        )
        if path:
            name = Path(path).stem
            self.current_workflow.name = name
            self.current_workflow.save_to_file(path)
            self.workflow_path = path
            self._on_log(t("Saved: {}", "保存: {}").format(path))
            self._refresh_workflow_display()

    def _open_workflow(self):
        wf_filter = t("Automator Workflow", "Automator ワークフロー")
        path = filedialog.askopenfilename(
            initialdir=str(SAVED_DIR),
            filetypes=[(wf_filter, "*.awf"), ("All Files", "*.*")],
        )
        if path:
            try:
                self.current_workflow = Workflow.load_from_file(path)
                self.workflow_path = path
                self._on_log(t("Loaded: {}", "読み込み: {}").format(path))
                self._refresh_workflow_display()
            except Exception as e:
                err_title = t("Error", "エラー")
                err_msg = t("Failed to load workflow:\n{}",
                           "ワークフローの読み込みに失敗しました:\n{}").format(e)
                messagebox.showerror(err_title, err_msg)

    def _schedule_workflow(self):
        if not self.current_workflow.actions:
            msg = t("Save the workflow first.", "先にワークフローを保存してください。")
            messagebox.showinfo(t("Empty Workflow", "空のワークフロー"), msg)
            return
        tmp_path = SAVED_DIR / f"_schedule_temp_{self.current_workflow.name}.awf"
        self.current_workflow.save_to_file(str(tmp_path))
        ScheduleDialog(self, str(tmp_path))

    def _tools_handler(self, choice):
        install_opt = t("Install Context Menu", "右クリックメニューをインストール")
        remove_opt = t("Remove Context Menu", "右クリックメニューを削除")
        clear_opt = t("Clear Workflow", "ワークフローをクリア")
        if choice == install_opt:
            self._install_context_menu()
        elif choice == remove_opt:
            self._remove_context_menu()
        elif choice == clear_opt:
            clear_title = t("Clear", "クリア")
            clear_msg = t("Clear all actions from workflow?",
                          "全てのアクションをクリアしますか？")
            if messagebox.askyesno(clear_title, clear_msg):
                self.current_workflow.clear()
                self._refresh_workflow_display()
                self._on_log(t("Workflow cleared", "ワークフローをクリアしました"))

    def _show_help(self):
        HelpDialog(self)

    def _install_context_menu(self):
        ps1 = Path(__file__).parent / "context_menu.ps1"
        os.system(f'powershell -ExecutionPolicy Bypass -File "{ps1}" -Action install')
        msg = t("Context menu installed. Right-click files to 'Run with Automator'.",
                "右クリックメニューをインストールしました。ファイルを右クリックして「Automatorで実行」できます。")
        self._on_log(msg)

    def _remove_context_menu(self):
        ps1 = Path(__file__).parent / "context_menu.ps1"
        os.system(f'powershell -ExecutionPolicy Bypass -File "{ps1}" -Action remove')
        self._on_log(t("Context menu removed.", "右クリックメニューを削除しました。"))

    def load_and_run(self, file_paths: list[str]):
        self._on_log(t("Running with files: {}", "ファイルと共に実行: {}").format(file_paths))
        recent = list(SAVED_DIR.glob("*.awf"))
        if not recent:
            msg = t("No saved workflows found. Open the app to create one.",
                    "保存されたワークフローがありません。アプリを開いて作成してください。")
            messagebox.showinfo(t("No Workflows", "ワークフローがありません"), msg)
            return
        if len(recent) == 1:
            wf = Workflow.load_from_file(str(recent[0]))
        else:
            from tkinter.simpledialog import askstring
            names = [p.stem for p in recent]
            prompt = t("Enter workflow name:\n{}", "ワークフロー名を入力:\n{}").format("\n".join(names))
            choice = askstring(t("Select Workflow", "ワークフローを選択"), prompt)
            if not choice:
                return
            matches = [p for p in recent if p.stem == choice]
            if not matches:
                err_msg = t("Workflow '{}' not found.", "ワークフロー '{}' が見つかりません。").format(choice)
                messagebox.showerror(t("Error", "エラー"), err_msg)
                return
            wf = Workflow.load_from_file(str(matches[0]))
        self.current_workflow = wf
        self._refresh_workflow_display()
        success, result = self.engine.run(wf, file_paths)
        if success:
            self._on_log(t("Done! Result: {}", "完了！結果: {}").format(str(result)[:200]))
        else:
            self._on_log(t("Error: {}", "エラー: {}").format(result))

    def run_workflow_file(self, workflow_path: str, file_paths: list[str] = None):
        try:
            wf = Workflow.load_from_file(workflow_path)
            self.current_workflow = wf
            self._refresh_workflow_display()
            msg = t("Running workflow: {}", "ワークフローを実行中: {}").format(workflow_path)
            self._on_log(msg)
            success, result = self.engine.run(wf, file_paths or [])
            return success, result
        except Exception as e:
            self._on_log(t("Error: {}", "エラー: {}").format(e))
            return False, str(e)


class ScheduleDialog(ctk.CTkToplevel):
    def __init__(self, parent, workflow_path: str):
        super().__init__(parent)
        self.workflow_path = workflow_path
        self.title(t("Schedule Workflow", "ワークフローをスケジュール"))
        self.geometry("450x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        title_text = t("Schedule Workflow", "ワークフローをスケジュール")
        ctk.CTkLabel(self, text=title_text, font=fonts.FONT_HEADING).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(15, 10))
        task_label = t("Task Name:", "タスク名:")
        ctk.CTkLabel(self, text=task_label, font=fonts.FONT_BODY).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.task_name = ctk.CTkEntry(self, placeholder_text=t("MyAutomationTask", "MyAutomationTask"),
                                       font=fonts.FONT_BODY)
        self.task_name.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.task_name.insert(0, f"Auto_{Path(self.workflow_path).stem}")
        trig_label = t("Trigger:", "トリガー:")
        ctk.CTkLabel(self, text=trig_label, font=fonts.FONT_BODY).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        trigger_display = [t("daily", "毎日"), t("weekly", "毎週"), t("startup", "起動時")]
        self.trigger_var = ctk.StringVar(value=trigger_display[0])
        trigger_menu = ctk.CTkOptionMenu(self, values=trigger_display,
                                          variable=self.trigger_var, command=self._on_trigger_change,
                                          font=fonts.FONT_BODY)
        trigger_menu.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="ew")
        time_label = t("Time (HH:MM):", "時刻 (HH:MM):")
        ctk.CTkLabel(self, text=time_label, font=fonts.FONT_BODY).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.time_entry = ctk.CTkEntry(self, placeholder_text=t("09:00", "09:00"), font=fonts.FONT_BODY)
        self.time_entry.grid(row=3, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.time_entry.insert(0, "09:00")
        days_label = t("Days (weekly):", "曜日（毎週）:")
        ctk.CTkLabel(self, text=days_label, font=fonts.FONT_BODY).grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.days_entry = ctk.CTkEntry(self, placeholder_text=t("Monday,Wednesday,Friday", "月曜,水曜,金曜"),
                                        font=fonts.FONT_BODY)
        self.days_entry.grid(row=4, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.days_entry.insert(0, t("Monday", "月曜"))
        info_text = t("Creates a Windows Scheduled Task.\nThe workflow will run automatically.",
                      "Windowsのタスクスケジューラを作成します。\nワークフローが自動実行されます。")
        info = ctk.CTkLabel(self, text=info_text, font=fonts.FONT_SMALL, text_color="gray")
        info.grid(row=5, column=0, columnspan=2, padx=20, pady=10)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(5, 15))
        create_text = t("Create Schedule", "スケジュール作成")
        ctk.CTkButton(btn_frame, text=create_text, command=self._create, width=140,
                       font=fonts.FONT_BUTTON).pack(side="left", padx=5)
        cancel_text = t("Cancel", "キャンセル")
        ctk.CTkButton(btn_frame, text=cancel_text, command=self.destroy, width=100,
                       font=fonts.FONT_BUTTON).pack(side="left", padx=5)

    def _on_trigger_change(self, choice):
        trigger_map = {t("daily", "毎日"): "daily", t("weekly", "毎週"): "weekly", t("startup", "起動時"): "startup"}
        eng_choice = trigger_map.get(choice, "daily")
        if eng_choice == "startup":
            self.time_entry.configure(state="disabled")
            self.days_entry.configure(state="disabled")
        elif eng_choice == "weekly":
            self.time_entry.configure(state="normal")
            self.days_entry.configure(state="normal")
        else:
            self.time_entry.configure(state="normal")
            self.days_entry.configure(state="disabled")

    def _create(self):
        from scheduler import schedule_workflow
        trigger_map = {t("daily", "毎日"): "daily", t("weekly", "毎週"): "weekly", t("startup", "起動時"): "startup"}
        task_name = self.task_name.get().strip()
        trigger = trigger_map.get(self.trigger_var.get(), "daily")
        params = {}
        if trigger in ("daily", "weekly"):
            params["time"] = self.time_entry.get().strip() or "09:00"
        if trigger == "weekly":
            params["days"] = self.days_entry.get().strip() or "Monday"
        ok, msg = schedule_workflow(self.workflow_path, task_name, trigger, params)
        if ok:
            success_title = t("Success", "成功")
            success_msg = t("Task '{}' created!", "タスク '{}' を作成しました！").format(task_name)
            messagebox.showinfo(success_title, success_msg)
            self.destroy()
        else:
            fail_title = t("Error", "エラー")
            fail_msg = t("Failed:\n{}", "失敗:\n{}").format(msg)
            messagebox.showerror(fail_title, fail_msg)


class HelpDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("Help - How to Use Automator", "ヘルプ - Automatorの使い方"))
        self.geometry("600x560")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        canvas = ctk.CTkScrollableFrame(self)
        canvas.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        canvas.grid_columnconfigure(0, weight=1)
        from i18n import t as _t
        is_jp = is_japanese()

        intro = _t("help_intro",
            "Automator lets you create workflows by chaining actions together.\n"
            "Each action takes input, processes it, and passes the result to the next action.")[1] if is_jp else \
            _t("help_intro", "")[0]
        ctk.CTkLabel(canvas, text=intro, font=fonts.FONT_BODY, justify="left",
                      wraplength=540).pack(anchor="w", padx=5, pady=(5, 15))

        steps = [
            ("help_step1", "help_step1_detail"),
            ("help_step2", "help_step2_detail"),
            ("help_step3", "help_step3_detail"),
            ("help_step4", "help_step4_detail"),
        ]
        for title_key, detail_key in steps:
            title = _t(title_key, "")[1] if is_jp else _t(title_key, "")[0]
            detail = _t(detail_key, "")[1] if is_jp else _t(detail_key, "")[0]
            ctk.CTkLabel(canvas, text=title, font=fonts.FONT_TITLE_BOLD,
                          anchor="w").pack(anchor="w", padx=5, pady=(10, 2))
            ctk.CTkLabel(canvas, text=detail, font=fonts.FONT_BODY, justify="left",
                          wraplength=540).pack(anchor="w", padx=15, pady=(0, 5))

        sep = ctk.CTkFrame(canvas, height=1, fg_color="#444")
        sep.pack(fill="x", padx=5, pady=10)

        tips_title = _t("help_tips", "Tips")[1] if is_jp else _t("help_tips", "Tips")[0]
        ctk.CTkLabel(canvas, text=tips_title, font=fonts.FONT_TITLE_BOLD,
                      anchor="w").pack(anchor="w", padx=5, pady=(5, 2))
        tips_detail = _t("help_tips_detail", "")[1] if is_jp else _t("help_tips_detail", "")[0]
        ctk.CTkLabel(canvas, text=tips_detail, font=fonts.FONT_BODY, justify="left",
                      wraplength=540).pack(anchor="w", padx=15, pady=(0, 10))

        sep2 = ctk.CTkFrame(canvas, height=1, fg_color="#444")
        sep2.pack(fill="x", padx=5, pady=10)

        actions_title = _t("help_actions_list", "Available Actions ({} total)").format(len(ALL_ACTIONS))
        if is_jp:
            actions_title = f"利用可能なアクション（全{len(ALL_ACTIONS)}個）"
        ctk.CTkLabel(canvas, text=actions_title, font=fonts.FONT_TITLE_BOLD,
                      anchor="w").pack(anchor="w", padx=5, pady=(5, 5))

        cats = {}
        for cls in ALL_ACTIONS:
            cat = cls.category.value
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(cls)
        for cat_name, actions in cats.items():
            display_cat = CATEGORY_JA.get(cat_name, cat_name) if is_jp else cat_name
            ctk.CTkLabel(canvas, text=f"  {display_cat}", font=fonts.FONT_BODY_BOLD,
                          anchor="w").pack(anchor="w", padx=10, pady=(5, 1))
            for cls in actions:
                a_name = cls.name_ja if is_jp and cls.name_ja else cls.name
                a_desc = cls.description_ja if is_jp and cls.description_ja else cls.description
                ctk.CTkLabel(canvas, text=f"    {cls.icon} {a_name}: {a_desc}",
                              font=fonts.FONT_SMALL, anchor="w", justify="left",
                              wraplength=530).pack(anchor="w", padx=20, pady=1)

        ctk.CTkButton(canvas, text="OK", command=self.destroy,
                       width=100, font=fonts.FONT_BUTTON).pack(pady=(15, 5))


def launch_gui():
    app = AutomatorApp()
    if len(sys.argv) > 2 and sys.argv[1] == "--run":
        wf_path = sys.argv[2]
        files = sys.argv[3:] if len(sys.argv) > 3 else []
        app.run_workflow_file(wf_path, files)
    elif len(sys.argv) > 2 and sys.argv[1] == "--run-with-files":
        files = sys.argv[2:]
        app.load_and_run(files)
    app.mainloop()
