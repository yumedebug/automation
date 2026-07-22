LANGUAGE = "en"


def set_japanese():
    global LANGUAGE
    LANGUAGE = "jp"


def is_japanese() -> bool:
    return LANGUAGE == "jp"


def t(en: str, ja: str) -> str:
    return ja if LANGUAGE == "jp" else en


CATEGORY_JA = {
    "Files & Folders": "ファイル／フォルダ",
    "Images": "画像",
    "Text": "テキスト",
    "System": "システム",
    "Input / Output": "入力／出力",
    "Filter": "フィルタ",
}

UI = {

    "app_title": ("Automator - Workflow Automation", "Automator - ワークフロー自動化"),

    "toolbar_run": (" ▶ Run ", " ▶ 実行"),
    "toolbar_stop": (" ■ Stop ", " ■ 停止"),
    "toolbar_save": (" 💾 Save ", " 💾 保存"),
    "toolbar_open": (" 📂 Open ", " 📂 開く"),
    "toolbar_schedule": (" ⏰ Schedule ", " ⏰ スケジュール"),

    "tools_menu": "ツール",
    "tools_install": ("Install Context Menu", "右クリックメニューをインストール"),
    "tools_remove": ("Remove Context Menu", "右クリックメニューを削除"),
    "tools_clear": ("Clear Workflow", "ワークフローをクリア"),

    "palette_title": "ACTIONS",

    "workflow_label": ("Workflow: {}", "ワークフロー: {}"),
    "add_action_btn": ("  + Add Action  ", "  + アクションを追加  "),
    "empty_hint": ("Drag actions from the left panel\nor click '+ Add Action'",
                   "左パネルからアクションをドラッグするか\n「+ アクションを追加」をクリック"),

    "log_title": "  Log",
    "log_ready": ("Ready. Add actions to build your workflow.\n", "準備完了。アクションを追加してください。\n"),

    "log_added": ("Added: {}", "追加: {}"),
    "log_deleted": ("Deleted: {}", "削除: {}"),
    "log_saved": ("Saved: {}", "保存: {}"),
    "log_loaded": ("Loaded: {}", "読み込み: {}"),
    "log_cleared": ("Workflow cleared", "ワークフローをクリアしました"),
    "log_running": ("Running workflow...", "ワークフローを実行中..."),
    "log_completed": ("Workflow completed!", "ワークフローが完了しました！"),
    "log_failed": ("Workflow failed: ", "ワークフローが失敗しました: "),
    "log_stopped": ("Stop requested (not implemented in this version)",
                    "停止が要求されました（このバージョンでは未実装）"),
    "log_context_installed": ("Context menu installed. Right-click files to 'Run with Automator'.",
                              "右クリックメニューをインストールしました。ファイルを右クリックして「Automatorで実行」できます。"),
    "log_context_removed": ("Context menu removed.", "右クリックメニューを削除しました。"),
    "log_run_with": ("Running with files: {}", "ファイルと共に実行: {}"),
    "log_done_result": ("Done! Result: {}", "完了！結果: {}"),
    "log_error": ("Error: {}", "エラー: {}"),

    "confirm_delete_title": "Confirm",
    "confirm_delete_msg": ("Delete '{}'?", "'{}' を削除しますか？"),
    "confirm_clear_title": "Clear",
    "confirm_clear_msg": ("Clear all actions from workflow?", "全てのアクションをクリアしますか？"),

    "dialog_configure": ("Configure: {}", "設定: {}"),
    "dialog_ok": "OK",
    "dialog_cancel": "Cancel",
    "dialog_browse": "Browse",

    "run_input_title": ("Select Input", "入力ファイルを選択"),
    "run_input_msg": ("Do you want to select input files?", "入力ファイルを選択しますか？"),
    "run_input_files_title": ("Select Input Files", "入力ファイルを選択"),

    "empty_workflow_title": ("Empty Workflow", "空のワークフロー"),
    "empty_workflow_msg": ("Add at least one action to the workflow.", "少なくとも1つのアクションを追加してください。"),

    "save_dialog_title": ("Automator Workflow", "Automator ワークフロー"),
    "open_dialog_title": ("Automator Workflow", "Automator ワークフロー"),
    "load_error_title": ("Error", "エラー"),
    "load_error_msg": ("Failed to load workflow:\n{}", "ワークフローの読み込みに失敗しました:\n{}"),

    "schedule_save_first": ("Save the workflow first.", "先にワークフローを保存してください。"),
    "no_workflows_title": ("No Workflows", "ワークフローがありません"),
    "no_workflows_msg": ("No saved workflows found. Open the app to create one.",
                         "保存されたワークフローがありません。アプリを開いて作成してください。"),
    "select_workflow_title": ("Select Workflow", "ワークフローを選択"),
    "select_workflow_prompt": ("Enter workflow name:\n{}", "ワークフロー名を入力:\n{}"),
    "workflow_not_found": ("Workflow '{}' not found.", "ワークフロー '{}' が見つかりません。"),

    "sched_title": ("Schedule Workflow", "ワークフローをスケジュール"),
    "sched_task_name": ("Task Name:", "タスク名:"),
    "sched_trigger": ("Trigger:", "トリガー:"),
    "sched_time": ("Time (HH:MM):", "時刻 (HH:MM):"),
    "sched_days": ("Days (weekly):", "曜日（毎週）:"),
    "sched_placeholder_time": "09:00",
    "sched_placeholder_days": "Monday,Wednesday,Friday",
    "sched_placeholder_task": "MyAutomationTask",
    "sched_info": ("Creates a Windows Scheduled Task.\nThe workflow will run automatically.",
                   "Windowsのタスクスケジューラを作成します。\nワークフローが自動実行されます。"),
    "sched_create_btn": ("Create Schedule", "スケジュール作成"),
    "sched_success_title": ("Success", "成功"),
    "sched_success_msg": ("Task '{}' created!", "タスク '{}' を作成しました！"),
    "sched_fail_title": ("Error", "エラー"),
    "sched_fail_msg": ("Failed:\n{}", "失敗:\n{}"),

    "help_btn": ("  ❓ Help  ", "  ❓ ヘルプ  "),
    "help_title": ("Help - How to Use Automator", "ヘルプ - Automatorの使い方"),
    "help_intro": (
        "Automator lets you create workflows by chaining actions together.\n"
        "Each action takes input, processes it, and passes the result to the next action.",
        "Automatorはアクションを連鎖させてワークフローを作成するツールです。\n"
        "各アクションは入力を受け取り、処理し、結果を次のアクションに渡します。",
    ),
    "help_step1": ("1. Add Actions", "1. アクションを追加"),
    "help_step1_detail": (
        "Click an action in the left panel or press '+ Add Action'.\n"
        "Configure each action's settings in the dialog.",
        "左パネルのアクションをクリックするか、「+ アクションを追加」を押します。\n"
        "設定ダイアログで各アクションのパラメータを設定します。",
    ),
    "help_step2": ("2. Arrange Actions", "2. アクションを並べ替え"),
    "help_step2_detail": (
        "Use ▲/▼ buttons to reorder. The workflow runs from top to bottom.\n"
        "Click ⚙ to edit an action, ✕ to delete it.",
        "▲/▼ボタンで順序を変更します。ワークフローは上から下に実行されます。\n"
        "⚙で編集、✕で削除できます。",
    ),
    "help_step3": ("3. Run Workflow", "3. ワークフローを実行"),
    "help_step3_detail": (
        "Press ▶ Run to execute. You'll be asked to select input files.\n"
        "Results flow through each action in sequence.",
        "▶ 実行を押すと実行されます。最初に入力ファイルの選択を求められます。\n"
        "結果は各アクションを順に通過します。",
    ),
    "help_step4": ("4. Save & Schedule", "4. 保存とスケジュール"),
    "help_step4_detail": (
        "Save your workflow with 💾 Save.\n"
        "Use ⏰ Schedule to set up automatic execution via Windows Task Scheduler.",
        "💾 保存でワークフローを保存できます。\n"
        "⏰ スケジュールからWindowsタスクスケジューラで自動実行を設定できます。",
    ),
    "help_tips": ("Tips", "ヒント"),
    "help_tips_detail": (
        "• Right-click any file/folder → 'Run with Automator' (after installing context menu)\n"
        "• Use 'Filter Files' to narrow down file selection\n"
        "• Combine image conversion + resize + rename for batch photo processing\n"
        "• Use 'Show Message' to get notified when a workflow completes",
        "• ファイル/フォルダを右クリック → 「Automatorで実行」（右クリックメニューインストール後）\n"
        "• 「ファイルをフィルタ」で対象ファイルを絞り込めます\n"
        "• 画像変換＋リサイズ＋リネームを組み合わせて一括写真処理\n"
        "• 「メッセージを表示」でワークフロー完了を通知",
    ),
    "help_actions_list": ("Available Actions ({} total)", "利用可能なアクション（全{}個）"),

    "trigger_daily": "daily",
    "trigger_weekly": "weekly",
    "trigger_startup": "startup",
    "trigger_display": ("daily", "毎日"),
    "trigger_weekly_display": ("weekly", "毎週"),
    "trigger_startup_display": ("startup", "起動時"),
}


CHOICES_JA = {
    "counter": "連番",
    "replace": "置換",
    "lowercase": "小文字",
    "uppercase": "大文字",
    "prefix_suffix": "接頭辞/接尾辞",
    "fit": "フィット",
    "stretch": "引き伸ばし",
    "pad": "パディング",
    "crop": "切り抜き",
    "same": "元のまま",
    "PNG": "PNG",
    "JPEG": "JPEG",
    "BMP": "BMP",
    "GIF": "GIF",
    "WEBP": "WEBP",
    "TIFF": "TIFF",
    "rotate_90": "90°回転",
    "rotate_180": "180°回転",
    "rotate_270": "270°回転",
    "flip_h": "水平反転",
    "flip_v": "垂直反転",
    "top_left": "左上",
    "top_right": "右上",
    "bottom_left": "左下",
    "bottom_right": "右下",
    "center": "中央",
    "text": "テキスト",
    "csv": "CSV",
    "name": "名前",
    "date": "日付",
    "size": "サイズ",
    "lines": "行数",
    "regex": "正規表現",
    "info": "情報",
    "warning": "警告",
    "error": "エラー",
    "question": "質問",
    "auto": "自動判別",
    "python": "Python",
    "batch": "バッチ",
    "powershell": "PowerShell",
    "utf-8": "UTF-8",
    "shift_jis": "Shift_JIS",
    "euc-jp": "EUC-JP",
    "utf-16": "UTF-16",
    "ascii": "ASCII",
}
