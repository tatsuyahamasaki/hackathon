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
def add_word(data):
    word = input("追加する単語を入力してください: ")
    meaning = input(f"{word}の意味を入力してください: ")
    data[word] = meaning
    print(f"「{word}」が追加されました。")

# 単語リストの表示
def show_words(data):
    if data:
        print("\n--- 単語リスト ---")
        for word, meaning in data.items():
            print(f"{word}: {meaning}")
    else:
        print("単語が登録されていません。")

# クイズ機能
def quiz(data):
    if not data:
        print("単語が登録されていません。")
        return
    word = random.choice(list(data.keys()))
    answer = input(f"「{word}」の意味は何ですか？: ")
    if answer == data[word]:
        print("正解！")
    else:
        print(f"不正解... 正しい意味は「{data[word]}」です。")

# メイン処理
def main():
    data = load_data()
    while True:
        print("\n--- 単語帳アプリ ---")
        print("1: 単語を追加")
        print("2: 単語を表示")
        print("3: クイズに挑戦")
        print("4: 終了")
        choice = input("番号を選択してください: ")

        if choice == "1":
            add_word(data)
        elif choice == "2":
            show_words(data)
        elif choice == "3":
            quiz(data)
        elif choice == "4":
            save_data(data)
            print("アプリを終了します。")
            break
        else:
            print("無効な入力です。")

if __name__ == "__main__":
    main()
aaaa
