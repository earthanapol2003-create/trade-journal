import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บให้รองรับมือถือและดูพรีเมียม
st.set_page_config(
    page_title="Systematic Trader Pro", page_icon="💎", layout="centered"
)

# ตกแต่ง CSS เพิ่มลูกเล่นความพรีเมียมและเอฟเฟกต์เรืองแสง
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 16px;
        border-radius: 14px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stMetric:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px;
        color: #c9d1d9;
        padding: 8px 16px;
        border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: white !important;
        font-weight: bold;
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

  # ดึงข้อมูลจากคอลัมน์ P&L (Index 3)
  pnl_col = df.columns[3] if len(df.columns) > 3 else None

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

  # สร้างลูกเล่น Tabs แบ่งหน้าจอให้ใช้งานง่ายบนมือถือ
  tab1, tab2 = st.tabs(["📊 แดชบอร์ดสรุปผล", "📂 ข้อมูลดิบทั้งหมด"])

  with tab1:
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

    # ลูกเล่น: แถบ Progress Bar แสดงสัดส่วน Win Rate
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("🎯 **สัดส่วนความแม่นยำพอร์ต (Win Rate Progress)**")
    st.progress(
        min(max(win_rate / 100.0, 0.0), 1.0),
        text=f"อัตราการชนะรวม: {win_rate:.1f}% ({wins} Win / {losses} Loss)",
    )

    st.markdown("---")
    st.markdown("### 📋 ตารางประวัติ (วันที่ • กำไร/ขาดทุน • ยอดถอน)")

    # เลือกแสดงผลเฉพาะคอลัมน์ที่ต้องการ: วัน/เดือน/ปี, กำไร/ขาดทุน, ยอดถอน
    if len(df.columns) >= 5:
      display_df = df.iloc[:, [0, 3, 4]].copy()
      display_df.columns = ["วัน/เดือน/ปี", "กำไร/ขาดทุน ($)", "ยอดถอน ($)"]
    elif len(df.columns) >= 4:
      display_df = df.iloc[:, [0, 3]].copy()
      display_df.columns = ["วัน/เดือน/ปี", "กำไร/ขาดทุน ($)"]
    else:
      display_df = df.copy()

    # ฟังก์ชันแต่งสีและพื้นหลังเซลล์ในตาราง
    def style_table_cells(val, col_name):
      try:
        num = (
            float(str(val).replace("$", "").replace(",", ""))
            if pd.notna(val)
            else 0
        )
        if col_name == "กำไร/ขาดทุน ($)":
          if num > 0:
            return "color: #2ea043; font-weight: bold; background-color: rgba(46, 160, 67, 0.1);"
          elif num < 0:
            return "color: #f85149; font-weight: bold; background-color: rgba(248, 81, 73, 0.1);"
        elif col_name == "ยอดถอน ($)":
          if num > 0:
            return "color: #ffa500; font-weight: bold; background-color: rgba(255, 165, 0, 0.1);"
      except:
        pass
      return ""

    try:
      styled_df = display_df.style
      for col in ["กำไร/ขาดทุน ($)", "ยอดถอน ($)"]:
        if col in display_df.columns:
          styled_df = styled_df.map(lambda v, c=col: style_table_cells(v, c), subset=[col])
      st.dataframe(styled_df, use_container_width=True)
    except Exception:
      st.dataframe(display_df, use_container_width=True)

  with tab2:
    st.markdown("### 📂 ตารางข้อมูลดิบแบบเต็ม (ทุกคอลัมน์)")
    st.dataframe(df, use_container_width=True)

  st.caption(
      "💡 ข้อมูลซิงค์ล่าสุดจากระบบคอมพิวเตอร์ของคุณ • Systematic Trader Pro"
  )
else:
  st.warning("⚠️ ยังไม่พบข้อมูลในไฟล์ `trading_journal.csv`")
  st.info("💡 คำแนะนำ: อัปโหลดไฟล์ฐานข้อมูลตัวล่าสุดขึ้น GitHub เพื่อเริ่มต้นใช้งาน")