import streamlit as st
import pandas as pd
from data_utils import get_oilprice_long
import plotly.graph_objects as go

st.title("⛽ Oil Cost Simulation")

# --- Load latest price from database ---
# คาดว่าได้คอลัมน์: Date, FULE_TYPE, Brand, Price
df = get_oilprice_long()

# หาวันล่าสุด
latest_date = df["Date"].max()
latest_df = df[df["Date"] == latest_date]

# =========================
# 1) เตรียม default ต่าง ๆ
# =========================

# รายชื่อ Brand
brand_list = sorted(latest_df["Brand"].unique())

# default brand
default_brand = "PTT"
if default_brand not in brand_list:
    default_brand = brand_list[0]

# รายชื่อชนิดน้ำมันทั้งหมด (จากวันล่าสุด)
fuel_type_list = sorted(latest_df["FULE_TYPE"].unique())

# default fuel type
default_fuel_type = "แก๊สโซฮอล ออกเทน 91 (Gasohol 91-E10)"
if default_fuel_type not in fuel_type_list:
    default_fuel_type = fuel_type_list[0]

# หา base price จาก brand + fuel type ที่ตั้งค่า default
mask_default = (
    (latest_df["Brand"] == default_brand)
    & (latest_df["FULE_TYPE"] == default_fuel_type)
)

if mask_default.any():
    base_price = float(latest_df.loc[mask_default, "Price"].iloc[0])
else:
    # fallback เผื่อ combination นี้ไม่มีจริง
    base_price = float(latest_df["Price"].iloc[0])

st.subheader("กรอกข้อมูลเพื่อคำนวณ")

# =========================
# แถวที่ 1 : ราคาตั้งต้น + ราคาที่คาดหวัง
# =========================
col1, col2 = st.columns(2)

with col1:
    current_price = st.number_input(
        "ราคาเชื้อเพลิงตั้งต้น (บาท/ลิตร)",
        value=float(base_price),
        min_value=0.0,
        step=0.05,
    )

with col2:
    future_price = st.number_input(
        "ราคาเชื้อเพลิงที่คาดหวัง (บาท/ลิตร)",
        value=float(base_price - 0.5),
        min_value=0.0,
        step=0.05,
        help="ถ้าไม่ต้องการเปรียบเทียบ ให้ใส่ 0 ไว้ได้",
    )

# =========================
# แถวที่ 2 : Brand + Fuel Type
# =========================
col3, col4 = st.columns(2)

with col3:
    # เลือก Brand ก่อน เพื่อเอาไปใช้ filter fuel type
    brand_selected = st.selectbox(
        "เลือกแบรนด์น้ำมัน",
        brand_list,
        index=brand_list.index(default_brand),
    )

# ตอนนี้ brand_selected มีค่าแล้ว ค่อย filter fuel type ตาม brand นี้
brand_df = df[df["Brand"] == brand_selected]
fuel_types_for_brand = sorted(brand_df["FULE_TYPE"].unique())

with col4:
    fuel_selected = st.selectbox(
        "เลือกชนิดเชื้อเพลิง",
        fuel_types_for_brand,
        index=fuel_types_for_brand.index(default_fuel_type)
        if default_fuel_type in fuel_types_for_brand
        else 0,
    )

# =========================
# แถวที่ 3 : ปริมาณน้ำมัน
# =========================
col5, _ = st.columns(2)

with col5:
    amount_liter = st.number_input(
        "กรอกปริมาณน้ำมัน (ลิตร)",
        min_value=0.1,
        value=50000.0,
        step=10.0,  # float
    )

# ======================================================
# 📈 กราฟเปรียบเทียบราคาน้ำมัน
# ======================================================
st.subheader("📈 กราฟเปรียบเทียบราคาน้ำมัน")

# เตรียมข้อมูลสำหรับกราฟ: เลือกเฉพาะ brand + fuel_type ที่สนใจ
df_plot = (
    df[(df["Brand"] == brand_selected) & (df["FULE_TYPE"] == fuel_selected)]
    .sort_values("Date")
    .copy()
)

# สร้างคอลัมน์ราคาคงที่ตาม current / future (ใช้วาดเส้นแนวนอน)
df_plot["current_price"] = float(current_price)
df_plot["future_price"] = float(future_price)

# ----------------- เริ่มสร้างกราฟ -----------------
fig = go.Figure()

# 1) เส้นราคาจริง (สีเขียว)
fig.add_trace(
    go.Scatter(
        x=df_plot["Date"],
        y=df_plot["Price"],
        mode="lines",
        name="ราคาจริง",
        line=dict(color="green", width=2),
    )
)

# 2) เส้นราคาเชื้อเพลิงตั้งต้น (ส้ม เส้นประ)
fig.add_trace(
    go.Scatter(
        x=df_plot["Date"],
        y=df_plot["current_price"],
        mode="lines",
        name="ราคาเชื้อเพลิงตั้งต้น",
        line=dict(color="orangered", width=3, dash="solid"),
    )
)

# 3) เส้นราคาเชื้อเพลิงที่คาดหวัง (น้ำเงิน เส้นประ + fill)
fig.add_trace(
    go.Scatter(
        x=df_plot["Date"],
        y=df_plot["future_price"],
        mode="lines",
        name="ราคาเชื้อเพลิงที่คาดหวัง",
        line=dict(color="blue", width=3, dash="solid"),
        fill="tonexty",
        fillcolor="rgba(0,0,0,0.15)",  # โซนระหว่างเส้น current กับ future
    )
)

fig.update_layout(
    title=f"ราคาน้ำมันของ {brand_selected} – {fuel_selected}",
    xaxis_title="วันที่",
    yaxis_title="ราคาน้ำมัน (บาทต่อลิตร)",
    template="plotly_white",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

# ======================================================
# 📊 ผลลัพธ์การคำนวณ (Realtime, อยู่ใต้กราฟ)
# ======================================================
st.subheader("📊 ผลลัพธ์การคำนวณ")

if future_price == 0.0:
    st.info("กรุณากรอกราคาเชื้อเพลิงที่คาดหวัง (> 0) เพื่อเปรียบเทียบค่าใช้จ่าย")
else:
    current_cost = float(current_price) * float(amount_liter)
    future_cost = float(future_price) * float(amount_liter)
    diff = future_cost - current_cost

    st.write(f"**ค่าใช้จ่ายจากราคาเชื้อเพลิงตั้งต้น:** {current_cost:,.2f} บาท")
    st.write(f"**ค่าใช้จ่ายจากราคาที่คาดหวัง:** {future_cost:,.2f} บาท")

    if diff > 0:
        st.error(f"💸 ค่าใช้จ่ายจะเพิ่มขึ้น **{diff:,.2f} บาท**")
    elif diff < 0:
        st.success(f"💚 ค่าใช้จ่ายจะลดลง **{-diff:,.2f} บาท**")
    else:
        st.info("ราคาคงเดิม ไม่เพิ่มไม่ลด")

# เว้นระยะให้รู้สึกเป็นอีกส่วนหนึ่ง
st.markdown("## ")

# ======================================================
# 🚗 ส่วนเสริม: คำนวณระยะทางจากน้ำมัน
# ======================================================
st.markdown("----")
st.subheader("🚗 ส่วนเสริม: คำนวณระยะทางจากน้ำมัน")

# ---------- แถวที่ 1 : Input เป็น Grid ----------
r1c1, r1c2 = st.columns(2)

with r1c1:
    fuel_eff_extra = st.number_input(
        "อัตราการสิ้นเปลืองเชื้อเพลิง (กิโลเมตรต่อลิตร)",
        min_value=0.1,
        value=6.0,
        step=0.1,
        key="fuel_eff_extra",
    )

with r1c2:
    trip_distance = st.number_input(
        "ระยะทางต่อเที่ยว (กิโลเมตร)",
        min_value=1.0,
        value=250.0,
        step=10.0,
        key="trip_distance",
    )

show_future = future_price > 0.0

# ---------- คำนวณตัวเลขพื้นฐาน ----------
if fuel_eff_extra > 0:
    # ปริมาณน้ำมันต่อเที่ยว (ลิตร)
    liters_per_trip = trip_distance / fuel_eff_extra

    # ค่าใช้จ่ายต่อกม.
    cost_per_km_current = current_price / fuel_eff_extra
    cost_per_km_future = future_price / fuel_eff_extra if show_future else None

    # ค่าใช้จ่ายต่อเที่ยว
    trip_cost_current = liters_per_trip * current_price
    trip_cost_future = liters_per_trip * future_price if show_future else None

    # ผลกระทบถ้าราคาน้ำมันเปลี่ยนไป 1 บาท/ลิตร
    delta_cost_per_km = 1.0 / fuel_eff_extra          # บาท/กม.
    delta_cost_per_trip = delta_cost_per_km * trip_distance  # บาท/เที่ยว

    # วิ่ง 100 กม.
    dist_100 = 100.0
    liters_for_100 = dist_100 / fuel_eff_extra
    cost_100_current = liters_for_100 * current_price
    cost_100_future = liters_for_100 * future_price if show_future else None
else:
    liters_per_trip = 0.0
    cost_per_km_current = None
    cost_per_km_future = None
    trip_cost_current = None
    trip_cost_future = None
    delta_cost_per_km = None
    delta_cost_per_trip = None
    dist_100 = 100.0
    cost_100_current = None
    cost_100_future = None

# ---------- แถวที่ 2 : สรุปแบบ Metric ----------
st.markdown("### 📌 สรุปต้นทุนแบบย่อ")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "ค่าใช้จ่ายต่อกม. (ตั้งต้น)",
        f"{(cost_per_km_current or 0):,.2f} บาท/กม.",
    )

with m2:
    if show_future and cost_per_km_future is not None:
        st.metric(
            "ค่าใช้จ่ายต่อกม. (ที่คาดหวัง)",
            f"{cost_per_km_future:,.2f} บาท/กม.",
        )
    else:
        st.metric("ค่าใช้จ่ายต่อกม. (ที่คาดหวัง)", "ยังไม่ได้กรอก")

with m3:
    if delta_cost_per_km is not None:
        st.metric(
            "เมื่อราคาน้ำมันเปลี่ยนแปลงทุกๆ 1 บาท",
            f"{delta_cost_per_km:,.2f} บาท/กม.",
        )
    else:
        st.metric("ผลกระทบเมื่อราคาน้ำมัน +1 บาท", "—")

# ---------- แถวที่ 4 : ค่าใช้จ่ายต่อเที่ยว ----------
st.markdown("### 🚛 ค่าใช้จ่ายต่อหนึ่งเที่ยวส่งของ")

r4c1, r4c2 = st.columns(2)

with r4c1:
    st.markdown("**เที่ยวละ (ราคาเชื้อเพลิงตั้งต้น)**")
    if trip_cost_current is not None and fuel_eff_extra > 0:
        st.write(
            f"- ระยะ {trip_distance:,.0f} กม.\n"
            f"- ใช้น้ำมัน ~ {liters_per_trip:,.2f} ลิตร\n"
            f"- ค่าใช้จ่ายต่อเที่ยว ≈ **{trip_cost_current:,.2f} บาท**"
        )
    else:
        st.write("⚠️ กรอกอัตราการสิ้นเปลืองและระยะทางต่อเที่ยวให้ครบ")

with r4c2:
    st.markdown("**เที่ยวละ (ราคาที่คาดหวัง)**")
    if show_future and trip_cost_future is not None and fuel_eff_extra > 0:
        st.write(
            f"- ระยะ {trip_distance:,.0f} กม.\n"
            f"- ใช้น้ำมัน ~ {liters_per_trip:,.2f} ลิตร\n"
            f"- ค่าใช้จ่ายต่อเที่ยว ≈ **{trip_cost_future:,.2f} บาท**"
        )
    else:
        st.write("⚠️ ยังไม่ได้กรอกราคาที่คาดหวัง (> 0)")

# ---------- แถวที่ 3 : วิ่ง 100 กม. ----------
st.markdown("### 🧮 วิ่ง 100 กม. ต้องจ่ายเท่าไหร่?")

r3c1, r3c2 = st.columns(2)

with r3c1:
    st.markdown("**ราคาเชื้อเพลิงตั้งต้น**")
    if cost_100_current is not None:
        st.write(f"วิ่ง 100 กม. → จ่ายประมาณ **{cost_100_current:,.2f} บาท**")
    else:
        st.write("⚠️ กรอกอัตราการสิ้นเปลืองให้ถูกต้องก่อน")

with r3c2:
    st.markdown("**ราคาที่คาดหวัง**")
    if show_future and cost_100_future is not None:
        st.write(f"วิ่ง 100 กม. → จ่ายประมาณ **{cost_100_future:,.2f} บาท**")
    else:
        st.write("⚠️ ยังไม่ได้กรอกราคาที่คาดหวัง (> 0)")
