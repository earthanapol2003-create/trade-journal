import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บให้รองรับมือถือและดูพรีเมียม
st.set_page_config(
    page_title="Systematic Trader Pro", page_icon="💎", layout="centered"
)

# ตกแต่ง CSS ธีมเข้มหรูหราสไตล์โปรแกรมเทรด
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

  # อ้างอิงตามโครงสร้างโปรแกรมคอมพิวเตอร์: คอลัมน์ที่ 4 (index 3) คือ P&L / กำไร-ขาดทุน
  # ตรวจสอบว่ามีคอลัมน์เพียงพอไหม ถ้ามี ให้เลือกคอลัมน์ที่ 4 เป็นหลัก
  pnl_col = None
  if len(df.columns) >= 4:
    pnl_col = df.columns[3]  # คอลัมน์ที่ 4 (index 3) ตรงกับ pnl
  else:
    # เผื่อกรณีฉุกเฉิน ให้หาคอลัมน์ที่มีคำว่า pnl หรือ กำไร
    for col in df.columns:
      if any(
          kw in col.lower() for kw in ["pnl", "กำไร", "profit", "loss", "net"]
      ):
        pnl_col = col
        break
    if not pnl_col and len(df.columns) > 0:
      pnl_col = df.columns[-1]  # ใช้คอลัมน์สุดท้ายสำรอง

  # แปลงข้อมูลกำไรให้เป็นตัวเลขเพื่อนำมาคำนวณสถิติ
  if pnl_col:
    df[pnl_col] = (
        df[pnl_col]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df[pnl_col] = pd.to_numeric(df[pnl_col], errors="coerce").fillna(0)

    total_trades = len(df)
    total_pnl = df[pnl_col].sum()
    wins = len(df[df[pnl_col] > 0])
    losses = len(df[df[pnl_col] < 0])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
  else:
    total_trades = len(df)
    total_pnl = 0
    wins = 0
    losses = 0
    win_rate = 0

  # แสดงการ์ดสถิติ (P&L รวม, Win Rate, จำนวนเทรด, ชนะ/แพ้)
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
  st.markdown("### 📋 ตารางบันทึกประวัติการเทรด")

  # ตกแต่งไฮไลต์สีเฉพาะคอลัมน์กำไร/ขาดทุนในตารางให้อ่านง่าย
  if pnl_col:

    def highlight_pnl(val):
      if pd.isna(val):
        return ""
      color = "#2ea043" if val > 0 else "#f85149" if val < 0 else "#c9d1d9"
      return f"color: {color}; font-weight: bold;"

    try:
      styled_df = df.style.map(highlight_pnl, subset=[pnl_col])
      st.dataframe(styled_df, use_container_width=True)
    except Exception:
      st.dataframe(df, use_container_width=True)
  else:
    st.dataframe(df, use_container_width=True)

  st.caption("💡 ข้อมูลซิงค์ล่าสุดจากระบบคอมพิวเตอร์ของคุณ")
else:
  st.warning("⚠️ ยังไม่พบข้อมูลในไฟล์ `trading_journal.csv`")
  st.info("💡 คำแนะนำ: อัปโหลดไฟล์ฐานข้อมูลตัวล่าสุดขึ้น GitHub เพื่อเริ่มต้นใช้งาน")