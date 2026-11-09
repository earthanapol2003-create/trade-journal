import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บให้รองรับมือถือและดูพรีเมียม
st.set_page_config(
    page_title="Systematic Trader Pro", page_icon="💎", layout="centered"
)

# ตกแต่ง CSS ธีมเข้มหรูหรา
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("💎 Systematic Trader Pro")
st.caption("🚀 Professional Trading Journal & Analytics (Mobile View)")
st.markdown("---")

FILENAME = "trading_journal.csv"

# โหลดข้อมูลจากไฟล์ CSV
try:
  df = pd.read_csv(FILENAME)
except Exception:
  df = pd.DataFrame()

if not df.empty:
  # ทำความสะอาดชื่อหัวตาราง
  df.columns = df.columns.astype(str).str.strip()

  # อ้างอิงตามโครงสร้างโปรแกรมคอมพิวเตอร์:
  # Index 0 = วันที่ (Date), Index 3 = กำไร/ขาดทุน (P&L), Index 4 = ยอดถอน (Withdraw)
  pnl_col = df.columns[3] if len(df.columns) > 3 else None

  # แปลงข้อมูลกำไรให้เป็นตัวเลขเพื่อนำมาคำนวณสถิติ
  if pnl_col:
    cleaned_pnl = (
        df[pnl_col]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    pnl_series = pd.to_numeric(cleaned_pnl, errors="coerce").fillna(0)

    total_trades = len(df)
    total_pnl = pnl_series.sum()
    wins = len(pnl_series[pnl_series > 0])
    losses = len(pnl_series[pnl_series < 0])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
  else:
    pnl_series = pd.Series([0] * len(df))
    total_trades = len(df)
    total_pnl = 0
    wins = 0
    losses = 0
    win_rate = 0

  # แสดงการ์ดสถิติหลัก
  col1, col2 = st.columns(2)
  with col1:
    st.metric(
        label="💰 กำไร/ขาดทุนรวม",
        value=f"${total_pnl:,.2f}",
        delta=f"{'+' if total_pnl >= 0 else ''}{total_pnl:,.2f}",
    )
  with col2:
    st.metric(label="🎯 Win Rate", value=f"{win_rate:.1f}%")

  col3, col4 = st.columns(2)
  with col3:
    st.metric(label="📊 เทรดทั้งหมด", value=f"{total_trades} ออเดอร์")
  with col4:
    st.metric(label="✅ ชนะ / ❌ แพ้", value=f"{wins} / {losses}")

  st.markdown("---")
  st.markdown("### 📋 ประวัติการเทรด (ย่อส่วนสำคัญ)")

  # เลือกแสดงผลเฉพาะคอลัมน์ที่ต้องการ: วัน/เดือน/ปี, กำไร/ขาดทุน, ถอน
  # ตรวจสอบว่ามีคอลัมน์ครบตามตำแหน่งไหม (Index 0, 3, 4)
  if len(df.columns) >= 5:
    display_df = df.iloc[:, [0, 3, 4]].copy()
    display_df.columns = [
        "วัน/เดือน/ปี",
        "กำไร/ขาดทุน ($)",
        "ยอดถอน ($)",
    ]  # เปลี่ยนหัวตารางให้ดูง่ายบนมือถือ
  elif len(df.columns) >= 4:
    display_df = df.iloc[:, [0, 3]].copy()
    display_df.columns = ["วัน/เดือน/ปี", "กำไร/ขาดทุน ($)"]
  else:
    display_df = df.copy()

  # ตกแต่งไฮไลต์สีเฉพาะคอลัมน์กำไร/ขาดทุนในตารางให้อ่านง่าย
  target_col = (
      "กำไร/ขาดทุน ($)" if "กำไร/ขาดทุน ($)" in display_df.columns else pnl_col
  )

  if target_col and target_col in display_df.columns:

    def highlight_pnl(val):
      try:
        num = float(
            str(val).replace("$", "").replace(",", "")
        ) if pd.notna(val) else 0
        color = "#2ea043" if num > 0 else "#f85149" if num < 0 else "#c9d1d9"
        return f"color: {color}; font-weight: bold;"
      except:
        return ""

    try:
      styled_df = display_df.style.map(highlight_pnl, subset=[target_col])
      st.dataframe(styled_df, use_container_width=True)
    except Exception:
      st.dataframe(display_df, use_container_width=True)
  else:
    st.dataframe(display_df, use_container_width=True)

  st.caption("💡 ข้อมูลซิงค์ล่าสุดจากระบบคอมพิวเตอร์ของคุณ")
else:
  st.warning("⚠️ ยังไม่พบข้อมูลในไฟล์ `trading_journal.csv`")
  st.info("💡 คำแนะนำ: อัปโหลดไฟล์ฐานข้อมูลตัวล่าสุดขึ้น GitHub เพื่อเริ่มต้นใช้งาน")