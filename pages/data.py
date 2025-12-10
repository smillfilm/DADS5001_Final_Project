import streamlit as st
import plotly.express as px

# สมมติว่า conn เป็น Snowflake connection ที่ใช้ได้
conn = st.connection("snowflake")
df = conn.query("""
    select ot.date_transaction, c.company_name, tot.type_name, ot.price 
    from oil_transaction ot 
    join oil_type tot on ot.type_id = tot.type_no 
    join company c on ot.company_id = c.company_id
""", ttl="10m")


# สร้างกราฟ Plotly
fig = px.bar(
    df,
    x='COMPANY_NAME',  # หรือ 'company_name' ขึ้นกับชื่อคอลัมน์จริง
    y='PRICE',         # หรือ 'price'
    color='TYPE_NAME', # หรือ 'type_name'
    barmode='group',
    title='เปรียบเทียบราคาน้ำมันแต่ละปั๊ม (19 พ.ย. 2025)',
    labels={'PRICE':'ราคา (บาท)','COMPANY_NAME':'ปั๊ม'}
)

# แสดงกราฟใน Streamlit
st.plotly_chart(fig, use_container_width=True)

# แสดง DataFrame
st.dataframe(df)


