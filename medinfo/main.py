import pandas as pd
import tkinter as tk
from tkinter import ttk

# 엑셀 파일 읽기
try:
    df = pd.read_excel('data/medinfo.xlsx', engine='openpyxl')
    print("Excel file read successfully")
    print(df.head())  # Print the first few rows of the DataFrame for verification
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit(1)

# Tkinter 윈도우 생성
root = tk.Tk()
root.title("엑셀 데이터 표시")
print("Tkinter window created")

# Treeview 위젯 설정
tree = ttk.Treeview(root)

# 열 생성
tree["columns"] = list(df.columns)
tree["show"] = "headings"

# 각 열의 제목 설정
for column in tree["columns"]:
    tree.heading(column, text=column)

# 데이터 삽입
for index, row in df.iterrows():
    tree.insert("", "end", values=list(row))

tree.pack(expand=True, fill='both')
print("Treeview widget packed")

# Tkinter 이벤트 루프 시작
root.mainloop()
print("Tkinter event loop started")