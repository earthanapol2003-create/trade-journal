import os
import tkinter as tk
from tkinter import messagebox
from database import get_all_csv_rows

def open_equity_chart_window(parent_root, bg_main, card_bg, text_main, text_muted, accent_primary, accent_cyan, accent_purple, green_color, red_color):
    rows = get_all_csv_rows()
    if not rows:
        messagebox.showwarning("แจ้งเตือน", "ยังไม่มีข้อมูลประวัติการเทรดให้สร้างกราฟครับ")
        return

    eq_win = tk.Toplevel(parent_root)
    eq_win.title("📊 กราฟความเติบโตของพอร์ต (Institutional Equity Curve)")
    eq_win.geometry("960x680")
    eq_win.configure(bg=bg_main)
    eq_win.resizable(False, False)

    header_frame = tk.Frame(eq_win, bg=bg_main)
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    tk.Label(header_frame, text="📊 EQUITY CURVE PERFORMANCE ANALYSIS", font=("Tahoma", 15, "bold"), fg=accent_cyan, bg=bg_main).pack(anchor="w")
    tk.Label(header_frame, text="กราฟแสดงเส้นทางการเติบโตของยอดเงินพอร์ตสุทธิ พร้อมจำลองพื้นที่สะสมกำไร", font=("Tahoma", 11), fg=text_muted, bg=bg_main).pack(anchor="w", pady=(2, 0))

    sorted_rows = sorted(rows, key=lambda x: x[0] if len(x)>0 else "")
    
    # คำนวณกราฟพอร์ตเริ่มต้นจาก 0
    points = [(0, 0.0, "เริ่มต้น", "Initial Equity")]
    current_eq = 0.0

    for idx, row in enumerate(sorted_rows, start=1):
        if len(row) >= 5:
            date, sym, act = row[0], row[1], row[2]
            try:
                pnl_f = float(row[3]) if row[3] else 0.0
                val_f = float(row[4]) if row[4] else 0.0
                
                if "ฝากเงิน" in act:
                    current_eq += val_f
                elif "ถอนเงินออก" in act:
                    current_eq -= val_f
                else:
                    current_eq += pnl_f

                points.append((idx, current_eq, date, f"{sym} ({act})"))
            except ValueError:
                pass

    if len(points) <= 1:
        messagebox.showwarning("แจ้งเตือน", "ข้อมูลประวัติยังไม่เพียงพอสำหรับการวาดกราฟครับ")
        eq_win.destroy()
        return

    final_eq = points[-1][1]
    total_pnl = sum(float(r[3]) for r in rows if len(r) >= 5 and "ฝากเงิน" not in r[2] and "ถอนเงินออก" not in r[2])
    profit_color = green_color if total_pnl >= 0 else red_color

    stat_bar = tk.Frame(eq_win, bg=bg_main)
    stat_bar.pack(fill="x", padx=30, pady=(0, 12))

    def make_mini_card(parent, title, val, col):
        f = tk.Frame(parent, bg=card_bg, padx=14, pady=8, highlightbackground=col, highlightthickness=1)
        f.pack(side="left", fill="x", expand=True, padx=(0, 10) if parent.winfo_children() else 0)
        tk.Label(f, text=title, font=("Tahoma", 9, "bold"), fg=text_muted, bg=card_bg).pack(anchor="w")
        tk.Label(f, text=val, font=("Tahoma", 14, "bold"), fg=col, bg=card_bg).pack(anchor="w", pady=(2,0))

    make_mini_card(stat_bar, "ยอดพอร์ตปัจจุบัน", f"${final_eq:,.2f}", accent_cyan)
    make_mini_card(stat_bar, "กำไรสุทธิทั้งหมด", f"${total_pnl:,.2f}", profit_color)

    canvas_card = tk.Frame(eq_win, bg=card_bg, padx=15, pady=15, highlightbackground="#334155", highlightthickness=1)
    canvas_card.pack(fill="both", expand=True, padx=30, pady=(0, 25))

    canvas_w, canvas_h = 880, 430
    canvas = tk.Canvas(canvas_card, width=canvas_w, height=canvas_h, bg=card_bg, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    eq_values = [p[1] for p in points]
    min_eq, max_eq = min(eq_values) * 0.94, max(eq_values) * 1.06
    if max_eq == min_eq: max_eq += 100

    margin_x, margin_y = 90, 45
    draw_w, draw_h = canvas_w - (margin_x * 2), canvas_h - (margin_y * 2)

    def get_coords(i, eq):
        x = margin_x + (i / (len(points) - 1)) * draw_w if len(points) > 1 else margin_x
        y = canvas_h - margin_y - ((eq - min_eq) / (max_eq - min_eq)) * draw_h
        return x, y

    for i in range(6):
        val = min_eq + (i / 5) * (max_eq - min_eq)
        _, y = get_coords(0, val)
        canvas.create_line(margin_x, y, canvas_w - margin_x, y, fill="#1E293B", dash=(4, 4), width=1)
        canvas.create_text(margin_x - 14, y, text=f"${val:,.0f}", fill=text_muted, anchor="e", font=("Tahoma", 9, "bold"))

    coord_list = [get_coords(i, p[1]) for i, p in enumerate(points)]
    poly_points = [coord_list[0][0], canvas_h - margin_y] + [coord for xy in coord_list for coord in xy] + [coord_list[-1][0], canvas_h - margin_y]
    
    try:
        canvas.create_polygon(poly_points, fill="#172554", outline="")
    except Exception:
        pass

    for i in range(len(coord_list) - 1):
        x1, y1 = coord_list[i]
        x2, y2 = coord_list[i+1]
        canvas.create_line(x1, y1, x2, y2, fill=accent_cyan, width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)

    step_skip = max(1, len(points) // 8)
    for i, (x, y) in enumerate(coord_list):
        canvas.create_oval(x-5, y-5, x+5, y+5, fill=accent_purple, outline=text_main, width=2)
        if i == 0 or i == len(points) - 1 or i % step_skip == 0:
            canvas.create_text(x, canvas_h - margin_y + 16, text=points[i][2], fill=text_muted, font=("Tahoma", 9), angle=25)