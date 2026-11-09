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
  # ถ้าไฟล์มีคอลัมน์น้อยกว่า 4 ให้ลองอ่านแบบไม่มี Header เผื่อโครงสร้างไฟล์ในคอมพิวเตอร์เก็บข้อมูลดิบ
  if df.shape[1] < 4:
    try:
      df = pd.read_csv(FILENAME, header=None)
    except Exception:
      pass

  # ดึงข้อมูลจากคอลัมน์ที่ 4 (index 3) โดยตรงตามระบบคอมพิวเตอร์ของคุณ
  if df.shape[1] >= 4:
    raw_pnl = df.iloc[:, 3]  # เลือกคอลัมน์ที่ 4 แน่นอน

    # แปลงข้อมูลเป็นตัวเลข (ล้างอักษรพิเศษหรือช่องว่าง)
    cleaned_pnl = (
        raw_pnl.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    pnl_series = pd.to_numeric(cleaned_pnl, errors="coerce").fillna(0)
  else:
    pnl_series = pd.Series([0] * len(df))

  # คำนวณสถิติ
  total_trades = len(df)
  total_pnl = pnl_series.sum()
  wins = len(pnl_series[pnl_series > 0])
  losses = len(pnl_series[pnl_series < 0])
  win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

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