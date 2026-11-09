import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mobile Trade Reader", page_icon="📱", layout="centered"
)

st.title("📱 Mobile Trade Reader")
st.markdown("---")

FILENAME = "trading_journal.csv"

# โหลดข้อมูลจากฐานข้อมูลกลางตัวเดียวกัน
try:
  df = pd.read_csv(FILENAME)
except Exception:
  df = pd.DataFrame()

if not df.empty:
  # คำนวณข้อมูลง่ายๆ สำหรับแสดงผลบนมือถือ
  total_pnl = df["กำไร/ขาดทุน ($)"].sum() if "กำไร/ขาดทุน ($)" in df.columns else 0
  total_trades = len(df)
  wins = (
      len(df[df["กำไร/ขาดทุน ($)"] > 0])
      if "กำไร/ขาดทุน ($)" in df.columns
      else 0
  )
  win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

  # แสดงการ์ดสรุปผล
  col1, col2 = st.columns(2)
  with col1:
    st.metric("กำไร/ขาดทุนรวม", f"${total_pnl:,.2f}")
    st.metric("เทรดทั้งหมด", f"{total_trades} ออเดอร์")
  with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")

  st.markdown("### 📋 ตารางประวัติการเทรด")
  st.dataframe(df, use_container_width=True)
else:
  st.info(
      "ยังไม่มีข้อมูลการเทรด หรือกำลังรอการบันทึกข้อมูลจากหน้าจอคอมพิวเตอร์"
  )