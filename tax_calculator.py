import os
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

def open_tax_calculator(parent_root, bg_main, card_bg, input_bg, text_main, text_muted, accent_primary, accent_cyan, accent_amber, green_color, red_color, font_text, font_header, font_label):
    tax_win = tk.Toplevel(parent_root)
    tax_win.title("🇹🇭 เครื่องมือคำนวณ & ออกรายงานภาษี (TAX AUDIT REPORT)")
    tax_win.geometry("820x960")
    tax_win.configure(bg=bg_main)
    tax_win.resizable(False, False)

    tk.Label(tax_win, text="🇹🇭 คำนวณภาษีเงินได้โอนเข้าไทย & หักต้นทุนการเทรด", font=("Tahoma", 15, "bold"), fg=accent_cyan, bg=bg_main).pack(pady=(15, 3))
    tk.Label(tax_win, text="อ้างอิงตามเกณฑ์กรมสรรพากร (รองรับการหักต้นทุน/ค่าใช้จ่ายตามจริงตามหลักบัญชีธุรกิจ)", font=font_text, fg=text_muted, bg=bg_main).pack(pady=(0, 10))

    card = tk.Frame(tax_win, bg=card_bg, padx=18, pady=14, highlightbackground="#334155", highlightthickness=1)
    card.pack(fill="x", padx=20, pady=5)

    tk.Label(card, text="ปีที่นำเงินเข้าไทย (ปีภาษี):", font=font_text, fg=text_muted, bg=card_bg).grid(row=0, column=0, sticky="w", pady=4)
    current_year = datetime.now().year
    entry_year = tk.Entry(card, font=font_text, bg=input_bg, fg=text_main, insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#475569", width=22)
    entry_year.insert(0, str(current_year))
    entry_year.grid(row=0, column=1, pady=4, ipady=3)

    tk.Label(card, text="จำนวนเงินที่โอนเข้า (USD):", font=font_text, fg=text_muted, bg=card_bg).grid(row=1, column=0, sticky="w", pady=4)
    entry_usd = tk.Entry(card, font=font_text, bg=input_bg, fg=text_main, insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#475569", width=22)
    entry_usd.insert(0, "1000")
    entry_usd.grid(row=1, column=1, pady=4, ipady=3)

    tk.Label(card, text="อัตราแลกเปลี่ยน (บาท / USD):", font=font_text, fg=text_muted, bg=card_bg).grid(row=2, column=0, sticky="w", pady=4)
    entry_fx = tk.Entry(card, font=font_text, bg=input_bg, fg=text_main, insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#475569", width=22)
    entry_fx.insert(0, "35.5")
    entry_fx.grid(row=2, column=1, pady=4, ipady=3)

    tk.Label(card, text="หักต้นทุน/ค่าใช้จ่ายการเทรด (บาท):", font=font_text, fg=accent_amber, bg=card_bg).grid(row=3, column=0, sticky="w", pady=4)
    entry_expense = tk.Entry(card, font=font_text, bg=input_bg, fg=text_main, insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#475569", width=22)
    entry_expense.insert(0, "0")
    entry_expense.grid(row=3, column=1, pady=4, ipady=3)

    res_frame = tk.Frame(tax_win, bg=card_bg, padx=18, pady=12, highlightbackground=accent_primary, highlightthickness=1)
    res_frame.pack(fill="x", padx=20, pady=8)

    lbl_thb_val = tk.Label(res_frame, text="เงินบาทที่ได้รับรวม: ฿0.00", font=("Tahoma", 11, "bold"), fg=text_main, bg=card_bg)
    lbl_thb_val.pack(anchor="w", pady=2)

    lbl_deduct_val = tk.Label(res_frame, text="หักต้นทุน/ค่าใช้จ่ายการเทรดจริง: -฿0.00", font=font_text, fg=accent_amber, bg=card_bg)
    lbl_deduct_val.pack(anchor="w", pady=2)

    lbl_allowance_val = tk.Label(res_frame, text="หักค่าลดหย่อนส่วนตัวพื้นฐาน: -฿60,000.00", font=font_text, fg=text_muted, bg=card_bg)
    lbl_allowance_val.pack(anchor="w", pady=2)

    lbl_net_income = tk.Label(res_frame, text="เงินได้สุทธิที่ต้องเสียภาษี: ฿0.00", font=("Tahoma", 11, "bold"), fg=accent_cyan, bg=card_bg)
    lbl_net_income.pack(anchor="w", pady=2)

    lbl_tax_payable = tk.Label(res_frame, text="รวมภาษีที่ต้องชำระทั้งสิ้น: ฿0.00", font=("Tahoma", 13, "bold"), fg=green_color, bg=card_bg)
    lbl_tax_payable.pack(anchor="w", pady=(8, 2))

    table_frame = tk.Frame(tax_win, bg=card_bg, padx=10, pady=10, highlightbackground="#334155", highlightthickness=1)
    table_frame.pack(fill="both", expand=True, padx=20, pady=5)

    tk.Label(table_frame, text="📊 ตารางแสดงการคำนวณภาษีทีละขั้นบันได (Progressive Breakdown)", font=font_header, fg=accent_cyan, bg=card_bg).pack(anchor="w", pady=(0, 6))

    columns = ("Bracket", "TaxRate", "TaxableChunk", "TaxAmount")
    tax_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
    
    tax_tree.heading("Bracket", text="ช่วงเงินได้สุทธิ (บาท)")
    tax_tree.heading("TaxRate", text="อัตราภาษี")
    tax_tree.heading("TaxableChunk", text="เงินได้ในขั้นนี้ (บาท)")
    tax_tree.heading("TaxAmount", text="ภาษีที่คิดในขั้นนี้ (บาท)")

    tax_tree.column("Bracket", width=180, anchor="center")
    tax_tree.column("TaxRate", width=80, anchor="center")
    tax_tree.column("TaxableChunk", width=150, anchor="e")
    tax_tree.column("TaxAmount", width=150, anchor="e")

    tax_tree.pack(fill="both", expand=True, pady=5)

    last_tax_details = {}

    def calculate_tax():
        nonlocal last_tax_details
        for item in tax_tree.get_children():
            tax_tree.delete(item)

        try:
            tax_year = int(entry_year.get().strip())
            usd = float(entry_usd.get().strip())
            fx = float(entry_fx.get().strip())
            expense_deduction = float(entry_expense.get().strip() or 0.0)
            
            thb = usd * fx
            lbl_thb_val.config(text=f"เงินบาทที่ได้รับรวม: ฿{thb:,.2f} THB")
            lbl_deduct_val.config(text=f"หักต้นทุน/ค่าใช้จ่ายการเทรดจริง: -฿{expense_deduction:,.2f} THB")

            personal_allowance = 60000.0
            income_after_expense = max(0.0, thb - expense_deduction)
            taxable_income = max(0.0, income_after_expense - personal_allowance)
            
            lbl_net_income.config(text=f"เงินได้สุทธิที่ต้องเสียภาษี: ฿{taxable_income:,.2f} THB")

            brackets = [
                (0, 150000, 0.0, "0%", "0 - 150,000"),
                (150000, 300000, 0.05, "5%", "150,001 - 300,000"),
                (300000, 500000, 0.10, "10%", "300,001 - 500,000"),
                (500000, 750000, 0.15, "15%", "500,001 - 750,000"),
                (750000, 1000000, 0.20, "20%", "750,001 - 1,000,000"),
                (1000000, 2000000, 0.25, "25%", "1,000,001 - 2,000,000"),
                (2000000, 5000000, 0.30, "30%", "2,000,001 - 5,000,000"),
                (5000000, float('inf'), 0.35, "35%", "5,000,001 ขึ้นไป")
            ]

            total_tax = 0.0
            breakdown_list = []
            for b_min, b_max, rate, rate_str, b_label in brackets:
                if taxable_income > b_min:
                    chunk_limit = b_max if b_max != float('inf') else taxable_income
                    chunk = min(taxable_income, chunk_limit) - b_min
                    if chunk > 0:
                        chunk_tax = chunk * rate
                        total_tax += chunk_tax
                        tax_tree.insert("", "end", values=(b_label, rate_str, f"{chunk:,.2f}", f"{chunk_tax:,.2f}"))
                        breakdown_list.append((b_label, rate_str, chunk, chunk_tax))

            lbl_tax_payable.config(text=f"รวมภาษีที่ต้องชำระทั้งสิ้น: ฿{total_tax:,.2f} THB", fg=red_color if total_tax > 0 else green_color)

            last_tax_details = {
                "year": tax_year, "usd": usd, "fx": fx, "thb": thb,
                "expense": expense_deduction, "allowance": personal_allowance,
                "taxable": taxable_income, "tax": total_tax, "breakdown": breakdown_list
            }
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกตัวเลขปี จำนวนเงิน และอัตราแลกเปลี่ยนให้ถูกต้อง")

    def generate_tax_report_pdf():
        if not last_tax_details:
            calculate_tax()
        d = last_tax_details
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("HTML Report / PDF Print", "*.html"), ("All Files", "*.*")],
            title="บันทึกรายงานภาษีสำหรับยื่นสรรพากร", initialfile=f"Tax_Audit_Report_{d['year']}.html"
        )
        if file_path:
            rows_html = "".join([f'<tr><td style="padding:10px; border:1px solid #cbd5e1; text-align:center;">{l}</td><td style="padding:10px; border:1px solid #cbd5e1; text-align:center;">{r}</td><td style="padding:10px; border:1px solid #cbd5e1; text-align:right;">฿{c:,.2f}</td><td style="padding:10px; border:1px solid #cbd5e1; text-align:right;">฿{t:,.2f}</td></tr>' for l, r, c, t in d['breakdown']])
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="th">
            <head>
                <meta charset="UTF-8">
                <title>รายงานสรุปการคำนวณภาษีเงินได้นำเข้าจากต่างประเทศ ปีภาษี {d['year']}</title>
                <style>
                    body {{ font-family: 'Tahoma', sans-serif; padding: 40px; color: #1e293b; background: #fff; max-width: 800px; margin: auto; }}
                    .header {{ text-align: center; border-bottom: 2px solid #0284c7; padding-bottom: 15px; margin-bottom: 25px; }}
                    .header h2 {{ margin: 0; color: #0f172a; font-size: 22px; }}
                    .header p {{ margin: 5px 0 0 0; color: #64748b; font-size: 14px; }}
                    .box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th {{ padding: 10px; border: 1px solid #cbd5e1; font-size: 14px; background: #f1f5f9; text-align: center; }}
                    td {{ font-size: 14px; padding: 10px; border: 1px solid #cbd5e1; }}
                    .summary-total {{ font-size: 18px; font-weight: bold; color: #0284c7; text-align: right; margin-top: 20px; }}
                    .legal-note {{ font-size: 13px; color: #475569; background: #fffbeb; border-left: 4px solid #f59e0b; padding: 14px; margin-top: 25px; line-height: 1.5; }}
                    .print-btn {{ display: block; width: 100%; background: #059669; color: white; padding: 14px; text-align: center; font-size: 16px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 25px; }}
                    .print-btn:hover {{ background: #047857; }}
                    @media print {{ .print-btn {{ display: none; }} }}
                </style>
            </head>
            <body>
                <button class="print-btn" onclick="window.print()">🖨️ คลิกที่นี่เพื่อพิมพ์เอกสาร / บันทึกเป็น PDF</button>
                <div class="header">
                    <h2>หนังสือสรุปการคำนวณภาษีเงินได้บุคคลธรรมดา (เงินได้ต่างประเทศ)</h2>
                    <p>ออกโดยระบบ Systematic Trader Pro Audit Engine — สำหรับประกอบการแสดงรายการภาษีปี {d['year']}</p>
                </div>
                <div class="box">
                    <h3 style="margin-top:0; font-size: 16px; color:#0369a1;">1. ข้อมูลการนำเงินเข้าและอัตราแลกเปลี่ยน</h3>
                    <p><b>ปีภาษีที่นำเงินเข้า:</b> {d['year']}</p>
                    <p><b>จำนวนเงินโอนกลับเข้าไทย:</b> ${d['usd']:,.2f} USD</p>
                    <p><b>อัตราแลกเปลี่ยนอ้างอิง:</b> ฿{d['fx']:,.2f} THB / USD</p>
                    <p style="font-size: 15px; font-weight: bold; color: #0f172a;"><b>รวมเป็นเงินได้พึงประเมินสุทธิ:</b> ฿{d['thb']:,.2f} THB</p>
                </div>
                <div class="box">
                    <h3 style="margin-top:0; font-size: 16px; color:#0369a1;">2. การหักค่าใช้จ่ายและค่าลดหย่อนตามกฎหมาย</h3>
                    <p><b>หักต้นทุน/ค่าใช้จ่ายการเทรดจริง:</b> -฿{d['expense']:,.2f} THB</p>
                    <p><b>หักค่าลดหย่อนส่วนตัวพื้นฐาน (มาตรา 47):</b> -฿{d['allowance']:,.2f} THB</p>
                    <hr style="border:0; border-top:1px solid #cbd5e1;">
                    <p style="font-size: 16px; font-weight: bold; color: #0284c7;"><b>คงเหลือเงินได้สุทธิที่นำไปคำนวณภาษี:</b> ฿{d['taxable']:,.2f} THB</p>
                </div>
                <h3 style="font-size: 16px; color:#0369a1;">3. รายละเอียดคำนวณภาษีอัตราก้าวหน้า (Progressive Tax Rate)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ช่วงเงินได้สุทธิ (บาท)</th>
                            <th>อัตราภาษี</th>
                            <th>เงินได้ในขั้นนี้ (บาท)</th>
                            <th>ภาษีที่คิดในขั้นนี้ (บาท)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div class="summary-total">รวมประเมินภาษีเงินได้ที่ต้องชำระทั้งสิ้น: ฿{d['tax']:,.2f} THB</div>
                <div class="legal-note"><b>📌 อ้างอิงข้อกฎหมาย:</b> รายงานการหักต้นทุนคำนวณตามหลักการบัญชีต้นทุนจริงเพื่อประกอบการยื่นแบบ ภ.ง.ด.90</div>
            </body>
            </html>
            """
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            webbrowser.open(file_path)

    tk.Button(tax_win, text="🧮 คำนวณภาษีและแสดงรายละเอียด", font=font_label, bg=accent_primary, fg="white", bd=0, pady=8, cursor="hand2", command=calculate_tax).pack(fill="x", padx=20, pady=5)
    tk.Button(tax_win, text="📄 สร้างรายงานภาษีสำหรับพิมพ์เป็น PDF (Tax Audit Report)", font=font_label, bg="#059669", fg="white", bd=0, pady=9, cursor="hand2", command=generate_tax_report_pdf).pack(fill="x", padx=20, pady=5)
    calculate_tax()