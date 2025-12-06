
# oilprice_prophet.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.diagnostics import cross_validation, performance_metrics
import snowflake.connector

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Oil Price Forecast (Prophet)", page_icon="⛽", layout="wide")
st.title("⛽ Oil Price Forecast — Prophet")
st.caption("แหล่งข้อมูล: PROJECT_5001.OIL_PRICE.OIL_TRANSACTION")

# -------------------------------------------------
# Snowflake helpers
# -------------------------------------------------
sf = st.secrets["connections"]["snowflake"]

def get_connection():
    return snowflake.connector.connect(
        account=sf["account"], user=sf["user"], password=sf["password"],
        role=sf["role"], warehouse=sf["warehouse"],
        database=sf["database"], schema=sf["schema"]
    )

@st.cache_data(ttl=1800, show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    cur.close(); conn.close()
    return df

@st.cache_data(ttl=1800, show_spinner=False)
def load_options():
    # ดึง TYPE_NAME และ TYPE_ID เรียงตาม TYPE_ID
    sql = """
    SELECT 
        OTY.TYPE_NAME
    FROM OIL_TRANSACTION OT
    JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
    GROUP BY OT.TYPE_ID, OTY.TYPE_NAME
    ORDER BY OT.TYPE_ID
    """

    types = run_query(sql)["TYPE_NAME"].tolist()

    # ดึงรายชื่อบริษัท
    # ดึงรายชื่อบริษัท
    sql_comp = """
        SELECT DISTINCT COM.COMPANY_ID, COM.COMPANY_NAME
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        ORDER BY COM.COMPANY_ID
    """
    companies = run_query(sql_comp)["COMPANY_NAME"].tolist()

    # ดึงวันที่ min-max
    dmm = run_query("SELECT MIN(DATE_TRANSACTION) AS DMIN, MAX(DATE_TRANSACTION) AS DMAX FROM OIL_TRANSACTION")
    dmin = pd.to_datetime(dmm.iloc[0]["DMIN"]).date()
    dmax = pd.to_datetime(dmm.iloc[0]["DMAX"]).date()

    return types, companies, dmin, dmax

types, companies, dmin, dmax = load_options()


# -------------------------------------------------
# Sidebar controls
# -------------------------------------------------
with st.sidebar:
    st.header("Filters")
    sel_type = st.selectbox("ชนิดน้ำมัน (TYPE_ID)", options=types)
    sel_companies = st.multiselect("บริษัท (COMPANY_ID)", options=companies, default=companies)
    date_range = st.date_input("ช่วงวันที่", value=(dmin, dmax), min_value=dmin, max_value=dmax)

    st.divider()
    st.header("Prophet settings")
    interval_width = st.slider("Uncertainty interval (เช่น 0.9 = 90%)", 0.5, 0.98, 0.9, 0.01)
    seasonality_mode = st.selectbox("Seasonality mode", ["additive", "multiplicative"], index=0)
    add_weekly = st.checkbox("ใช้ seasonality รายสัปดาห์", value=True)
    add_yearly = st.checkbox("ใช้ seasonality รายปี", value=True)
    add_daily = st.checkbox("ใช้ seasonality รายวัน", value=False)
    changepoint_prior_scale = st.number_input("ความยืดหยุ่น trend (changepoint_prior_scale)", value=0.05, min_value=0.001, step=0.01, format="%.3f")
    seasonality_prior_scale = st.number_input("seasonality_prior_scale", value=10.0, min_value=1.0, step=1.0)
    n_changepoints = st.slider("จำนวน changepoints", 5, 50, 25)

    st.divider()
    forecast_days = st.slider("พยากรณ์ล่วงหน้า (วัน)", 7, 120, 30)

    st.divider()
    do_backtest = st.checkbox("ทำ Backtest (Prophet cross_validation)", value=False)
    init_pct = st.slider("Initial train % (สำหรับ backtest)", 50, 90, 80)
    horizon_days = st.slider("Horizon สำหรับ backtest (วัน)", 7, 60, 30)
    period_days = st.slider("ระยะเลื่อนระหว่าง cutoff (วัน)", 7, 60, 15)

# -------------------------------------------------
# Load data
# -------------------------------------------------
start_date, end_date = date_range

if sel_companies:
    companies_str = ",".join(f"'{c}'" for c in sel_companies)  # ใส่ single quotes
    comp_clause = f"COM.COMPANY_NAME IN ({companies_str})"
else:
    comp_clause = "1=1"

sql = f"""
SELECT 
    OT.DATE_TRANSACTION,
    OT.TYPE_ID,
    OTY.TYPE_NAME,
    OT.COMPANY_ID,
    OT.PRICE
FROM OIL_TRANSACTION OT
JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
WHERE OTY.TYPE_NAME = '{sel_type}'
  AND {comp_clause}
  AND OT.DATE_TRANSACTION BETWEEN '{start_date}' AND '{end_date}'
ORDER BY OT.DATE_TRANSACTION ASC
"""
raw = run_query(sql)

# Clean
raw["DATE_TRANSACTION"] = pd.to_datetime(raw["DATE_TRANSACTION"], errors="coerce")
raw["PRICE"] = pd.to_numeric(raw["PRICE"], errors="coerce")
raw = raw.dropna(subset=["DATE_TRANSACTION", "PRICE"]).sort_values("DATE_TRANSACTION")

if raw.empty:
    st.error("⚠️ ไม่มีข้อมูลหลังการกรอง — ลองปรับช่วงวันที่/บริษัท")
    st.stop()

with st.expander("ตัวอย่างข้อมูล (Top 10)"):
    st.write(raw.head(10))

# -------------------------------------------------
# Aggregate (ถ้าเลือกหลายบริษัท → เฉลี่ยรายวัน)
# -------------------------------------------------
df = (
    raw.groupby("DATE_TRANSACTION", as_index=False)
       .agg(PRICE=("PRICE", "mean"))
       .rename(columns={"DATE_TRANSACTION": "ds", "PRICE": "y"})
)

# Prophet ต้องการ ds (datetime) และ y (float)
df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
df["y"]  = pd.to_numeric(df["y"], errors="coerce")
df = df.dropna(subset=["ds", "y"]).sort_values("ds")

if len(df) < 30:
    st.warning("ข้อมูลน้อยกว่า 30 จุด — Prophet อาจทำนายไม่เสถียร")
if df["y"].max() > 1e6:
    st.warning("สเกลราคาดูผิดปกติ (หลักล้าน) — ตรวจความถูกต้องของ PRICE หน่วยบาท/ลิตร")

# -------------------------------------------------
# Train Prophet
# -------------------------------------------------
m = Prophet(
    interval_width=interval_width,
    seasonality_mode=seasonality_mode,
    changepoint_prior_scale=changepoint_prior_scale,
    seasonality_prior_scale=seasonality_prior_scale,
    n_changepoints=n_changepoints
)

if add_weekly: m.add_seasonality(name="weekly", period=7, fourier_order=3)
if add_yearly: m.add_seasonality(name="yearly", period=365.25, fourier_order=10)
if add_daily:  m.add_seasonality(name="daily", period=1, fourier_order=8)

with st.spinner("กำลังเทรน Prophet..."):
    m.fit(df)

# -------------------------------------------------
# Forecast future
# -------------------------------------------------
future = m.make_future_dataframe(periods=forecast_days, freq="D", include_history=True)
forecast = m.predict(future)

# -------------------------------------------------
# Plotly: Forecast + uncertainty interval
# -------------------------------------------------
st.subheader(f"🔮 Forecast {forecast_days} วัน (รวมแถบความไม่แน่นอน)")
fig_forecast = plot_plotly(m, forecast)
fig_forecast.update_layout(height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_forecast, use_container_width=True)

st.subheader("Component plots (trend/seasonality)")
fig_comp = plot_components_plotly(m, forecast)
fig_comp.update_layout(height=600)
st.plotly_chart(fig_comp, use_container_width=True)

# ตารางผลพยากรณ์
with st.expander("ตารางผลพยากรณ์ (yhat, yhat_lower, yhat_upper)"):
    st.dataframe(
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_days),
        use_container_width=True
    )
    st.download_button(
        "⬇️ ดาวน์โหลด Forecast (CSV)",
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(index=False).encode("utf-8"),
        file_name=f"prophet_forecast_type{sel_type}.csv",
        mime="text/csv"
    )

# -------------------------------------------------
# Backtest (optional) ด้วย Prophet cross_validation
# -------------------------------------------------
if do_backtest:
    st.subheader("📏 Backtest (Prophet cross_validation)")
    # ตั้งค่า initial/period/horizon ตามสัดส่วนที่เลือก
    total_days = (df["ds"].max() - df["ds"].min()).days
    initial_days = max(int(total_days * init_pct / 100), horizon_days * 2)  # กันไม่ให้สั้นเกินไป

    try:
        with st.spinner("กำลังรัน cross_validation... (อาจใช้เวลาขึ้นกับขนาดข้อมูล)"):
            df_cv = cross_validation(
                m,
                initial=f"{initial_days} days",
                period=f"{period_days} days",
                horizon=f"{horizon_days} days",
                parallel="processes"  # เร็วขึ้นหน่อย
            )
            df_perf = performance_metrics(df_cv)
        # แสดงผล
        c1, c2, c3 = st.columns(3)
        c1.metric("RMSE", f"{df_perf['rmse'].iloc[-1]:,.3f}")
        c2.metric("MAE",  f"{df_perf['mae'].iloc[-1]:,.3f}")
        c3.metric("MAPE", f"{df_perf['mape'].iloc[-1]*100:,.2f}%")

        with st.expander("ดูตาราง performance metrics ทั้งหมด"):
            st.dataframe(df_perf, use_container_width=True)
            st.download_button(
                "⬇️ ดาวน์โหลดผล Backtest (CSV)",
                df_perf.to_csv(index=False).encode("utf-8"),
                file_name=f"prophet_backtest_type{sel_type}.csv",
                mime="text/csv"
            )

        # กราฟพยากรณ์กับจริงในแต่ละ cutoff
        st.subheader("Actual vs Predicted (ตาม cutoff ใน backtest)")
        fig_cv = go.Figure()
        fig_cv.add_trace(go.Scatter(x=df_cv['ds'], y=df_cv['y'], name='Actual', mode='lines', line=dict(color='#1f77b4')))
        fig_cv.add_trace(go.Scatter(x=df_cv['ds'], y=df_cv['yhat'], name='Predicted', mode='lines', line=dict(color='#d62728')))
        fig_cv.update_layout(height=420, xaxis_title="วันที่", yaxis_title="ราคา (บาท/ลิตร)", legend=dict(orientation="h"))
        st.plotly_chart(fig_cv, use_container_width=True)

    except Exception as e:
        st.warning(f"Backtest ล้มเหลว: {e}\nลองลด horizon หรือเพิ่ม initial ให้ยาวขึ้น แล้วรันใหม่ครับ")
