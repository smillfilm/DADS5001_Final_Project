# data_utils.py
import pandas as pd
import streamlit as st

# ---- 1. ฟังก์ชันแปลง wide -> long ----
def transform_to_long(df: pd.DataFrame) -> pd.DataFrame:
    # ปรับชื่อคอลัมน์ให้เป็นมาตรฐานเดียวกับเดิม
    rename_map = {}

    # จาก Snowflake
    if "DATE_TRANSACTION" in df.columns and "Date" not in df.columns:
        rename_map["DATE_TRANSACTION"] = "Date"
    if "TYPE_NAME" in df.columns and "FULE_TYPE" not in df.columns:
        rename_map["TYPE_NAME"] = "FULE_TYPE"

    # จาก CSV เก่า ที่ใช้ "SUSCO DEALER"
    if "SUSCO DEALER" in df.columns and "SUSCO_DEALER" not in df.columns:
        rename_map["SUSCO DEALER"] = "SUSCO_DEALER"

    if rename_map:
        df = df.rename(columns=rename_map)

    # list ยี่ห้อให้ตรงกับ column จริงใน Snowflake/CSV ใหม่
    brand_cols = [
        "PTT", "BANGCHAK", "SHELL", "ESSO", "CHEVRON",
        "IRPC", "PTG", "SUSCO", "PURE", "SUSCO_DEALER"
    ]

    # เอาเฉพาะ column ที่มีอยู่จริงใน df (กัน KeyError)
    value_vars = [c for c in brand_cols if c in df.columns]
    if not value_vars:
        raise KeyError(f"No brand columns found in DataFrame. Expected one of: {brand_cols}")

    # melt จาก wide -> long
    df_long = df.melt(
        id_vars=["Date", "FULE_TYPE"],      # ตอนนี้มั่นใจว่ามีแล้ว
        value_vars=value_vars,
        var_name="Brand",
        value_name="Price",
    )

    # ให้ Price เป็นตัวเลขเสมอ
    df_long["Price"] = pd.to_numeric(df_long["Price"], errors="coerce")

    # ตัด NA และค่าที่เป็น 0 หรือติดลบออก
    df_long = df_long.dropna(subset=["Price"])
    df_long = df_long[df_long["Price"] > 0]

    # แก้ชื่อ Brand ให้ไม่มีช่องว่าง (กัน error เวลา filter / groupby)
    df_long["Brand"] = df_long["Brand"].str.replace(" ", "_")

    # แปลง Date เป็น datetime ถ้าเป็น string
    if df_long["Date"].dtype == "object":
        df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce")

    # ตัดแถวที่ Date แปลงไม่ได้ทิ้ง
    df_long = df_long.dropna(subset=["Date"])

    return df_long


# ---- 2. ฟังก์ชันหลัก: อ่านจาก Snowflake + Transform + cache ----
@st.cache_data
def get_oilprice_long() -> pd.DataFrame:
    from snowflake.connector import connect

    sf = st.secrets["connections"]["snowflake"]
    conn = connect(
        account=sf["account"],
        user=sf["user"],
        password=sf["password"],
        role=sf["role"],
        warehouse=sf["warehouse"],
        database=sf["database"],
        schema=sf["schema"],
    )

    sql = """
    SELECT
        t.DATE_TRANSACTION,
        ty.TYPE_NAME,
        MAX(CASE WHEN com.COMPANY_ID = 1  THEN t.PRICE END) AS PTT,
        MAX(CASE WHEN com.COMPANY_ID = 2  THEN t.PRICE END) AS BANGCHAK,
        MAX(CASE WHEN com.COMPANY_ID = 3  THEN t.PRICE END) AS SHELL,
        MAX(CASE WHEN com.COMPANY_ID = 4  THEN t.PRICE END) AS ESSO,
        MAX(CASE WHEN com.COMPANY_ID = 5  THEN t.PRICE END) AS CHEVRON,
        MAX(CASE WHEN com.COMPANY_ID = 6  THEN t.PRICE END) AS IRPC,
        MAX(CASE WHEN com.COMPANY_ID = 7  THEN t.PRICE END) AS PTG,
        MAX(CASE WHEN com.COMPANY_ID = 8  THEN t.PRICE END) AS SUSCO,
        MAX(CASE WHEN com.COMPANY_ID = 9  THEN t.PRICE END) AS PURE,
        MAX(CASE WHEN com.COMPANY_ID = 10 THEN t.PRICE END) AS SUSCO_DEALER
    FROM OIL_TRANSACTION t
    JOIN OIL_TYPE ty   ON ty.TYPE_NO    = t.TYPE_ID
    JOIN COMPANY com   ON com.COMPANY_ID = t.COMPANY_ID
    WHERE t.PRICE IS NOT NULL
    GROUP BY t.DATE_TRANSACTION, ty.TYPE_NAME
    ORDER BY t.DATE_TRANSACTION, ty.TYPE_NAME
    """
    cur = conn.cursor()
    cur.execute(sql)
    df_wide = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
    cur.close()
    conn.close()

    df_long = transform_to_long(df_wide)
    return df_long
