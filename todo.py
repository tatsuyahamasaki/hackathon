import tkinter as tk
from tkinter import messagebox, simpledialog
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

# 時刻入力ダイアログの関数（ドロップダウン形式、分は15分単位）
def select_time():
    time_window = tk.Toplevel(root)
    time_window.title("時刻を選択")
    time_window.geometry("+300+250")
    
    # 時と分のドロップダウンリストを作成
    hour_var = tk.StringVar(time_window)
    hour_var.set("23")  # デフォルトを23に設定
    hours = [f"{h:02}" for h in range(24)]
    hour_menu = tk.OptionMenu(time_window, hour_var, *hours)
    hour_menu.grid(row=0, column=1, padx=10, pady=10)
    
    minute_var = tk.StringVar(time_window)
    minute_var.set("45")  # デフォルトを45に設定
    minutes = ["00", "15", "30", "45"]  # 15分単位の選択肢
    minute_menu = tk.OptionMenu(time_window, minute_var, *minutes)
    minute_menu.grid(row=0, column=3, padx=10, pady=10)

    # ラベルを追加
    tk.Label(time_window, text="時:").grid(row=0, column=0)
    tk.Label(time_window, text="分:").grid(row=0, column=2)

    # OKボタンで選択した時刻を取得
    def set_time():
        selected_hour = hour_var.get()
        selected_minute = minute_var.get()
        time_window.destroy()
        return f"{selected_hour}:{selected_minute}"

    ok_button = tk.Button(time_window, text="OK", command=set_time)
    ok_button.grid(row=1, column=1, columnspan=3, pady=10)
    
    time_window.wait_window()  # ウィンドウが閉じられるまで待機

    return f"{hour_var.get()}:{minute_var.get()}"

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

    deadline_date = select_date()
    if deadline_date:
        # 時刻を設定（入力がない場合は23:59に設定）
        deadline_time = select_time()
        deadline = f"{deadline_date} {deadline_time}"

        # 新しいタスクをリストに追加
        data.append({"name": task, "completed": False, "deadline": deadline})
        save_data(data)
        messagebox.showinfo("成功", f"「{task}」が追加されました（締め切り: {deadline}）。")
        update_task_list()
        update_calendar_marks()  # カレンダーのマークを更新

# タスクリストの選択肢を生成（タスク名、締切日、時刻）
def get_task_choices(include_completed=False):
    task_choices = []
    # データを締め切り日でソート（締め切りが早い順）
    sorted_data = sorted(
        [task for task in data],
        key=lambda x: datetime.strptime(x["deadline"], "%Y/%m/%d %H:%M")  # 時刻も含めた形式に変更
    )

    for task in sorted_data:
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
            deadline_date = task["deadline"].split(" ")[0]
            calendar.calevent_create(datetime.strptime(deadline_date, "%Y/%m/%d"), "● " + task['name'], "task")
    calendar.tag_config("task", foreground="red")

# カレンダーの日付をクリックしたときのイベント
def show_tasks_for_selected_date(event):
    selected_date = calendar.get_date()  # 選択した日付を取得
    
    # 新しいウィンドウでタスク情報を表示
    task_window = tk.Toplevel(root)
    task_window.title(f"{selected_date} のタスク")
    
    # Textウィジェットの設定
    task_text = tk.Text(task_window, wrap="word", height=10, width=40)
    task_text.pack(padx=10, pady=10)

    # タスクをウィジェットに挿入（未完了タスクは赤、完了タスクは青で表示）
    tasks_for_date = [
        f"{task['name']} - {task['deadline'].split()[1]} - {'完了' if task['completed'] else '未完了'}"
        for task in data if task["deadline"].startswith(selected_date)
    ]

    if tasks_for_date:
        for task in tasks_for_date:
            if "未完了" in task:
                task_text.insert("end", task + "\n", "incomplete")
            else:
                task_text.insert("end", task + "\n", "completed")
        # 未完了タスクの文字色を赤に設定
        task_text.tag_config("incomplete", foreground="red")
        # 完了済みタスクの文字色を青に設定
        task_text.tag_config("completed", foreground="blue")
    else:
        task_text.insert("end", "この日にタスクはありません。")

    task_text.config(state="disabled")  # テキストを編集不可に

    if tasks_for_date:
        for task in tasks_for_date:
            if "未完了" in task:
                task_text.insert("end", task + "\n", "incomplete")
            else:
                task_text.insert("end", task + "\n")
        # 未完了タスクの文字色を赤に設定
        task_text.tag_config("incomplete", foreground="red")
    else:
        task_text.insert("end", "この日にタスクはありません。")

    task_text.config(state="disabled")  # テキストを編集不可に


# 締め切りが近いタスクリストを表示
def update_task_list():
    root.task_list.delete(0, tk.END)
    today = datetime.today()
    upcoming_deadline = today + timedelta(days=7)

    # データを締め切り日でソート（締め切りが早い順）
    sorted_data = sorted(
        [task for task in data if not task["completed"]],
        key=lambda x: datetime.strptime(x["deadline"], "%Y/%m/%d %H:%M")
    )

    for task in sorted_data:
        deadline = datetime.strptime(task["deadline"], "%Y/%m/%d %H:%M")
        if deadline <= upcoming_deadline and not task["completed"]:
            root.task_list.insert(tk.END, f"{task['name']} - 未完了（締め切り: {task['deadline']}）")

# タスクの完了と削除
def complete_task():
    complete_window = tk.Toplevel(root)
    complete_window.title("タスクを完了")
    complete_window.geometry("300x250+300+250")
    
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
calendar = Calendar(
    root,
    selectmode='day',
    date_pattern="yyyy/mm/dd",
    showweeknumbers=False,
    font=("Arial", 20),  # フォントサイズを16に設定
    width=15,  # カレンダーの幅を拡張
    height=5   # カレンダーの高さを拡張
)
calendar.pack(pady=20)
update_calendar_marks()  # カレンダーのマークを初期設定

# カレンダーの日付をクリックした際にその日のタスクを表示
calendar.bind("<<CalendarSelected>>", show_tasks_for_selected_date)

# 締め切りが近いタスクを表示するリストボックス
root.task_list = tk.Listbox(
    root, 
    bd=10,
    font=("Arial", 15),  # フォントサイズを16に設定
    width=50,  # カレンダーの幅を拡張
    height=10   # カレンダーの高さを拡張
    )
root.task_list.pack(padx=20, pady=(10, 0))

update_task_list()

# ボタンの配置
frame = tk.Frame(root)
frame.pack(pady=10,padx=10)

btn_add = tk.Button(frame, text="タスクを追加", width=20, command=add_task)
btn_add.grid(row=1, column=0, pady=5,padx=5)

btn_complete = tk.Button(frame, text="タスクを完了", width=20, command=complete_task)
btn_complete.grid(row=1, column=2, pady=5,padx=5)

btn_exit = tk.Button(frame, text="終了", width=20, command=on_closing)
btn_exit.grid(row=1, column=5, pady=5,padx=5)

# ウィンドウを閉じるときの処理
root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループの開始
root.mainloop()