import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
from tkinter.scrolledtext import ScrolledText


class MedicationBanner(ttk.Frame):
    def __init__(self, parent, medication_data, manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.medication_data = medication_data
        self.manager = manager

        # 배너 스타일 설정
        style = ttk.Style()
        style.configure("Banner.TFrame", background="#f0f0f0")
        style.configure("MedName.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("MedTime.TLabel", font=('Helvetica', 10))
        style.configure("MedInfo.TLabel", font=('Helvetica', 9))

        # 메인 배너 프레임
        self.configure(style="Banner.TFrame", padding="10")

        # 왼쪽 정보 프레임
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 제품명과 복용시간
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame,
                  text=medication_data['Product Name'],
                  style="MedName.TLabel").pack(side=tk.LEFT)

        ttk.Label(header_frame,
                  text=f"복용시간: {medication_data['Notification Time']}",
                  style="MedTime.TLabel").pack(side=tk.RIGHT)

        # 주요 정보 표시
        info_frame = ttk.Frame(left_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))

        info_text = f"주요성분: {medication_data['Main Ingredient']}\n"
        info_text += f"효능: {medication_data['Effectiveness']}\n"
        info_text += f"복용방법: {medication_data['How to Take It']}"

        ttk.Label(info_frame,
                  text=info_text,
                  style="MedInfo.TLabel",
                  wraplength=400).pack(side=tk.LEFT)

        # 오른쪽 버튼 프레임
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # 상세정보 버튼
        ttk.Button(button_frame,
                   text="상세정보",
                   command=self.show_details).pack(pady=2)

        # 시간변경 버튼
        ttk.Button(button_frame,
                   text="시간변경",
                   command=self.change_time).pack(pady=2)

        # 삭제 버튼
        ttk.Button(button_frame,
                   text="삭제",
                   command=self.delete_medication).pack(pady=2)

        # 구분선 추가
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, pady=(10, 0))

    def show_details(self):
        details_window = tk.Toplevel(self)
        details_window.title(f"약물 상세 정보 - {self.medication_data['Product Name']}")
        details_window.geometry("600x400")

        details_frame = ttk.Frame(details_window)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_text = ScrolledText(details_frame)
        info_text.pack(fill=tk.BOTH, expand=True)

        # 모든 정보 표시
        for key, value in self.medication_data.items():
            if key != 'index':  # index 컬럼 제외
                info_text.insert(tk.END, f"{key}: {value}\n\n")

        info_text.configure(state='disabled')

    def change_time(self):
        time_window = tk.Toplevel(self)
        time_window.title("복용 시간 변경")
        time_window.geometry("400x300")

        time_frame = ttk.Frame(time_window)
        time_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 시간 입력
        ttk.Label(time_frame, text="복용 시간:").pack()
        time_entry = ttk.Entry(time_frame)
        time_entry.pack(pady=5)
        time_entry.insert(0, self.medication_data['Notification Time'])
        ttk.Label(time_frame, text="형식: HH:MM (예: 09:00)").pack()

        # 복용 조건 선택
        ttk.Label(time_frame, text="\n복용 조건:").pack()
        condition_var = tk.StringVar()

        conditions = {
            '식전': '식사하기 30분 전에 복용하세요.',
            '식후': '식사 직후에 복용하세요.',
            '공복': '식사와 식사 사이 충분한 시간이 지난 후 복용하세요.\n(보통 식사 2시간 후)'
        }

        for condition in conditions.keys():
            ttk.Radiobutton(time_frame,
                            text=condition,
                            variable=condition_var,
                            value=condition).pack()

        # 설명 레이블
        explanation_label = ttk.Label(time_frame,
                                      text="",
                                      wraplength=350,
                                      justify='left')
        explanation_label.pack(pady=10)

        def update_explanation(*args):
            selected = condition_var.get()
            if selected in conditions:
                explanation_label.config(text=conditions[selected])

        condition_var.trace('w', update_explanation)

        # 이전 설정값 불러오기
        if 'Taking_Condition' in self.medication_data:
            condition_var.set(self.medication_data['Taking_Condition'])
        else:
            condition_var.set('식후')  # 기본값

        def save_new_time():
            time_str = time_entry.get()
            try:
                datetime.strptime(time_str, "%H:%M")
                self.medication_data['Notification Time'] = time_str
                self.medication_data['Taking_Condition'] = condition_var.get()
                self.manager.update_medication(
                    self.medication_data['Product Name'],
                    {'Notification Time': time_str,
                     'Taking_Condition': condition_var.get()}
                )
                time_window.destroy()
                messagebox.showinfo("성공", "복용 시간이 변경되었습니다.")
            except ValueError:
                messagebox.showerror("오류", "올바른 시간 형식을 입력하세요 (HH:MM)")

        ttk.Button(time_frame, text="저장", command=save_new_time).pack(pady=10)

    def delete_medication(self):
        if messagebox.askyesno("확인", "이 약물을 삭제하시겠습니까?"):
            self.manager.delete_medication(self.medication_data['Product Name'])
            self.destroy()


class MedicationManager:
    def __init__(self, root):
        self.root = root
        self.root.title("내 복용 약물 관리")
        self.root.geometry("800x600")

        # 데이터 로드
        try:
            self.medication_db = pd.read_excel('medications.xlsx')
        except FileNotFoundError:
            self.medication_db = pd.DataFrame(columns=[
                'Product Name', 'Company Name', 'Main Ingredient',
                'Effectiveness', 'How to Take It', 'Precautions',
                'Warnings', 'Medications to Avoid', 'Major Side Effects',
                'Storage Instructions'
            ])

        try:
            self.my_medications = pd.read_excel('my_medications.xlsx')
        except FileNotFoundError:
            self.my_medications = pd.DataFrame(columns=[
                'Product Name', 'Company Name', 'Main Ingredient',
                'Effectiveness', 'How to Take It', 'Precautions',
                'Warnings', 'Medications to Avoid', 'Major Side Effects',
                'Storage Instructions', 'Notification Time'
            ])

        self.create_main_screen()
        self.check_notifications()

    def create_main_screen(self):
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 상단 타이틀
        title_label = ttk.Label(self.main_frame,
                                text="내 복용 약물",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 10))

        # 약물 추가 버튼
        add_button = ttk.Button(self.main_frame,
                                text="복용 약물 추가",
                                command=self.show_add_screen)
        add_button.pack(pady=(0, 20))

        # 스크롤 가능한 캔버스 생성
        self.canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame,
                                  orient=tk.VERTICAL,
                                  command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0),
                                  window=self.scrollable_frame,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 현재 복용 중인 약물 표시
        self.update_medication_list()

    def update_medication_list(self):
        # 기존 배너 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 약물 배너 추가
        for _, medication in self.my_medications.iterrows():
            banner = MedicationBanner(self.scrollable_frame,
                                      medication,
                                      self)
            banner.pack(fill=tk.X, padx=5, pady=5)

    def show_add_screen(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("복용 약물 추가")
        add_window.geometry("500x400")

        # 검색 프레임
        search_frame = ttk.Frame(add_window)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="약물 검색:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 검색 결과 트리뷰
        columns = ('제품명', '회사명', '주요 성분')
        search_tree = ttk.Treeview(add_window, columns=columns, show='headings')

        for col in columns:
            search_tree.heading(col, text=col)

        search_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def search_medications(*args):
            search_text = search_var.get().lower()
            for item in search_tree.get_children():
                search_tree.delete(item)

            for _, row in self.medication_db.iterrows():
                if (search_text in str(row['Product Name']).lower() or
                        search_text in str(row['Company Name']).lower() or
                        search_text in str(row['Main Ingredient']).lower()):
                    search_tree.insert('', tk.END, values=(
                        row['Product Name'],
                        row['Company Name'],
                        row['Main Ingredient']
                    ))

        search_var.trace('w', search_medications)

        def add_selected_medication():
            selected_item = search_tree.selection()
            if not selected_item:
                messagebox.showwarning("경고", "약물을 선택해주세요.")
                return

            selected_values = search_tree.item(selected_item)['values']
            selected_name = selected_values[0]

            # 이미 추가된 약물인지 확인
            if not self.my_medications[
                self.my_medications['Product Name'] == selected_name
            ].empty:
                messagebox.showwarning("경고", "이미 추가된 약물입니다.")
                return

            # 선택된 약물의 전체 정보 가져오기
            medication_info = self.medication_db[
                self.medication_db['Product Name'] == selected_name
                ].iloc[0]

            # 알림 시간 설정 창
            self.set_notification_time(medication_info, add_window)

        ttk.Button(add_window,
                   text="선택 약물 추가",
                   command=add_selected_medication).pack(pady=10)

    def set_notification_time(self, medication_info, parent_window):
        time_window = tk.Toplevel(parent_window)
        time_window.title("복용 시간 설정")
        time_window.geometry("400x300")

        time_frame = ttk.Frame(time_window)
        time_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 시간 입력
        ttk.Label(time_frame, text="복용 시간:").pack()
        time_entry = ttk.Entry(time_frame)
        time_entry.pack(pady=5)
        ttk.Label(time_frame, text="형식: HH:MM (예: 09:00)").pack()

        # 복용 조건 선택
        ttk.Label(time_frame, text="\n복용 조건:").pack()
        condition_var = tk.StringVar(value='식후')  # 기본값

        conditions = {
            '식전': '식사하기 30분 전에 복용하세요.',
            '식후': '식사 직후에 복용하세요.',
            '공복': '식사와 식사 사이 충분한 시간이 지난 후 복용하세요.\n(보통 식사 2시간 후)'
        }

        for condition in conditions.keys():
            ttk.Radiobutton(time_frame,
                            text=condition,
                            variable=condition_var,
                            value=condition).pack()

        # 설명 레이블
        explanation_label = ttk.Label(time_frame,
                                      text=conditions['식후'],  # 기본값 설명
                                      wraplength=350,
                                      justify='left')
        explanation_label.pack(pady=10)

        def update_explanation(*args):
            selected = condition_var.get()
            if selected in conditions:
                explanation_label.config(text=conditions[selected])

        condition_var.trace('w', update_explanation)

        def save_with_time():
            time_str = time_entry.get()
            try:
                datetime.strptime(time_str, "%H:%M")
                medication_info_dict = medication_info.to_dict()
                medication_info_dict['Notification Time'] = time_str
                medication_info_dict['Taking_Condition'] = condition_var.get()

                self.my_medications = pd.concat([
                    self.my_medications,
                    pd.DataFrame([medication_info_dict])
                ], ignore_index=True)

                self.my_medications.to_excel('my_medications.xlsx', index=False)
                self.update_medication_list()

                time_window.destroy()
                parent_window.destroy()
                messagebox.showinfo("성공", "약물이 추가되었습니다.")

            except ValueError:
                messagebox.showerror("오류", "올바른 시간 형식을 입력하세요 (HH:MM)")

        ttk.Button(time_frame, text="저장", command=save_with_time).pack(pady=10)

    def update_medication(self, product_name, updates):
        mask = self.my_medications['Product Name'] == product_name
        for field, value in (updates.items() if isinstance(updates, dict) else [('Notification Time', updates)]):
            self.my_medications.loc[mask, field] = value
        self.my_medications.to_excel('my_medications.xlsx', index=False)
        self.update_medication_list()

    def delete_medication(self, product_name):
        self.my_medications = self.my_medications[
            self.my_medications['Product Name'] != product_name
            ]
        self.my_medications.to_excel('my_medications.xlsx', index=False)

    def check_notifications(self):
        current_time = datetime.now().strftime("%H:%M")
        for _, medication in self.my_medications.iterrows():
            if medication['Notification Time'] == current_time:
                messagebox.showinfo("복용 알림",
                                    f"{medication['Product Name']} 복용 시간입니다!")

        # 1분마다 알림 체크
        self.root.after(60000, self.check_notifications)

def main():
        root = tk.Tk()
        app = MedicationManager(root)
        root.mainloop()

if __name__ == "__main__":
        main()