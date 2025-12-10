
# oilprice_change_board.py
import streamlit as st
import pandas as pd
import snowflake.connector
import altair as alt

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="ราคาน้ำมันล่าสุด", page_icon="⛽", layout="wide")
st.title("⛽ ราคาน้ำมันล่าสุดรายบริษัท")
st.caption("ที่มา: PROJECT_5001.OIL_PRICE.OIL_TRANSACTION, OIL_TYPE, COMPANY")

# ---------------------------
# Snowflake connection helpers
# ---------------------------
sf = st.secrets["connections"]["snowflake"]

def get_connection():
    """Get Snowflake connection from secrets"""
    sf = st.secrets["connections"]["snowflake"]
    try:
        conn = snowflake.connector.connect(
            account=sf["account"],
            user=sf["user"],
            password=sf["password"],
            role=sf.get("role", None),  # Optional
            warehouse=sf.get("warehouse", "COMPUTE_WH"),
            database=sf.get("database", "PR_NEWS_CENTER"),
            schema=sf.get("schema", "PUBLIC")
        )
        return conn
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
        return 
@st.cache_data(ttl=900)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    cur.close(); conn.close()
    return df

# ---------------------------
# SQL: ดึง "สองเหตุการณ์เปลี่ยนราคา" ล่าสุด ต่อ TYPE_ID + COMPANY_ID
# ---------------------------
SQL_LAST_TWO_CHANGES = """
WITH base AS (
  SELECT
    t.DATE_TRANSACTION,
    t.TYPE_ID,
    ty.TYPE_NAME,
    t.COMPANY_ID,
    com.COMPANY_NAME,
    t.PRICE,
    LAG(t.PRICE) OVER (
      PARTITION BY t.TYPE_ID, t.COMPANY_ID
      ORDER BY t.DATE_TRANSACTION
    ) AS prev_price
  FROM OIL_TRANSACTION t
  JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
  JOIN COMPANY com ON com.COMPANY_ID = t.COMPANY_ID
  WHERE t.PRICE IS NOT NULL
),
changes AS (
  -- เหตุการณ์ "เปลี่ยนราคา" = แถวแรก หรือ PRICE เปลี่ยนจาก prev_price
  SELECT
    DATE_TRANSACTION,
    TYPE_ID,
    TYPE_NAME,
    COMPANY_ID,
    COMPANY_NAME,
    PRICE,
    CASE WHEN prev_price IS NULL OR PRICE <> prev_price THEN 1 ELSE 0 END AS is_change
  FROM base
),
last2 AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY TYPE_ID, COMPANY_ID
      ORDER BY DATE_TRANSACTION DESC
    ) AS rn
  FROM changes
  WHERE is_change = 1
),
last_change AS (
  SELECT
    TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
    DATE_TRANSACTION AS DATE_LAST_CHANGE,
    PRICE AS PRICE_LAST
  FROM last2 WHERE rn = 1
),
prev_change AS (
  SELECT
    TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
    DATE_TRANSACTION AS DATE_PREV_CHANGE,
    PRICE AS PRICE_PREV
  FROM last2 WHERE rn = 2
),
final AS (
  SELECT
    lc.TYPE_ID, lc.TYPE_NAME, lc.COMPANY_ID, lc.COMPANY_NAME,
    lc.DATE_LAST_CHANGE, lc.PRICE_LAST,
    pc.DATE_PREV_CHANGE, pc.PRICE_PREV
  FROM last_change lc
  LEFT JOIN prev_change pc
    ON pc.TYPE_ID = lc.TYPE_ID
   AND pc.COMPANY_ID = lc.COMPANY_ID
)
SELECT
  TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
  DATE_LAST_CHANGE, PRICE_LAST,
  DATE_PREV_CHANGE, PRICE_PREV
FROM final
ORDER BY COMPANY_NAME, TYPE_NAME;
"""

df = run_query(SQL_LAST_TWO_CHANGES)

# Cast types & diff
df["DATE_LAST_CHANGE"] = pd.to_datetime(df["DATE_LAST_CHANGE"], errors="coerce")
df["DATE_PREV_CHANGE"] = pd.to_datetime(df["DATE_PREV_CHANGE"], errors="coerce")
df["PRICE_LAST"] = pd.to_numeric(df["PRICE_LAST"], errors="coerce")
df["PRICE_PREV"] = pd.to_numeric(df["PRICE_PREV"], errors="coerce")
df["DIFF_FROM_PREV_CHANGE"] = df["PRICE_LAST"] - df["PRICE_PREV"]

# วันที่ล่าสุดในระบบ (แสดงประกอบ)
max_date_sql = "SELECT MAX(DATE_TRANSACTION) AS MAX_DATE FROM OIL_TRANSACTION"
max_date_df = run_query(max_date_sql)
max_date = pd.to_datetime(max_date_df.iloc[0]["MAX_DATE"]) if not max_date_df.empty else None

st.write(
    f"📅 **วันที่ล่าสุดในระบบ:** {max_date.date() if pd.notna(max_date) else '-'} — "
    "ส่วนต่างที่โชว์คำนวณจาก **วันที่ล่าสุดที่มีการเปลี่ยนราคา** เทียบกับ **วันก่อนหน้าที่มีการเปลี่ยนราคา**"
)

# ---------------------------
# GREEN THEME (CSS + palette)
# ---------------------------
GREEN_PALETTE = {
    "bg": "#E8F5E9", "border": "#A5D6A7", "accent": "#2E7D32",
    "accent2": "#1B5E20", "text": "#0B3D0B", "up": "#2E7D32",     # ▼ ลดราคา
    "down": "#D32F2F", "neutral": "#666666",                      # ▲ ขึ้นราคา
    "bg_up": "#E8F5E9", "bg_down": "#FFEBEE", "bg_neutral": "#FFFFFF",
    "border_up": "#66BB6A", "border_down": "#EF5350", "border_neutral": "#E0E0E0"
}
st.markdown(f"""
<style>
.card-green {{
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.card-title {{ font-weight: 700; color: {GREEN_PALETTE['accent']}; margin-bottom: 6px; }}
.card-price {{ font-size: 22px; font-weight: 700; color: {GREEN_PALETTE['text']}; }}
.card-diff {{ font-size: 14px; font-weight: 600; }}
.card-meta {{ font-size: 12px; color: #7A7A7A; margin-top: 6px; }}
.badge {{ display: inline-block; background: {GREEN_PALETTE['accent']}; color: white; font-size: 12px; padding: 2px 8px; border-radius: 999px; margin-left: 6px; }}

/* สถานะพื้นหลัง/ขอบสำหรับขึ้น-ลง-คงที่ */
.card-up {{
  background: {GREEN_PALETTE['bg_down']};
  border: 1px solid {GREEN_PALETTE['border_down']};
}}
.card-down {{
  background: {GREEN_PALETTE['bg_up']};
  border: 1px solid {GREEN_PALETTE['border_up']};
}}
.card-neutral {{
  background: {GREEN_PALETTE['bg_neutral']};
  border: 1px solid {GREEN_PALETTE['border_neutral']};
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar: บริษัท + ชนิดน้ำมัน + การจัดเรียง
# ---------------------------
companies_avail = sorted(df["COMPANY_NAME"].dropna().unique().tolist())
types_avail     = sorted(df["TYPE_NAME"].dropna().unique().tolist())

with st.sidebar:
    st.header("ตั้งค่าการแสดงผล")
    selected_companies = st.multiselect(
        "เลือกบริษัทที่จะโชว์", options=companies_avail,
        default=(companies_avail[:3] if companies_avail else [])
    )
    selected_types = st.multiselect(
        "เลือกชนิดน้ำมัน (TYPE_NAME)", options=types_avail,
        default=(types_avail[:6] if types_avail else [])
    )
    sort_by = st.selectbox("จัดเรียงชนิดน้ำมันตาม", ["ชื่อ (TYPE_NAME)", "ราคา (PRICE_LAST)"], index=0)

# กรองตามตัวเลือก
df_filtered = df.copy()
if selected_companies:
    df_filtered = df_filtered[df_filtered["COMPANY_NAME"].isin(selected_companies)]
if selected_types:
    df_filtered = df_filtered[df_filtered["TYPE_NAME"].isin(selected_types)]

if df_filtered.empty:
    st.warning("ไม่มีข้อมูลสำหรับตัวเลือกที่กำหนด ลองปรับบริษัท/ชนิดน้ำมันใหม่ครับ")
    st.stop()

# ---------------------------
# ฟังก์ชันวาดบอร์ดสีเขียว (พื้นหลังเปลี่ยนตาม diff) - แก้ไข
# ---------------------------
def render_company_board_green(company_name: str, sub_df: pd.DataFrame):
    """
    sub_df ต้องมีคอลัมน์:
    TYPE_NAME, PRICE_LAST, DATE_LAST_CHANGE, DATE_PREV_CHANGE, DIFF_FROM_PREV_CHANGE
    **แก้ไข:** จะแสดงเฉพาะชนิดน้ำมันที่มีข้อมูลการเปลี่ยนแปลงราคา (มี DATE_PREV_CHANGE)
    """
    # กรองเฉพาะชนิดน้ำมันที่มีข้อมูลการเปลี่ยนแปลงราคา (มี DATE_PREV_CHANGE)
    sub_df_filtered = sub_df[sub_df["DATE_PREV_CHANGE"].notna()].copy()
    if sub_df_filtered.empty:
        # ไม่ต้องแสดงอะไรเลยถ้าไม่มีข้อมูลการเปลี่ยนแปลง
        return
    st.markdown(f"### 🏷️ {company_name}", unsafe_allow_html=True)
    # เรียงตามตั้งค่า
    if sort_by == "ราคา (PRICE_LAST)":
        sub_df_filtered = sub_df_filtered.sort_values(["PRICE_LAST", "TYPE_NAME"])
    else:
        sub_df_filtered = sub_df_filtered.sort_values("TYPE_NAME")
    cols = st.columns(3)
    for i, row in sub_df_filtered.iterrows():
        col    = cols[i % 3]
        typ    = row["TYPE_NAME"]
        price  = row["PRICE_LAST"]
        d_last = row["DATE_LAST_CHANGE"]
        d_prev = row["DATE_PREV_CHANGE"]
        diff   = row["DIFF_FROM_PREV_CHANGE"]
        # สถานะ: up (▲) / down (▼) / neutral (—)
        if pd.notna(diff):
            if diff > 0:
                card_class = "card-up"
                diff_color = GREEN_PALETTE["down"]   # สีแดง
                diff_text  = f"▲ +{diff:.2f}"
            elif diff < 0:
                card_class = "card-down"
                diff_color = GREEN_PALETTE["up"]     # สีเขียว
                diff_text  = f"▼ {diff:.2f}"
            else:
                card_class = "card-neutral"
                diff_color = GREEN_PALETTE["neutral"]
                diff_text  = "— 0.00"
        else:
            card_class = "card-neutral"
            diff_color = GREEN_PALETTE["neutral"]
            diff_text  = "—"
        with col.container():
            st.markdown(
                f"""
<div class="card-green {card_class}">
<div class="card-title">{typ}</div>
<div class="card-price">{price:,.2f} บาท/ลิตร</div>
<div class="card-diff" style="color:{diff_color};">{diff_text}</div>
<div class="card-meta">
    เปลี่ยนล่าสุด: {d_last.date() if pd.notna(d_last) else '-'}
    {" | รอบก่อน: " + d_prev.date().isoformat() if pd.notna(d_prev) else ""}
</div>
</div>
""",
                unsafe_allow_html=True
            )
# ---------------------------
# วาดบอร์ดตามบริษัทที่เลือก
# ---------------------------
for comp in (selected_companies if selected_companies else companies_avail):
    sub = df_filtered[df_filtered["COMPANY_NAME"] == comp]
    if sub.empty:
        st.info(f"ไม่มีข้อมูลสำหรับ {comp}")
    else:
        render_company_board_green(comp, sub)

# ---------------------------
# ตารางสรุป (หลังกรอง)
# ---------------------------
st.divider()
st.subheader("ตารางเหตุการณ์เปลี่ยนราคาล่าสุดต่อชนิด/บริษัท (หลังกรอง)")


# เปลี่ยนชื่อคอลัมน์ใน df_filtered
df_filtered = df_filtered.rename(columns={
    "TYPE_NAME": "ชนิดน้ำมัน",
    "COMPANY_NAME": "แบรนด์",
    "DIFF_FROM_PREV_CHANGE": "ส่วนต่างราคา",
    "DATE_LAST_CHANGE" : "วันที่ปรับราคาล่าสุด", 
    "PRICE_LAST":"ราคาล่าสุด",
    "DATE_PREV_CHANGE":"วันที่ปรับราคาก่อนหน้า", 
    "PRICE_PREV":"ราคาก่อนหน้า"


})

# ปรับคอลัมน์ที่จะแสดง
show_cols = [
    "ชนิดน้ำมัน", "แบรนด์", "วันที่ปรับราคาล่าสุด", "ราคาล่าสุด",
    "วันที่ปรับราคาก่อนหน้า", "ราคาก่อนหน้า", "ส่วนต่างราคา"
]

# แสดงตาราง
st.dataframe(
    df_filtered[show_cols].sort_values(["แบรนด์", "ชนิดน้ำมัน"]),
    use_container_width=True
)



# ---------------------------
# มินิกราฟย้อนหลัง 30 วัน (ไม่ใช่ 60 วัน)
# ---------------------------
st.divider()
st.subheader("ราคาน้ำมันย้อนหลัง 30 วัน (เลือกชนิด/บริษัท)")
type_sel = st.selectbox("ชนิดน้ำมัน", options=sorted(df_filtered["ชนิดน้ำมัน"].unique().tolist()))
comp_sel = st.selectbox("บริษัท", options=sorted(df_filtered["แบรนด์"].unique().tolist()))

HIST_SQL = f"""
SELECT t.DATE_TRANSACTION, ty.TYPE_NAME, com.COMPANY_NAME, t.PRICE
FROM OIL_TRANSACTION t
JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
JOIN COMPANY com ON com.COMPANY_ID = t.COMPANY_ID
WHERE ty.TYPE_NAME = '{type_sel}'
  AND com.COMPANY_NAME = '{comp_sel}'
  AND t.DATE_TRANSACTION >= DATEADD('day', -30, (SELECT MAX(DATE_TRANSACTION) FROM OIL_TRANSACTION))
ORDER BY t.DATE_TRANSACTION
"""
hist = run_query(HIST_SQL)

if not hist.empty:
    hist["DATE_TRANSACTION"] = pd.to_datetime(hist["DATE_TRANSACTION"], errors="coerce")
    hist["PRICE"] = pd.to_numeric(hist["PRICE"], errors="coerce")
    chart = alt.Chart(hist).mark_line(point=True).encode(
        x=alt.X("DATE_TRANSACTION:T", title="วันที่"),
        y=alt.Y("PRICE:Q", title="ราคา (บาท/ลิตร)"),
        tooltip=[
            alt.Tooltip("DATE_TRANSACTION:T", title="วันที่"),
            alt.Tooltip("PRICE:Q", title="ราคา", format=".2f"),
            alt.Tooltip("TYPE_NAME:N", title="ชนิด"),
            alt.Tooltip("COMPANY_NAME:N", title="บริษัท"),
        ],
    ).properties(height=300).interactive()
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("ไม่มีข้อมูลย้อนหลังสำหรับตัวเลือกนี้ในช่วง 30 วัน")
