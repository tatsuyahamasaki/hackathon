#上部にカレンダーの追加（タスク締切日がある日は色が違くなるよう設定）、タスクの削除、完了をdropdownから選択、ウィンドウサイズを調整
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from datetime import datetime
from tkcalendar import Calendar, DateEntry
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

# タスクデータの読み込み
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# タスクデータの保存
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
        data[task] = {"completed": False, "deadline": deadline}
        save_data(data)
        messagebox.showinfo("成功", f"「{task}」が追加されました（締め切り: {deadline}）。")
        update_task_list()
        update_calendar_marks()  # カレンダーのマークを更新

# カレンダーのマークを更新
def update_calendar_marks():
    for date in calendar.get_calevents():
        calendar.calevent_remove(date)  # 既存のイベントを削除
    for task, info in data.items():
        if not info["completed"]:
            deadline = info["deadline"]
            # 締め切り日に赤い点を追加
            calendar.calevent_create(datetime.strptime(deadline, "%Y/%m/%d"), task, "task")

# タスクの完了
def complete_task():
    complete_window = tk.Toplevel(root)
    complete_window.title("タスクを完了")
    complete_window.geometry("300x200")
    
    selected_task = tk.StringVar(complete_window)
    incomplete_tasks = [task for task, info in data.items() if not info["completed"]]
    selected_task.set(incomplete_tasks[0] if incomplete_tasks else "タスクなし")
    task_menu = tk.OptionMenu(complete_window, selected_task, *incomplete_tasks)
    task_menu.pack(pady=10)

    def confirm_complete():
        task = selected_task.get()
        if task in data:
            data[task]["completed"] = True
            save_data(data)
            messagebox.showinfo("成功", f"「{task}」が完了になりました。")
            update_task_list()
            update_calendar_marks()  # カレンダーのマークを更新
            complete_window.destroy()
        else:
            messagebox.showwarning("エラー", "そのタスクは存在しません。")

    complete_button = tk.Button(complete_window, text="完了", command=confirm_complete)
    complete_button.pack(pady=5)

# タスクの削除
def delete_task():
    delete_window = tk.Toplevel(root)
    delete_window.title("タスクを削除")
    delete_window.geometry("300x200")
    
    selected_task = tk.StringVar(delete_window)
    tasks = list(data.keys())
    selected_task.set(tasks[0] if tasks else "タスクなし")
    task_menu = tk.OptionMenu(delete_window, selected_task, *tasks)
    task_menu.pack(pady=10)

    def confirm_delete():
        task = selected_task.get()
        if task in data:
            del data[task]
            save_data(data)
            messagebox.showinfo("成功", f"「{task}」が削除されました。")
            update_task_list()
            update_calendar_marks()  # カレンダーのマークを更新
            delete_window.destroy()
        else:
            messagebox.showwarning("エラー", "そのタスクは存在しません。")

    delete_button = tk.Button(delete_window, text="削除", command=confirm_delete)
    delete_button.pack(pady=5)

# タスクのリストボックスを更新
def update_task_list():
    root.task_list.delete(0, tk.END)
    for task, info in data.items():
        status = "完了" if info["completed"] else "未完了"
        root.task_list.insert(tk.END, f"{task} - {status}（締め切り: {info['deadline']}）")

# 締め切りが近いタスクを表示
def show_near_deadline():
    today = datetime.today()
    tasks_window = tk.Toplevel(root)
    tasks_window.title("締め切りが近いタスク")
    tasks_window.geometry("300x200")
    
    st = scrolledtext.ScrolledText(tasks_window, width=60, height=20)
    st.pack(padx=10, pady=10)

    near_deadline = [
        (task, info) for task, info in data.items()
        if info["deadline"] and (datetime.strptime(info["deadline"], "%Y/%m/%d") - today).days <= 3
    ]

    if near_deadline:
        for task, info in near_deadline:
            status = "完了" if info["completed"] else "未完了"
            st.insert(tk.END, f"{task} - {status}（締め切り: {info['deadline']}）\n")
    else:
        st.insert(tk.END, "締め切りが近いタスクはありません。")

# アプリ終了処理
def on_closing():
    save_data(data)
    root.destroy()

# メインウィンドウの設定
root = tk.Tk()
root.title("タスク管理アプリ")
root.geometry("300x600")

# データの読み込み
data = load_data()

# カレンダーウィジェットを追加
calendar = Calendar(root, selectmode='day', date_pattern="yyyy/mm/dd", showweeknumbers=False)
calendar.pack(pady=20)
update_calendar_marks()  # カレンダーのマークを初期設定

# タスクの一覧を表示するリストボックス
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

btn_delete = tk.Button(frame, text="タスクを削除", width=20, command=delete_task)
btn_delete.grid(row=3, column=0, pady=5)

btn_near_deadline = tk.Button(frame, text="締め切りが近いタスク", width=20, command=show_near_deadline)
btn_near_deadline.grid(row=4, column=0, pady=5)

btn_exit = tk.Button(frame, text="終了", width=20, command=on_closing)
btn_exit.grid(row=5, column=0, pady=5)

# ウィンドウを閉じるときの処理
root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループの開始
root.mainloop()
