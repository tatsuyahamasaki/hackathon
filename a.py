import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import json
import random

# 保存するファイル名
DATA_FILE = "vocabulary.json"

# 単語データの読み込み
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 単語データの保存
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 単語の追加
def add_word():
    word = simpledialog.askstring("単語追加", "追加する単語を入力してください:")
    if word:
        meaning = simpledialog.askstring("意味追加", f"{word}の意味を入力してください:")
        if meaning:
            data[word] = meaning
            save_data(data)
            messagebox.showinfo("成功", f"「{word}」が追加されました。")

# 単語リストの表示
def show_words():
    words_window = tk.Toplevel(root)
    words_window.title("単語リスト")
    st = scrolledtext.ScrolledText(words_window, width=40, height=20)
    st.pack(padx=10, pady=10)

    if data:
        for word, meaning in data.items():
            st.insert(tk.END, f"{word}: {meaning}\n")
    else:
        st.insert(tk.END, "単語が登録されていません。")

# クイズ機能
def quiz():
    if not data:
        messagebox.showwarning("エラー", "単語が登録されていません。")
        return

    word = random.choice(list(data.keys()))
    answer = simpledialog.askstring("クイズ", f"「{word}」の意味は何ですか？")
    if answer == data[word]:
        messagebox.showinfo("正解", "正解です！")
    else:
        messagebox.showinfo("不正解", f"不正解... 正しい意味は「{data[word]}」です。")

# アプリ終了処理
def on_closing():
    save_data(data)
    root.destroy()

# メインウィンドウの設定
root = tk.Tk()
root.title("単語帳アプリ")

# データの読み込み
data = load_data()

# ボタンの配置
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

btn_add = tk.Button(frame, text="単語を追加", width=20, command=add_word)
btn_add.grid(row=0, column=0, pady=5)

btn_show = tk.Button(frame, text="単語を表示", width=20, command=show_words)
btn_show.grid(row=1, column=0, pady=5)

btn_quiz = tk.Button(frame, text="クイズに挑戦", width=20, command=quiz)
btn_quiz.grid(row=2, column=0, pady=5)

btn_exit = tk.Button(frame, text="終了", width=20, command=on_closing)
btn_exit.grid(row=3, column=0, pady=5)

# ウィンドウを閉じるときの処理
root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループの開始
root.mainloop()
