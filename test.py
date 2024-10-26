import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from datetime import datetime
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

        # リストボックスにタスクを追加
        root.task_list.insert(tk.END, f"{task} - 未完了（締め切り: {deadline}）")

# タスクの完了状態を切り替え
def toggle_task():
    task = simpledialog.askstring("タスク切り替え", "完了/未完了を切り替えるタスクを入力してください:")
    if task in data:
        data[task]["completed"] = not data[task]["completed"]
        save_data(data)
        status = "完了" if data[task]["completed"] else "未完了"
        messagebox.showinfo("成功", f"「{task}」が{status}になりました。")

        # リストボックスを更新
        update_task_list()

    else:
        messagebox.showwarning("エラー", "そのタスクは存在しません。")

# タスクの削除
def delete_task():
    task = simpledialog.askstring("タスク削除", "削除するタスクを入力してください:")
    if task in data:
        del data[task]
        save_data(data)
        messagebox.showinfo("成功", f"「{task}」が削除されました。")

        # リストボックスを更新
        update_task_list()

    else:
        messagebox.showwarning("エラー", "そのタスクは存在しません。")

# タスクのリストボックスを更新
def update_task_list():
    # リストボックスをクリア
    root.task_list.delete(0, tk.END)
    for task, info in data.items():
        status = "完了" if info["completed"] else "未完了"
        root.task_list.insert(tk.END, f"{task} - {status}（締め切り: {info['deadline']}）")

# 締め切りが近いタスクを表示
def show_near_deadline():
    today = datetime.today()
    tasks_window = tk.Toplevel(root)
    tasks_window.title("締め切りが近いタスク")
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
    save_data(data)#アプリが閉じられるときにデータ保存
    root.destroy()

# メインウィンドウの設定
root = tk.Tk()
root.title("タスク管理アプリ")

# データの読み込み
data = load_data()

# タスクの一覧を表示するリストボックス
root.task_list = tk.Listbox(root, selectmode="multiple", bd=10)
root.task_list.pack(fill="both", expand=True, padx=20, pady=(10, 0))  # ボタンの上に配置

# ボタンの配置
frame = tk.Frame(root)
frame.pack(pady=10)

btn_add = tk.Button(frame, text="タスクを追加", width=20, command=add_task)
btn_add.grid(row=0, column=0, pady=5)

btn_toggle = tk.Button(frame, text="完了/未完了切替", width=20, command=toggle_task)
btn_toggle.grid(row=2, column=0, pady=5)

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
