import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
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

  # ให้ผู้ใช้เลือกคอลัมน์กำไร/ขาดทุนด้วยตัวเองจาก Sidebar หรือหน้าจอ เพื่อความแม่นยำสูงสุด
  st.sidebar.markdown("### ⚙️ ตั้งค่าการแสดงผล")
  column_list = list(df.columns)

  # พยายามหาคอลัมน์ที่น่าจะเป็นกำไรมาตั้งเป็นค่าเริ่มต้น
  default_idx = 0
  for i, col in enumerate(column_list):
    col_lower = col.lower()
    if any(kw in col_lower for kw in ["กำไร", "p&l", "profit", "loss", "net"]):
      default_idx = i
      break

  selected_pnl_col = st.sidebar.selectbox(
      "เลือกคอลัมน์สำหรับคำนวณกำไร/ขาดทุน:", column_list, index=default_idx
  )

  # แปลงข้อมูลในคอลัมน์ที่เลือกให้เป็นตัวเลข
  pnl_col = selected_pnl_col
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

  # แสดงการ์ดสถิติ
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

  # แสดงตารางข้อมูล
  st.dataframe(df, use_container_width=True)

  st.caption("💡 ข้อมูลซิงค์ล่าสุดจากระบบคอมพิวเตอร์ของคุณ")
else:
  st.warning("⚠️ ยังไม่พบข้อมูลในไฟล์ `trading_journal.csv`")
  st.info("💡 คำแนะนำ: อัปโหลดไฟล์ฐานข้อมูลตัวล่าสุดขึ้น GitHub เพื่อเริ่มต้นใช้งาน")