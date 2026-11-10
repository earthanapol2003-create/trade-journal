import csv
import os
import shutil
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

from database import FILENAME, CONFIG_FILE, RECEIPTS_DIR, CHARTS_DIR, BACKUP_DIR, init_file, get_all_csv_rows
from chart_window import open_equity_chart_window
from tax_calculator import open_tax_calculator

# พยายาม Import pandas และ openpyxl สำหรับจัดการไฟล์ Excel
try:
    import pandas as pd
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_EXCEL_LIBS = True
except ImportError:
    HAS_EXCEL_LIBS = False

class LargeThaiTerminalJournal:
    def __init__(self, root):
        self.root = root
        self.root.title("SYSTEMATIC TRADER PRO — Production & Tax Audit Edition")
        self.root.geometry("1480x900")
        self.root.minsize(1100, 780)
        
        self.BG_MAIN = "#0B0F19"
        self.CARD_BG = "#131C31"
        self.INPUT_BG = "#1E293B"
        self.INPUT_DISABLED = "#0F172A"
        self.TEXT_MAIN = "#F8FAFC"
        self.TEXT_MUTED = "#94A3B8"
        
        self.ACCENT_PRIMARY = "#6366F1"
        self.ACCENT_HOVER = "#4F46E5"
        self.ACCENT_CYAN = "#06B6D4"
        self.ACCENT_PURPLE = "#A855F7"
        self.ACCENT_AMBER = "#F59E0B"
        self.GREEN_COLOR = "#10B981"
        self.RED_COLOR = "#EF4444"
        self.BLUE_COLOR = "#3B82F6"
        
        self.FONT_TITLE = ("Tahoma", 16, "bold")
        self.FONT_HEADER = ("Tahoma", 12, "bold")
        self.FONT_LABEL = ("Tahoma", 11, "bold")
        self.FONT_TEXT = ("Tahoma", 11)
        self.FONT_CARD_TITLE = ("Tahoma", 10, "bold")
        self.FONT_CARD_VAL = ("Tahoma", 16, "bold")

        self.root.configure(bg=self.BG_MAIN)
        self.setup_styles()
        
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.selected_receipt_path = ""
        self.selected_chart_path = ""
        
        # TOP BAR
        top_bar = tk.Frame(root, bg=self.BG_MAIN)
        top_bar.grid(row=0, column=0, sticky="ew", padx=25, pady=(12, 8))
        top_bar.columnconfigure(1, weight=1)
        
        title_frame = tk.Frame(top_bar, bg=self.BG_MAIN)
        title_frame.grid(row=0, column=0, sticky="w")
        tk.Label(title_frame, text="⚡ SYSTEMATIC TRADER PRO", font=self.FONT_TITLE, fg=self.TEXT_MAIN, bg=self.BG_MAIN).pack(side="left")
        tk.Label(title_frame, text="Institutional Terminal", font=self.FONT_TEXT, fg=self.ACCENT_CYAN, bg=self.BG_MAIN).pack(side="left", padx=12)

        tools_frame = tk.Frame(top_bar, bg=self.BG_MAIN)
        tools_frame.grid(row=0, column=1, sticky="e")

        self.create_top_btn(tools_frame, "📊 กราฟพอร์ต", "#D97706", "#B45309", lambda: open_equity_chart_window(self.root, self.BG_MAIN, self.CARD_BG, self.TEXT_MAIN, self.TEXT_MUTED, self.ACCENT_PRIMARY, self.ACCENT_CYAN, self.ACCENT_PURPLE, self.GREEN_COLOR, self.RED_COLOR))
        self.create_top_btn(tools_frame, "🇹🇭 คำนวณภาษี", "#2563EB", "#1D4ED8", lambda: open_tax_calculator(self.root, self.BG_MAIN, self.CARD_BG, self.INPUT_BG, self.TEXT_MAIN, self.TEXT_MUTED, self.ACCENT_PRIMARY, self.ACCENT_CYAN, self.ACCENT_AMBER, self.GREEN_COLOR, self.RED_COLOR, self.FONT_TEXT, self.FONT_HEADER, self.FONT_LABEL))
        self.create_top_btn(tools_frame, "🟢 ส่งออก Excel", "#16A34A", "#15803D", self.export_journal_excel)
        self.create_top_btn(tools_frame, "📄 รายงาน PDF", "#059669", "#047857", self.export_journal_pdf)
        self.create_top_btn(tools_frame, "🛡️ สำรองข้อมูล", "#475569", "#334155", self.backup_database)

        # METRICS CARDS
        cards_frame = tk.Frame(root, bg=self.BG_MAIN)
        cards_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=6)
        
        self.card_balance_val = self.create_metric_card(cards_frame, "ยอดเงินพอร์ตสุทธิ", "$0.00", self.TEXT_MAIN, 0, self.ACCENT_PURPLE)
        self.card_pnl_val = self.create_metric_card(cards_frame, "กำไร/ขาดทุนสุทธิ (รวม)", "$0.00", self.TEXT_MAIN, 1, self.ACCENT_CYAN)
        self.card_withdraw_val = self.create_metric_card(cards_frame, "ยอดถอนเงินสะสม", "$0.00", self.ACCENT_AMBER, 2, self.ACCENT_AMBER)
        self.card_winrate_val = self.create_metric_card(cards_frame, "อัตราชนะ (WIN RATE)", "0.0%", self.GREEN_COLOR, 3, self.GREEN_COLOR)
        self.card_grade_val = self.create_metric_card(cards_frame, "เกรดวินัยการเทรด", "N/A", self.ACCENT_PRIMARY, 4, self.ACCENT_PRIMARY)

        # MAIN CONTAINER
        main_container = tk.Frame(root, bg=self.BG_MAIN)
        main_container.grid(row=2, column=0, sticky="nsew", padx=25, pady=(8, 15))
        main_container.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)

        # LEFT PANEL: FORM
        form_panel = tk.Frame(main_container, bg=self.CARD_BG, padx=20, pady=16, highlightbackground="#334155", highlightthickness=1)
        form_panel.grid(row=0, column=0, sticky="ns", padx=(0, 18))

        tk.Label(form_panel, text="📌 บันทึกออเดอร์ & พอร์ต", font=self.FONT_HEADER, fg=self.ACCENT_CYAN, bg=self.CARD_BG).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.create_form_field(form_panel, "วันที่เทรด:", 1, datetime.now().strftime("%Y-%m-%d"), "date")
        self.create_form_field(form_panel, "สินทรัพย์:", 2, "XAUUSD", "symbol")
        
        tk.Label(form_panel, text="ประเภทรายการ:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=3, column=0, sticky="w", pady=5)
        self.combo_action = ttk.Combobox(form_panel, values=["กำไร (Win)", "ขาดทุน (Loss)", "ฝากเงิน / เติมเงิน (Deposit)", "ถอนเงินออก (Withdrawal)"], state="readonly", width=18, font=self.FONT_TEXT)
        self.combo_action.current(0)
        self.combo_action.grid(row=3, column=1, pady=5)
        self.combo_action.bind("<<ComboboxSelected>>", self.on_action_change)

        self.create_form_field(form_panel, "กำไร/ขาดทุน ($):", 4, "", "pnl")
        self.create_form_field(form_panel, "ฝาก/ถอน เงิน ($):", 5, "0", "withdraw")
        self.create_form_field(form_panel, "เป้าหมาย R:R:", 6, "3", "rr")
        self.create_form_field(form_panel, "ทุนเทรด (ไม้):", 7, "3", "capital")
        
        tk.Label(form_panel, text="วินัยการเทรด:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=8, column=0, sticky="w", pady=5)
        self.combo_rule = ttk.Combobox(form_panel, values=["ทำตามระบบ 100%", "มีหลุดแผนเล็กน้อย", "FOMO / หัวร้อน"], state="readonly", width=18, font=self.FONT_TEXT)
        self.combo_rule.current(0)
        self.combo_rule.grid(row=8, column=1, pady=5)

        self.create_form_field(form_panel, "บันทึกเพิ่มเติม:", 9, "", "notes")

        tk.Label(form_panel, text="แนบไฟล์หลักฐาน:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=10, column=0, sticky="w", pady=6)
        attach_sub_frame = tk.Frame(form_panel, bg=self.CARD_BG)
        attach_sub_frame.grid(row=10, column=1, sticky="ew", pady=6)
        attach_sub_frame.columnconfigure(0, weight=1)
        attach_sub_frame.columnconfigure(1, weight=1)

        self.btn_upload = tk.Button(attach_sub_frame, text="📎 สลิป", font=("Tahoma", 10, "bold"), bg="#334155", fg="white", bd=0, pady=5, cursor="hand2", command=self.upload_receipt)
        self.btn_upload.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.btn_chart = tk.Button(attach_sub_frame, text="📈 กราฟ", font=("Tahoma", 10, "bold"), bg="#334155", fg="white", bd=0, pady=5, cursor="hand2", command=self.upload_chart)
        self.btn_chart.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self.btn_save = tk.Button(form_panel, text="💾 บันทึกข้อมูลออเดอร์", font=self.FONT_LABEL, bg=self.ACCENT_PRIMARY, fg="white", bd=0, pady=11, cursor="hand2", command=self.save_entry)
        self.btn_save.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(16, 5))
        self.bind_hover_effect(self.btn_save, self.ACCENT_PRIMARY, self.ACCENT_HOVER)

        # RIGHT PANEL: TABLE & ACTIONS
        right_container = tk.Frame(main_container, bg=self.BG_MAIN)
        right_container.grid(row=0, column=1, sticky="nsew")
        right_container.rowconfigure(0, weight=1)
        right_container.columnconfigure(0, weight=1)

        table_frame = tk.Frame(right_container, bg=self.CARD_BG, padx=16, pady=16, highlightbackground="#334155", highlightthickness=1)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        table_frame.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)

        filter_header_frame = tk.Frame(table_frame, bg=self.CARD_BG)
        filter_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(filter_header_frame, text="📜 ประวัติคำสั่งเทรดและการทำธุรกรรม", font=self.FONT_HEADER, fg=self.ACCENT_CYAN, bg=self.CARD_BG).pack(side="left")
        tk.Label(filter_header_frame, text="เลือกเดือน:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(side="left", padx=(18, 8))
        
        self.combo_month_filter = ttk.Combobox(filter_header_frame, values=["ทั้งหมด (All Time)"], state="readonly", width=18, font=self.FONT_TEXT)
        self.combo_month_filter.current(0)
        self.combo_month_filter.pack(side="left")
        self.combo_month_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_data())

        tree_container = tk.Frame(table_frame, bg=self.CARD_BG)
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        columns = ("Date", "Symbol", "PnL", "Withdraw", "RR", "Capital", "Rule", "Receipt", "Chart")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        
        headers = [("Date", "วันที่", 105), ("Symbol", "คู่เงิน", 80), ("PnL", "กำไร/ขาดทุน ($)", 125), 
                   ("Withdraw", "ฝาก/ถอน ($)", 110), ("RR", "เป้า R:R", 70), ("Capital", "ทุนไม้", 70), 
                   ("Rule", "วินัยการเทรด", 150), ("Receipt", "สลิปหลักฐาน", 95), ("Chart", "รูปกราฟ", 95)]
        
        for col, text, width in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col not in ["PnL", "Withdraw"] else "e")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", self.open_receipt_from_tree)

        self.tree.tag_configure("win", foreground=self.GREEN_COLOR)
        self.tree.tag_configure("loss", foreground=self.RED_COLOR)
        self.tree.tag_configure("deposit", foreground=self.BLUE_COLOR)
        self.tree.tag_configure("withdraw", foreground=self.ACCENT_AMBER)

        btn_action_frame = tk.Frame(right_container, bg=self.BG_MAIN)
        btn_action_frame.grid(row=1, column=0, sticky="ew")
        btn_action_frame.columnconfigure((0, 1, 2), weight=1)

        self.btn_view_receipt = tk.Button(btn_action_frame, text="🖼️ ดูสลิปหลักฐาน", font=self.FONT_LABEL, bg=self.ACCENT_PRIMARY, fg="white", bd=0, pady=9, cursor="hand2", command=self.view_selected_receipt)
        self.btn_view_receipt.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.bind_hover_effect(self.btn_view_receipt, self.ACCENT_PRIMARY, self.ACCENT_HOVER)

        self.btn_view_chart = tk.Button(btn_action_frame, text="📈 ดูรูปกราฟเทรด", font=self.FONT_LABEL, bg="#0284C7", fg="white", bd=0, pady=9, cursor="hand2", command=self.view_selected_chart)
        self.btn_view_chart.grid(row=0, column=1, sticky="ew", padx=6)
        self.bind_hover_effect(self.btn_view_chart, "#0284C7", "#0369A1")

        self.btn_delete = tk.Button(btn_action_frame, text="🗑️ ลบรายการที่เลือก", font=self.FONT_LABEL, bg=self.RED_COLOR, fg="white", bd=0, pady=9, cursor="hand2", command=self.delete_selected_entry)
        self.btn_delete.grid(row=0, column=2, sticky="ew", padx=(6, 0))
        self.bind_hover_effect(self.btn_delete, self.RED_COLOR, "#DC2626")

        # STATUS BAR
        self.status_bar = tk.Frame(root, bg=self.CARD_BG, height=34, highlightbackground="#334155", highlightthickness=1)
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=25, pady=(0, 12))
        
        self.lbl_pulse = tk.Label(self.status_bar, text="●", font=("Tahoma", 12, "bold"), fg=self.GREEN_COLOR, bg=self.CARD_BG)
        self.lbl_pulse.pack(side="left", padx=(12, 0), pady=4)
        self.lbl_status = tk.Label(self.status_bar, text=" ระบบเชื่อมต่อสำเร็จ — พร้อมใช้งานระดับสถาบัน", font=self.FONT_TEXT, fg=self.GREEN_COLOR, bg=self.CARD_BG)
        self.lbl_status.pack(side="left", padx=6, pady=4)
        self.lbl_clock = tk.Label(self.status_bar, text="", font=self.FONT_TEXT, fg=self.ACCENT_CYAN, bg=self.CARD_BG)
        self.lbl_clock.pack(side="right", padx=12, pady=4)
        
        self.update_live_clock()
        self.animate_pulse()
        self.on_action_change(None)
        self.refresh_all_data()

    def create_top_btn(self, parent, text, bg_color, hover_color, command):
        btn = tk.Button(parent, text=text, font=("Tahoma", 10, "bold"), bg=bg_color, fg="white", bd=0, padx=12, pady=6, cursor="hand2", command=command)
        btn.pack(side="left", padx=4)
        self.bind_hover_effect(btn, bg_color, hover_color)
        return btn

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.CARD_BG, foreground=self.TEXT_MAIN, fieldbackground=self.CARD_BG, rowheight=38, font=self.FONT_TEXT, borderwidth=0)
        style.configure("Treeview.Heading", background=self.INPUT_BG, foreground=self.TEXT_MUTED, font=self.FONT_HEADER, borderwidth=0)
        style.map("Treeview", background=[("selected", self.ACCENT_PRIMARY)])

    def bind_hover_effect(self, btn, normal_color, hover_color):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_color))

    def update_live_clock(self):
        self.lbl_clock.config(text=f"🕒 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')}")
        self.root.after(1000, self.update_live_clock)

    def animate_pulse(self):
        next_color = self.TEXT_MUTED if self.lbl_pulse.cget("fg") == self.GREEN_COLOR else self.GREEN_COLOR
        self.lbl_pulse.config(fg=next_color)
        self.root.after(800, self.animate_pulse)

    def create_metric_card(self, parent, title, initial_val, text_color, col_idx, border_color):
        card = tk.Frame(parent, bg=self.CARD_BG, padx=14, pady=10, highlightbackground=border_color, highlightthickness=1)
        card.grid(row=0, column=col_idx, sticky="ew", padx=(0 if col_idx==0 else 8, 0))
        parent.columnconfigure(col_idx, weight=1)
        tk.Label(card, text=title, font=self.FONT_CARD_TITLE, fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(anchor="w")
        val_label = tk.Label(card, text=initial_val, font=self.FONT_CARD_VAL, fg=text_color, bg=self.CARD_BG)
        val_label.pack(anchor="w", pady=(3, 0))
        return val_label

    def create_form_field(self, parent, label_text, row, default_val, field_name):
        tk.Label(parent, text=label_text, font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, font=self.FONT_TEXT, bg=self.INPUT_BG, fg=self.TEXT_MAIN, insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#475569", width=20)
        entry.insert(0, default_val)
        entry.grid(row=row, column=1, pady=5, ipady=4)
        setattr(self, f"entry_{field_name}", entry)

    def on_action_change(self, event):
        action = self.combo_action.get()
        if "ฝากเงิน" in action or "ถอนเงินออก" in action:
            self.entry_pnl.config(state="normal")
            self.entry_pnl.delete(0, tk.END)
            self.entry_pnl.insert(0, "0")
            self.entry_pnl.config(state="disabled", disabledbackground=self.INPUT_DISABLED)

            for field in [self.entry_rr, self.entry_capital]:
                field.config(state="normal")
                field.delete(0, tk.END)
                field.insert(0, "-")
                field.config(state="disabled", disabledbackground=self.INPUT_DISABLED)
        else:
            self.entry_pnl.config(state="normal", bg=self.INPUT_BG)
            if self.entry_pnl.get() == "0":
                self.entry_pnl.delete(0, tk.END)
            for field, val in [(self.entry_rr, "3"), (self.entry_capital, "3")]:
                field.config(state="normal", bg=self.INPUT_BG)
                if field.get() == "-":
                    field.delete(0, tk.END)
                    field.insert(0, val)

    def upload_receipt(self):
        file_path = filedialog.askopenfilename(title="เลือกรูปภาพสลิปหลักฐาน", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")])
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1]
                dest_path = os.path.join(RECEIPTS_DIR, f"Receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
                shutil.copy(file_path, dest_path)
                self.selected_receipt_path = dest_path
                self.btn_upload.config(text="✅ สลิปแล้ว", bg=self.GREEN_COLOR)
                messagebox.showinfo("สำเร็จ", "📎 แนบรูปสลิปหลักฐานเรียบร้อยแล้วครับ!")
            except Exception as e:
                messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    def upload_chart(self):
        file_path = filedialog.askopenfilename(title="เลือกรูปภาพกราฟหน้าจอเทรด", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")])
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1]
                dest_path = os.path.join(CHARTS_DIR, f"Chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
                shutil.copy(file_path, dest_path)
                self.selected_chart_path = dest_path
                self.btn_chart.config(text="✅ กราฟแล้ว", bg=self.GREEN_COLOR)
                messagebox.showinfo("สำเร็จ", "📈 แนบรูปกราฟเทรดเรียบร้อยแล้วครับ!")
            except Exception as e:
                messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    def save_entry(self):
        date_str = self.entry_date.get().strip()
        symbol = self.entry_symbol.get().strip().upper()
        action = self.combo_action.get()
        pnl_raw = self.entry_pnl.get().strip()
        withdraw_raw = self.entry_withdraw.get().strip()
        rule = self.combo_rule.get()
        notes = self.entry_notes.get().strip()

        if "ฝากเงิน" in action:
            pnl = 0.0
            try:
                withdraw = float(withdraw_raw) if withdraw_raw else 0.0
            except ValueError: withdraw = 0.0
            if withdraw <= 0:
                messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกจำนวนเงินที่ต้องการฝาก/เติมด้วยครับ")
                return
        elif "ถอนเงินออก" in action:
            pnl = 0.0
            try:
                withdraw = float(withdraw_raw) if withdraw_raw else 0.0
            except ValueError: withdraw = 0.0
            if withdraw <= 0:
                messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกจำนวนเงินที่ต้องการถอนออกด้วยครับ")
                return
        else:
            if not pnl_raw or pnl_raw == "-" or pnl_raw == "":
                messagebox.showwarning("แจ้งเตือน", "⚠️ กรุณากรอกตัวเลขกำไร / ขาดทุน ($) ก่อนทำการบันทึกข้อมูลครับ!")
                return
            withdraw = 0.0
            try:
                pnl_val = float(pnl_raw)
                pnl = -pnl_val if "ขาดทุน" in action and pnl_val > 0 else pnl_val
            except ValueError: pnl = 0.0

        self.entry_rr.config(state="normal")
        self.entry_capital.config(state="normal")
        rr_raw, capital_raw = self.entry_rr.get().strip(), self.entry_capital.get().strip()
        self.on_action_change(None)

        rr_display = f"{float(rr_raw.lower().replace('r',''))}R" if rr_raw and rr_raw != "-" else "-"
        capital_display = capital_raw if capital_raw and capital_raw != "-" else "-"

        with open(FILENAME, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([date_str, symbol, action, pnl, withdraw, rr_display, capital_display, rule, notes, self.selected_receipt_path, self.selected_chart_path])

        messagebox.showinfo("สำเร็จ", "✅ บันทึกรายการสำเร็จเรียบร้อยแล้วครับ!")
        self.entry_pnl.config(state="normal")
        self.entry_pnl.delete(0, tk.END)
        self.entry_withdraw.delete(0, tk.END)
        self.entry_withdraw.insert(0, "0")
        self.entry_notes.delete(0, tk.END)
        self.selected_receipt_path, self.selected_chart_path = "", ""
        self.btn_upload.config(text="📎 สลิป", bg="#334155")
        self.btn_chart.config(text="📈 กราฟ", bg="#334155")
        self.on_action_change(None)
        self.refresh_all_data()

    def view_selected_receipt(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาคลิกเลือกรายการที่ต้องการดูสลิปในตารางก่อนครับ")
            return
        rows = get_all_csv_rows()
        idx = len(rows) - 1 - list(self.tree.get_children()).index(selected[0])
        if 0 <= idx < len(rows) and len(rows[idx]) >= 10 and rows[idx][9].strip():
            if os.path.exists(rows[idx][9].strip()): webbrowser.open(os.path.abspath(rows[idx][9].strip()))
            else: messagebox.showerror("ไม่พบไฟล์", "ไม่พบไฟล์รูปสลิปในระบบ")
        else: messagebox.showinfo("ไม่มีหลักฐาน", "⚠️ รายการนี้ยังไม่ได้แนบรูปสลิปหลักฐานครับ")

    def view_selected_chart(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาคลิกเลือกรายการที่ต้องการดูกราฟในตารางก่อนครับ")
            return
        rows = get_all_csv_rows()
        idx = len(rows) - 1 - list(self.tree.get_children()).index(selected[0])
        if 0 <= idx < len(rows) and len(rows[idx]) >= 11 and rows[idx][10].strip():
            if os.path.exists(rows[idx][10].strip()): webbrowser.open(os.path.abspath(rows[idx][10].strip()))
            else: messagebox.showerror("ไม่พบไฟล์", "ไม่พบไฟล์รูปกราฟในระบบ")
        else: messagebox.showinfo("ไม่มีหลักฐาน", "⚠️ รายการนี้ยังไม่ได้แนบรูปกราฟหน้าจอครับ")

    def open_receipt_from_tree(self, event):
        self.view_selected_receipt()

    def backup_database(self):
        try:
            timestamp = datetime.now().strftime("%d-%m-%Y_%H%M%S")
            backup_sub = os.path.join(BACKUP_DIR, f"Backup_{timestamp}")
            os.makedirs(backup_sub)
            if os.path.exists(FILENAME): shutil.copy(FILENAME, backup_sub)
            if os.path.exists(CONFIG_FILE): shutil.copy(CONFIG_FILE, backup_sub)
            if os.path.exists(RECEIPTS_DIR): shutil.copytree(RECEIPTS_DIR, os.path.join(backup_sub, RECEIPTS_DIR))
            if os.path.exists(CHARTS_DIR): shutil.copytree(CHARTS_DIR, os.path.join(backup_sub, CHARTS_DIR))
            
            backups = sorted([os.path.join(BACKUP_DIR, d) for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))])
            if len(backups) > 5:
                for old in backups[:-5]: shutil.rmtree(old)
            messagebox.showinfo("สำเร็จ", f"🛡️ สำรองข้อมูลเรียบร้อยแล้ว!\n(Backup_{timestamp})")
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    def export_journal_excel(self):
        if not HAS_EXCEL_LIBS:
            messagebox.showerror("ต้องการแพ็กเกจเพิ่ม", "กรุณาติดตั้ง openpyxl และ pandas ก่อนใช้งาน โดยรันคำสั่ง:\npip install openpyxl pandas")
            return

        rows = get_all_csv_rows()
        if not rows:
            messagebox.showwarning("แจ้งเตือน", "ยังไม่มีข้อมูลให้ส่งออก")
            return
        
        available_years = sorted(list(set(r[0][:4] for r in rows if len(r) > 0 and len(r[0]) >= 4)), reverse=True)
        if not available_years:
            available_years = [datetime.now().strftime("%Y")]

        dialog = tk.Toplevel(self.root)
        dialog.title("🟢 เลือกช่วงปีสำหรับส่งออกไฟล์ Excel (Tax Audit)")
        dialog.geometry("420x260")
        dialog.configure(bg=self.CARD_BG)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="เลือกช่วงปีที่ต้องการออกรายงานการเงิน:", font=self.FONT_HEADER, fg=self.GREEN_COLOR, bg=self.CARD_BG).pack(pady=(20, 10))

        frame_years = tk.Frame(dialog, bg=self.CARD_BG)
        frame_years.pack(pady=5)

        tk.Label(frame_years, text="ตั้งแต่ปี:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=0, padx=5, sticky="w")
        from_combo = ttk.Combobox(frame_years, values=available_years, state="readonly", width=10, font=self.FONT_TEXT)
        from_combo.current(len(available_years) - 1)
        from_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame_years, text="ถึงปี:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=2, padx=5, sticky="w")
        to_combo = ttk.Combobox(frame_years, values=available_years, state="readonly", width=10, font=self.FONT_TEXT)
        to_combo.current(0)
        to_combo.grid(row=0, column=3, padx=5)

        all_time_var = tk.BooleanVar(value=False)
        chk_all = tk.Checkbutton(dialog, text="ส่งออกข้อมูลทั้งหมด (All Time)", variable=all_time_var, font=self.FONT_TEXT, fg=self.TEXT_MAIN, bg=self.CARD_BG, selectcolor=self.INPUT_BG, activebackground=self.CARD_BG, activeforeground=self.TEXT_MAIN)
        chk_all.pack(pady=12)

        def confirm_excel_export():
            is_all = all_time_var.get()
            start_y = from_combo.get()
            end_y = to_combo.get()

            if not is_all and start_y > end_y:
                messagebox.showerror("ข้อผิดพลาด", "ปีเริ่มต้นต้องไม่มากกว่าปีสิ้นสุดครับ")
                return

            dialog.destroy()

            file_label_str = "All_Time" if is_all else (f"{start_y}" if start_y == end_y else f"{start_y}_to_{end_y}")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel Files", "*.xlsx")], 
                initialfile=f"Tax_Audit_Report_{file_label_str}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )

            if file_path:
                export_data = []
                total_pnl_sum = 0.0
                total_dep_sum = 0.0
                total_wd_sum = 0.0

                for r in rows:
                    if len(r) >= 5:
                        date_val, sym_val, act_val = r[0], r[1], r[2]
                        row_year = date_val[:4]

                        if not is_all:
                            if not (start_y <= row_year <= end_y):
                                continue

                        try: p = float(r[3] or 0)
                        except ValueError: p = 0.0
                        try: w = float(r[4] or 0)
                        except ValueError: w = 0.0

                        deposit_val = w if "ฝากเงิน" in act_val else 0.0
                        withdraw_val = w if "ถอนเงินออก" in act_val else 0.0
                        pnl_val = p if ("ฝากเงิน" not in act_val and "ถอนเงินออก" not in act_val) else 0.0

                        if "ฝากเงิน" in act_val: total_dep_sum += w
                        elif "ถอนเงินออก" in act_val: total_wd_sum += w
                        else: total_pnl_sum += p

                        # ตัดคอลัมน์ที่ไม่จำเป็นออก เหลือเฉพาะข้อมูลการเงินและภาษีระดับสถาบัน
                        export_data.append({
                            "วันที่ (Date)": date_val,
                            "สินทรัพย์ (Symbol)": sym_val,
                            "ประเภทรายการ (Action)": act_val,
                            "กำไร/ขาดทุน (PnL $)": pnl_val,
                            "เงินฝาก (Deposit $)": deposit_val,
                            "เงินถอน (Withdraw $)": withdraw_val
                        })

                if not export_data:
                    messagebox.showwarning("แจ้งเตือน", "ไม่พบข้อมูลการเทรดในช่วงปีที่เลือกครับ")
                    return

                try:
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "Tax Audit Statement"
                    ws.views.sheetView[0].showGridLines = True

                    headers = list(export_data[0].keys())
                    ws.append(headers)

                    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
                    header_font = Font(name="Tahoma", size=11, bold=True, color="FFFFFF")
                    align_center = Alignment(horizontal="center", vertical="center")
                    align_right = Alignment(horizontal="right", vertical="center")
                    border_thin = Border(
                        left=Side(style='thin', color='CBD5E1'),
                        right=Side(style='thin', color='CBD5E1'),
                        top=Side(style='thin', color='CBD5E1'),
                        bottom=Side(style='thin', color='CBD5E1')
                    )

                    for col_idx in range(1, len(headers) + 1):
                        cell = ws.cell(row=1, column=col_idx)
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = align_center
                        cell.border = border_thin

                    ws.row_dimensions[1].height = 26

                    for row_idx, item in enumerate(export_data, start=2):
                        row_vals = list(item.values())
                        ws.append(row_vals)
                        ws.row_dimensions[row_idx].height = 22

                        for col_idx in range(1, len(row_vals) + 1):
                            cell = ws.cell(row=row_idx, column=col_idx)
                            cell.font = Font(name="Tahoma", size=10)
                            cell.border = border_thin

                            if col_idx in [4, 5, 6]:  # PnL, Deposit, Withdraw
                                cell.number_format = '$#,##0.00'
                                cell.alignment = align_right
                            elif col_idx in [1, 2, 3]:  # Date, Symbol, Action
                                cell.alignment = align_center

                    summary_row = len(export_data) + 2
                    ws.cell(row=summary_row, column=1, value="รวมสุทธิ (Total)").font = Font(name="Tahoma", size=10, bold=True)
                    ws.cell(row=summary_row, column=4, value=total_pnl_sum).number_format = '$#,##0.00'
                    ws.cell(row=summary_row, column=5, value=total_dep_sum).number_format = '$#,##0.00'
                    ws.cell(row=summary_row, column=6, value=total_wd_sum).number_format = '$#,##0.00'

                    for c in range(1, len(headers) + 1):
                        cell = ws.cell(row=summary_row, column=c)
                        cell.font = Font(name="Tahoma", size=10, bold=True)
                        cell.border = Border(top=Side(style='thin', color='000000'), bottom=Side(style='double', color='000000'))
                        if c in [4, 5, 6]: cell.alignment = align_right

                    for col in ws.columns:
                        max_len = max(len(str(cell.value or '')) for cell in col)
                        col_letter = get_column_letter(col[0].column)
                        ws.column_dimensions[col_letter].width = max(max_len + 6, 18)

                    wb.save(file_path)
                    messagebox.showinfo("สำเร็จ", f"🟢 ส่งออกรายงาน Excel (Tax Audit) เรียบร้อยแล้ว!\nบันทึกที่: {file_path}")
                except Exception as e:
                    messagebox.showerror("เกิดข้อผิดพลาด", str(e))

        tk.Button(dialog, text="🟢 ยืนยันส่งออก Excel", font=self.FONT_LABEL, bg="#16A34A", fg="white", bd=0, padx=20, pady=8, cursor="hand2", command=confirm_excel_export).pack(pady=10)

    def export_journal_pdf(self):
        rows = get_all_csv_rows()
        if not rows:
            messagebox.showwarning("แจ้งเตือน", "ยังไม่มีข้อมูลให้ส่งออก")
            return
        
        available_years = sorted(list(set(r[0][:4] for r in rows if len(r) > 0 and len(r[0]) >= 4)), reverse=True)
        if not available_years:
            available_years = [datetime.now().strftime("%Y")]

        dialog = tk.Toplevel(self.root)
        dialog.title("📅 เลือกช่วงปีสำหรับพิมพ์รายงาน PDF")
        dialog.geometry("420x260")
        dialog.configure(bg=self.CARD_BG)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="เลือกช่วงปีที่ต้องการออกรายงานภาษี:", font=self.FONT_HEADER, fg=self.ACCENT_CYAN, bg=self.CARD_BG).pack(pady=(20, 10))

        frame_years = tk.Frame(dialog, bg=self.CARD_BG)
        frame_years.pack(pady=5)

        tk.Label(frame_years, text="ตั้งแต่ปี:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=0, padx=5, sticky="w")
        from_combo = ttk.Combobox(frame_years, values=available_years, state="readonly", width=10, font=self.FONT_TEXT)
        from_combo.current(len(available_years) - 1)
        from_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame_years, text="ถึงปี:", font=self.FONT_TEXT, fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=2, padx=5, sticky="w")
        to_combo = ttk.Combobox(frame_years, values=available_years, state="readonly", width=10, font=self.FONT_TEXT)
        to_combo.current(0)
        to_combo.grid(row=0, column=3, padx=5)

        all_time_var = tk.BooleanVar(value=False)
        chk_all = tk.Checkbutton(dialog, text="ส่งออกข้อมูลทั้งหมด (All Time)", variable=all_time_var, font=self.FONT_TEXT, fg=self.TEXT_MAIN, bg=self.CARD_BG, selectcolor=self.INPUT_BG, activebackground=self.CARD_BG, activeforeground=self.TEXT_MAIN)
        chk_all.pack(pady=12)

        def confirm_export():
            is_all = all_time_var.get()
            start_y = from_combo.get()
            end_y = to_combo.get()

            if not is_all and start_y > end_y:
                messagebox.showerror("ข้อผิดพลาด", "ปีเริ่มต้นต้องไม่มากกว่าปีสิ้นสุดครับ")
                return

            dialog.destroy()

            file_label_str = "All_Time" if is_all else (f"{start_y}" if start_y == end_y else f"{start_y}_to_{end_y}")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html", 
                filetypes=[("HTML Report / PDF", "*.html")], 
                initialfile=f"Trading_Audit_{file_label_str}_{datetime.now().strftime('%Y%m%d')}.html"
            )
            
            if file_path:
                rows_html = ""
                total_pnl = 0.0
                total_deposits = 0.0
                total_withdraws = 0.0
                count_filtered = 0
                
                for i, r in enumerate(rows):
                    if len(r) >= 5:
                        date_val, sym_val, act_val = r[0], r[1], r[2]
                        row_year = date_val[:4]

                        if not is_all:
                            if not (start_y <= row_year <= end_y):
                                continue

                        count_filtered += 1
                        try: p = float(r[3] or 0)
                        except ValueError: p = 0.0
                        try: w = float(r[4] or 0)
                        except ValueError: w = 0.0
                            
                        pnl_str = "-"
                        dep_str = "-"
                        wd_str = "-"
                        pnl_color = "#334155"

                        if "ฝากเงิน" in act_val:
                            total_deposits += w
                            dep_str = f"${w:,.2f}"
                        elif "ถอนเงินออก" in act_val:
                            total_withdraws += w
                            wd_str = f"${w:,.2f}"
                        else:
                            total_pnl += p
                            pnl_color = "#059669" if p > 0 else ("#dc2626" if p < 0 else "#64748b")
                            pnl_str = f"+${p:,.2f}" if p > 0 else (f"-${abs(p):,.2f}" if p < 0 else "$0.00")

                        row_bg = "#f8fafc" if count_filtered % 2 == 1 else "#ffffff"

                        rows_html += f"""
                        <tr style="background-color: {row_bg};">
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: center; color: #334155; font-size: 13px;">{date_val}</td>
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: center; color: #0f172a; font-weight: bold; font-size: 13px;">{sym_val}</td>
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: center; color: #475569; font-size: 13px;">{act_val}</td>
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: right; color: {pnl_color}; font-weight: bold; font-size: 13px;">{pnl_str}</td>
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: right; color: #3b82f6; font-weight: 500; font-size: 13px;">{dep_str}</td>
                            <td style="padding: 12px 14px; border: 1px solid #cbd5e1; text-align: right; color: #d97706; font-weight: 500; font-size: 13px;">{wd_str}</td>
                        </tr>
                        """

                if count_filtered == 0:
                    messagebox.showwarning("แจ้งเตือน", "ไม่พบข้อมูลการเทรดในช่วงปีที่เลือกครับ")
                    return
                
                title_range_str = "ข้อมูลทั้งหมด (All Time)" if is_all else (f"ปี {start_y}" if start_y == end_y else f"ช่วงปี {start_y} ถึง {end_y}")

                html_content = f"""
                <!DOCTYPE html>
                <html lang="th">
                <head>
                    <meta charset="UTF-8">
                    <title>รายงานสรุปการเทรดเพื่อการตรวจสอบภาษี ({title_range_str})</title>
                    <style>
                        body {{ font-family: 'Tahoma', sans-serif; background-color: #f1f5f9; color: #1e293b; margin: 0; padding: 40px 20px; }}
                        .page-container {{ max-width: 960px; margin: auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
                        .header {{ border-bottom: 2px solid #cbd5e1; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end; }}
                        .header h2 {{ margin: 0; color: #0f172a; font-size: 22px; }}
                        .header p {{ margin: 5px 0 0 0; color: #64748b; font-size: 13px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; }}
                        th {{ background-color: #e2e8f0; color: #334155; padding: 12px 14px; border: 1px solid #cbd5e1; font-size: 13px; font-weight: bold; text-align: center; }}
                        .summary-grid {{ display: flex; gap: 15px; margin-top: 10px; }}
                        .summary-box {{ flex: 1; background: #f8fafc; border: 1px solid #cbd5e1; padding: 15px 18px; border-radius: 8px; }}
                        .print-btn {{ display: block; width: 100%; background: #059669; color: white; padding: 12px; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 25px; text-align: center; }}
                        .print-btn:hover {{ background: #047857; }}
                        @media print {{ .print-btn {{ display: none; }} body {{ background: #fff; padding: 0; }} .page-container {{ box-shadow: none; padding: 0; }} }}
                    </style>
                </head>
                <body>
                    <div class="page-container">
                        <button class="print-btn" onclick="window.print()">🖨️ พิมพ์รายงาน / บันทึกเป็น PDF (Tax Audit Ready)</button>
                        <div class="header">
                            <div>
                                <h2>รายงานสรุปผลการเทรดและธุรกรรม ({title_range_str})</h2>
                                <p>ระบบ Systematic Trader Pro — วันที่พิมพ์: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                            </div>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th style="width: 18%;">วันที่</th>
                                    <th style="width: 14%;">สินทรัพย์</th>
                                    <th style="width: 23%;">ประเภทรายการ</th>
                                    <th style="width: 15%; text-align: right;">กำไร/ขาดทุน (PnL)</th>
                                    <th style="width: 15%; text-align: right;">เงินฝาก (Deposit)</th>
                                    <th style="width: 15%; text-align: right;">เงินถอน (Withdraw)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows_html}
                            </tbody>
                        </table>
                        <div class="summary-grid">
                            <div class="summary-box">
                                <span style="font-size: 12px; color: #64748b; display: block; margin-bottom: 4px;">กำไรสุทธิรวม (Total PnL - สำหรับยื่นภาษี)</span>
                                <strong style="font-size: 16px; color: {'#059669' if total_pnl >= 0 else '#dc2626'};">${total_pnl:,.2f} USD</strong>
                            </div>
                            <div class="summary-box">
                                <span style="font-size: 12px; color: #64748b; display: block; margin-bottom: 4px;">ยอดเงินฝากรวม (Total Deposits)</span>
                                <strong style="font-size: 16px; color: #3b82f6;">${total_deposits:,.2f} USD</strong>
                            </div>
                            <div class="summary-box">
                                <span style="font-size: 12px; color: #64748b; display: block; margin-bottom: 4px;">ยอดเงินถอนรวม (Total Withdrawals)</span>
                                <strong style="font-size: 16px; color: #d97706;">${total_withdraws:,.2f} USD</strong>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    messagebox.showinfo("สำเร็จ", "✅ สร้างรายงานเรียบร้อยแล้ว!")
                    webbrowser.open(file_path)
                except Exception as e:
                    messagebox.showerror("เกิดข้อผิดพลาด", str(e))

        tk.Button(dialog, text="📄 ยืนยันสร้างรายงาน", font=self.FONT_LABEL, bg=self.ACCENT_PRIMARY, fg="white", bd=0, padx=20, pady=8, cursor="hand2", command=confirm_export).pack(pady=10)

    def delete_selected_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
            return
        if not messagebox.askyesno("ยืนยัน", "ต้องการลบรายการพร้อมไฟล์หลักฐานใช่หรือไม่?"): return
        
        rows = []
        if os.path.exists(FILENAME):
            with open(FILENAME, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows = list(reader)
        
        idx = len(rows) - 1 - list(self.tree.get_children()).index(selected[0])
        if 0 <= idx < len(rows):
            for path_idx in [9, 10]:
                if len(rows[idx]) > path_idx and rows[idx][path_idx].strip() and os.path.exists(rows[idx][path_idx].strip()):
                    try: os.remove(rows[idx][path_idx].strip())
                    except Exception: pass
            rows.pop(idx)
            with open(FILENAME, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if header: writer.writerow(header)
                writer.writerows(rows)
            self.refresh_all_data()
            messagebox.showinfo("สำเร็จ", "🗑️ ลบรายการเรียบร้อยแล้ว")

    def refresh_all_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows, months = get_all_csv_rows(), set()
        total_pnl, net_deposits, net_withdraws, trades, wins, score_sum = 0.0, 0.0, 0.0, 0, 0, 0.0

        for r in rows:
            if len(r) >= 8:
                months.add(r[0][:7])
                p = float(r[3] or 0)
                w = float(r[4] or 0)
                act = r[2]
                
                if "ฝากเงิน" in act:
                    net_deposits += w
                elif "ถอนเงินออก" in act:
                    net_withdraws += w
                else:
                    total_pnl += p
                    if p != 0:
                        if p > 0: wins += 1
                        trades += 1

                score_sum += 1.0 if "100%" in r[7] else (0.5 if "เล็กน้อย" in r[7] else 0.0)

        filter_opts = ["ทั้งหมด (All Time)"] + sorted(list(months), reverse=True)
        cur = self.combo_month_filter.get()
        self.combo_month_filter['values'] = filter_opts
        self.combo_month_filter.set(cur if cur in filter_opts else filter_opts[0])
        sel_month = self.combo_month_filter.get()

        f_pnl, f_trades, f_wins = 0.0, 0, 0
        for r in reversed(rows):
            if len(r) >= 8:
                date, sym, act, pnl_s, wd_s, rr, cap, rule = r[:8]
                has_rec = "📷 มีสลิป" if len(r) > 9 and r[9].strip() else "-"
                has_cht = "📈 มีกราฟ" if len(r) > 10 and r[10].strip() else "-"
                
                if sel_month != "ทั้งหมด (All Time)" and date[:7] != sel_month: continue
                
                try: p = float(pnl_s or 0)
                except ValueError: p = 0.0
                try: w = float(wd_s or 0)
                except ValueError: w = 0.0
                
                if "ฝากเงิน" not in act and "ถอนเงินออก" not in act:
                    f_pnl += p
                    if p != 0:
                        if p > 0: f_wins += 1
                        f_trades += 1
                
                if "ฝากเงิน" in act:
                    tag = "deposit"
                    disp_w = f"+${w:,.2f}"
                elif "ถอนเงินออก" in act:
                    tag = "withdraw"
                    disp_w = f"-${w:,.2f}"
                else:
                    tag = "win" if p > 0 else ("loss" if p < 0 else "")
                    disp_w = "-"

                disp_pnl = f"+${p:,.2f}" if p > 0 else (f"-${abs(p):,.2f}" if p < 0 else "-")
                self.tree.insert("", "end", values=(date, sym, disp_pnl, disp_w, rr, cap, rule, has_rec, has_cht), tags=(tag,))

        balance = net_deposits + total_pnl - net_withdraws
        dpnl = f_pnl if sel_month != "ทั้งหมด (All Time)" else total_pnl
        win_rate = (f_wins / f_trades * 100) if f_trades > 0 else 0.0

        self.card_balance_val.config(text=f"${balance:,.2f}")
        self.card_pnl_val.config(text=f"+${dpnl:,.2f}" if dpnl >= 0 else f"-${abs(dpnl):,.2f}", fg=self.GREEN_COLOR if dpnl >= 0 else self.RED_COLOR)
        self.card_withdraw_val.config(text=f"${net_withdraws:,.2f}")
        self.card_winrate_val.config(text=f"{win_rate:.1f}%")

        avg_score = (score_sum / len(rows) * 100) if rows else 0.0
        self.card_grade_val.config(text="เกรด A 🔥" if avg_score > 90 else ("เกรด B 👍" if avg_score > 70 else ("เกรด C ⚠️" if avg_score >= 50 else "เกรด D ❌")))

if __name__ == "__main__":
    init_file()
    root = tk.Tk()
    app = LargeThaiTerminalJournal(root)
    root.mainloop()