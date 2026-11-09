import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บให้เต็มตาและรองรับมือถือ
st.set_page_config(
    page_title="Systematic Trader Pro", page_icon="💎", layout="centered"
)

# ตกแต่ง CSS ให้ธีมเข้มหรูหราสไตล์โปรแกรมเทรดมืออาชีพ
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
  # ค้นหาชื่อคอลัมน์กำไร/ขาดทุนอัตโนมัติ
  pnl_col = None
  for col in df.columns:
    if "กำไร" in col or "P&L" in col or "Profit" in col or "Loss" in col:
      pnl_col = col
      break

  # คำนวณสถิติหลัก
  total_trades = len(df)
  total_pnl = df[pnl_col].sum() if pnl_col else 0

  wins = len(df[df[pnl_col] > 0]) if pnl_col else 0
  losses = len(df[df[pnl_col] < 0]) if pnl_col else 0
  win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

  # แสดงการ์ดสถิติแบบมืออาชีพ
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

  # ตกแต่งตารางให้ไฮไลต์สีเฉพาะคอลัมน์กำไร/ขาดทุน (ถ้ามีคอลัมน์นั้น)
  if pnl_col:

    def highlight_pnl(val):
      if pd.isna(val):
        return ""
      color = "#2ea043" if val > 0 else "#f85149" if val < 0 else "#c9d1d9"
      return f"color: {color}; font-weight: bold;"

    # ใช้ Styler เพื่อจัดสีเฉพาะคอลัมน์ P&L ให้ดูสะอาดและอ่านง่าย
    styled_df = df.style.map(highlight_pnl, subset=[pnl_col])
    st.dataframe(styled_df, use_container_width=True)
  else:
    st.dataframe(df, use_container_width=True)

  st.caption("💡 ข้อมูลซิงค์ล่าสุดจากระบบคอมพิวเตอร์ของคุณ")
else:
  st.warning("⚠️ ยังไม่พบข้อมูลในไฟล์ `trading_journal.csv`")
  st.info("💡 คำแนะนำ: อัปโหลดไฟล์ฐานข้อมูลตัวล่าสุดขึ้น GitHub เพื่อเริ่มต้นใช้งาน")