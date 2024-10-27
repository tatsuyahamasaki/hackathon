import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from datetime import datetime, timedelta
from tkcalendar import Calendar
import json

# タスクデータを保存するためのファイル名
DATA_FILE = "tasks_with_calendar.json"

# カレンダーダイアログのクラス
class CalendarDialog(simpledialog.Dialog):
    def __init__(self, master, title=None):
        self.selected_date = None
        super().__init__(parent=master, title=title)
   
    def body(self, master):
        self.calendar = Calendar(master, showweeknumbers=False, date_pattern="yyyy/mm/dd")
        self.calendar.pack(padx=10, pady=10)

    def apply(self):
        self.selected_date = self.calendar.get_date()

# タスクデータの読み込み（リスト形式）
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# タスクデータの保存（リスト形式）
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# カレンダーから締め切りを選択
def select_date():
    dialog = CalendarDialog(root, title="締め切りを選択")
    return dialog.selected_date

# タスクの追加
def add_task():
    task = simpledialog.askstring("タスク追加", "追加するタスクを入力してください:")
    if not task:
        return

    deadline = select_date()
    if deadline:
        # 新しいタスクをリストに追加
        data.append({"name": task, "completed": False, "deadline": deadline})
        save_data(data)
        messagebox.showinfo("成功", f"「{task}」が追加されました（締め切り: {deadline}）。")
        update_task_list()
        update_calendar_marks()  # カレンダーのマークを更新

# タスクリストの選択肢を生成（タスク名と締切日）
def get_task_choices(include_completed=False):
    task_choices = []
################################変更箇所####################################
    sorted_data = sorted(
        [task for task in data],
        key=lambda x: datetime.strptime(x["deadline"], "%Y/%m/%d")
    )

    for task in sorted_data:

################################変更箇所####################################

        if not task["completed"] or include_completed:
            task_choices.append(f"{task['name']} - {task['deadline']}")
    return task_choices

# 選択されたタスクからタスク名を抽出
def extract_task_name(selected_task):
    return selected_task.split(" - ")[0]

# カレンダーのマークを更新
def update_calendar_marks():
    for date in calendar.get_calevents():
        calendar.calevent_remove(date)
    for task in data:
        if not task["completed"]:
            deadline = task["deadline"]
            calendar.calevent_create(datetime.strptime(deadline, "%Y/%m/%d"), "● " + task['name'], "task")
    calendar.tag_config("task", foreground="red")

# 締め切りが近いタスクリストを表示
def update_task_list():
    root.task_list.delete(0, tk.END)
    today = datetime.today()
    upcoming_deadline = today + timedelta(days=7)
################################変更箇所####################################

    # データを締め切り日でソート（締め切りが早い順）
    sorted_data = sorted(
        [task for task in data if not task["completed"]],
        key=lambda x: datetime.strptime(x["deadline"], "%Y/%m/%d")
    )

    for task in sorted_data:

##########################################################################

        deadline = datetime.strptime(task["deadline"], "%Y/%m/%d")
        if deadline <= upcoming_deadline and not task["completed"]:
            root.task_list.insert(tk.END, f"{task['name']} - 未完了（締め切り: {task['deadline']}）")

# タスクの完了と削除
def complete_task():
    complete_window = tk.Toplevel(root)
    complete_window.title("タスクを完了")
    complete_window.geometry("300x250")
    
    selected_task = tk.StringVar(complete_window)
    task_choices = get_task_choices()
    selected_task.set(task_choices[0] if task_choices else "タスクなし")
    task_menu = tk.OptionMenu(complete_window, selected_task, *task_choices)
    task_menu.pack(pady=10)

    # タスク完了後に削除するかどうかを選択するチェックボックス
    delete_after_complete = tk.BooleanVar()
    delete_check = tk.Checkbutton(complete_window, text="完了後に削除", variable=delete_after_complete)
    delete_check.pack(pady=10)

    def confirm_complete():
        task_text = selected_task.get()
        task_name = extract_task_name(task_text)
        
        # リストから該当タスクを見つけて処理
        for task in data:
            if task["name"] == task_name:
                task["completed"] = True
                if delete_after_complete.get():
                    data.remove(task)
                    messagebox.showinfo("完了と削除", f"「{task_name}」が完了し、削除されました。")
                else:
                    messagebox.showinfo("完了", f"「{task_name}」が完了になりました。")
                save_data(data)
                update_task_list()
                update_calendar_marks()  # カレンダーのマークを更新
                complete_window.destroy()
                break
        else:
            messagebox.showwarning("エラー", "そのタスクは存在しません。")

    complete_button = tk.Button(complete_window, text="完了", command=confirm_complete)
    complete_button.pack(pady=5)

# アプリ終了処理
def on_closing():
    save_data(data)
    root.destroy()

# メインウィンドウの設定
root = tk.Tk()
root.title("タスク管理アプリ")
root.geometry("600x800")

# データの読み込み
data = load_data()

# カレンダーウィジェットを追加
calendar = Calendar(root, selectmode='day', date_pattern="yyyy/mm/dd", showweeknumbers=False)
calendar.pack(pady=20)
update_calendar_marks()  # カレンダーのマークを初期設定

# カレンダーをタップした時の処理
def show_tasks_for_selected_date(event):
    selected_date = calendar.get_date()  # 選択した日付を取得
    tasks_for_date = [task["name"] for task in data if task["deadline"] == selected_date and not task["completed"]]

    if tasks_for_date:
        task_message = "\n".join(tasks_for_date)
        messagebox.showinfo("タスク一覧", f"{selected_date} のタスク:\n{task_message}")
    else:
        messagebox.showinfo("タスク一覧", f"{selected_date} のタスクはありません。")

# カレンダーのタップイベントをバインド
calendar.bind("<<CalendarSelected>>", show_tasks_for_selected_date)

# 締め切りが近いタスクを表示するリストボックス
root.task_list = tk.Listbox(root, selectmode="multiple", bd=10)
root.task_list.pack(fill="both", expand=True, padx=20, pady=(10, 0))

update_task_list()

# ボタンの配置
frame = tk.Frame(root)
frame.pack(pady=10)

btn_add = tk.Button(frame, text="タスクを追加", width=20, command=add_task)
btn_add.grid(row=0, column=0, pady=5)

btn_complete = tk.Button(frame, text="タスクを完了", width=20, command=complete_task)
btn_complete.grid(row=2, column=0, pady=5)

btn_exit = tk.Button(frame, text="終了", width=20, command=on_closing)
btn_exit.grid(row=5, column=0, pady=5)

# ウィンドウを閉じるときの処理
root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループの開始
root.mainloop()