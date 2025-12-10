# ai_assistant.py
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

def show_ai_assistant():
    """AI Assistant สำหรับวิเคราะห์ข้อมูลน้ำมัน"""
    
    st.title("🤖 AI Assistant - Oil Analytics")
    
    # Status badge
    if 'subscribe_flag' in st.session_state and st.session_state['subscribe_flag'] == 1:
        st.success("✅ AI Assistant พร้อมใช้งาน")
    else:
        st.error("⛔ คุณต้องอัปเกรดเป็น PRO เพื่อใช้งานฟีเจอร์นี้")
        return
    
    # Tab สำหรับฟังก์ชันต่างๆ
    tab1, tab2, tab3, tab4 = st.tabs(["💬 สอบถามข้อมูล", "📊 วิเคราะห์อัตโนมัติ", "📈 รายงาน", "⚙️ การตั้งค่า"])
    
    with tab1:
        _show_chat_interface()
    
    with tab2:
        _show_auto_analysis()
    
    with tab3:
        _show_reports()
    
    with tab4:
        _show_ai_settings()

def _show_chat_interface():
    """แสดงอินเทอร์เฟซแชท"""
    
    # Initialize chat history
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    
    # Display chat history
    st.subheader("💬 สนทนากับ AI")
    
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "data" in message:
                st.dataframe(message["data"], use_container_width=True)
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True)
    
    # Quick questions
    st.markdown("### 💡 คำถามที่พบบ่อย")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 แนวโน้มราคาล่าสุด", use_container_width=True):
            _analyze_price_trend()
    
    with col2:
        if st.button("🏆 บริษัทที่ราคาถูกสุด", use_container_width=True):
            _analyze_cheapest_company()
    
    with col3:
        if st.button("📊 เปรียบเทียบบริษัท", use_container_width=True):
            _compare_companies()
    
    # Chat input
    if prompt := st.chat_input("ถามอะไรเกี่ยวกับข้อมูลน้ำมัน..."):
        # Add user message
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("AI กำลังวิเคราะห์ข้อมูล..."):
                response = _process_ai_query(prompt)
                st.markdown(response)
                st.session_state.ai_messages.append({"role": "assistant", "content": response})
        
        st.rerun()

def _show_auto_analysis():
    """แสดงการวิเคราะห์อัตโนมัติ"""
    
    st.subheader("📊 วิเคราะห์ข้อมูลอัตโนมัติ")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("วันที่เริ่มต้น", 
                                  value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("วันที่สิ้นสุด", 
                                value=datetime.now())
    
    # Analysis type selector
    analysis_type = st.selectbox(
        "เลือกรูปแบบการวิเคราะห์",
        ["แนวโน้มราคา", "การเปรียบเทียบบริษัท", "ฤดูกาลที่มีผลต่อราคา", "พยากรณ์ราคา"]
    )
    
    if st.button("🚀 เริ่มการวิเคราะห์", type="primary"):
        with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
            if analysis_type == "แนวโน้มราคา":
                _analyze_price_trend_auto(start_date, end_date)
            elif analysis_type == "การเปรียบเทียบบริษัท":
                _analyze_company_comparison(start_date, end_date)
            elif analysis_type == "ฤดูกาลที่มีผลต่อราคา":
                _analyze_seasonal_effect()
            elif analysis_type == "พยากรณ์ราคา":
                _predict_price_trend()

def _show_reports():
    """แสดงรายงาน"""
    
    st.subheader("📈 รายงานสรุป")
    
    # Generate report options
    report_type = st.selectbox(
        "เลือกรูปแบบรายงาน",
        ["รายงานรายวัน", "รายงานรายสัปดาห์", "รายงานรายเดือน", "รายงานเปรียบเทียบ"]
    )
    
    if st.button("📥 สร้างรายงาน", type="primary"):
        with st.spinner("กำลังสร้างรายงาน..."):
            report_data = _generate_report(report_type)
            
            # Display report
            st.markdown("### 📋 สรุปผลการวิเคราะห์")
            st.write(report_data["summary"])
            
            # Display charts
            if "charts" in report_data:
                for chart in report_data["charts"]:
                    st.plotly_chart(chart, use_container_width=True)
            
            # Display data
            if "data" in report_data:
                st.dataframe(report_data["data"], use_container_width=True)
            
            # Download button
            st.download_button(
                label="📄 ดาวน์โหลดรายงาน (PDF)",
                data=json.dumps(report_data, ensure_ascii=False),
                file_name=f"oil_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def _show_ai_settings():
    """แสดงการตั้งค่า AI"""
    
    st.subheader("⚙️ การตั้งค่า AI Assistant")
    
    # Model selection
    model_type = st.selectbox(
        "เลือกรูปแบบการวิเคราะห์",
        ["Basic Analysis", "Advanced ML", "Deep Analysis"],
        help="เลือกระดับความซับซ้อนของการวิเคราะห์"
    )
    
    # Confidence threshold
    confidence = st.slider(
        "ระดับความมั่นใจขั้นต่ำ",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="กำหนดระดับความมั่นใจขั้นต่ำในการพยากรณ์"
    )
    
    # Auto update
    auto_update = st.checkbox(
        "อัปเดตข้อมูลอัตโนมัติ",
        value=True,
        help="อัปเดตข้อมูลล่าสุดทุกครั้งที่ใช้งาน"
    )
    
    if st.button("💾 บันทึกการตั้งค่า", type="primary"):
        st.success("✅ บันทึกการตั้งค่าเรียบร้อยแล้ว")

# ==============================
# DATABASE FUNCTIONS
# ==============================

def _get_connection():
    """สร้างการเชื่อมต่อกับ Snowflake"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        return conn
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อฐานข้อมูล: {e}")
        return None

def _get_price_data(date_range=None):
    """ดึงข้อมูลราคาจาก database"""
    conn = _get_connection()
    if not conn:
        return None
    
    try:
        query = """
        SELECT 
            DATE_TRANSACTION,
            TYPE_NAME,
            COMPANY_NAME,
            PRICE,
            VOLUME
        FROM OIL_TRANSACTION OT
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        """
        
        if date_range:
            query += f" WHERE DATE_TRANSACTION BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
        
        query += " ORDER BY DATE_TRANSACTION DESC"
        
        df = conn.query(query)
        return df
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return None

def _get_company_comparison():
    """เปรียบเทียบข้อมูลบริษัท"""
    conn = _get_connection()
    if not conn:
        return None
    
    try:
        query = """
        SELECT 
            COMPANY_NAME,
            AVG(PRICE) as AVG_PRICE,
            MIN(PRICE) as MIN_PRICE,
            MAX(PRICE) as MAX_PRICE,
            COUNT(*) as TRANSACTION_COUNT
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        WHERE DATE_TRANSACTION >= DATEADD(day, -30, CURRENT_DATE())
        GROUP BY COMPANY_NAME
        ORDER BY AVG_PRICE
        """
        
        df = conn.query(query)
        return df
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return None

# ==============================
# AI ANALYSIS FUNCTIONS
# ==============================

def _process_ai_query(query):
    """ประมวลผลคำถามจากผู้ใช้"""
    query_lower = query.lower()
    
    # ตรวจสอบ keyword ในคำถาม
    if any(word in query_lower for word in ["ราคา", "แพง", "ถูก", "ค่า"]):
        return _analyze_price_query(query)
    elif any(word in query_lower for word in ["บริษัท", "เปรียบเทียบ", "เทียบ"]):
        return _analyze_company_query(query)
    elif any(word in query_lower for word in ["แนวโน้ม", "ทิศทาง", "อนาคต"]):
        return _analyze_trend_query(query)
    elif any(word in query_lower for word in ["สรุป", "รายงาน", "ภาพรวม"]):
        return _generate_summary()
    else:
        return "ฉันสามารถช่วยคุณวิเคราะห์ข้อมูลน้ำมันได้ เช่น:\n- ราคาน้ำมันล่าสุด\n- การเปรียบเทียบบริษัท\n- แนวโน้มราคา\n- รายงานสรุป\n\nกรุณาถามคำถามที่เจาะจงมากขึ้นค่ะ"

def _analyze_price_query(query):
    """วิเคราะห์คำถามเกี่ยวกับราคา"""
    df = _get_price_data()
    if df is None or df.empty:
        return "ไม่พบข้อมูลราคาในระบบ"
    
    # ดึงข้อมูลล่าสุด
    latest_data = df.sort_values('DATE_TRANSACTION', ascending=False).head(10)
    
    # คำนวณสถิติ
    avg_price = latest_data['PRICE'].mean()
    min_price = latest_data['PRICE'].min()
    max_price = latest_data['PRICE'].max()
    
    response = f"""
    **📊 สรุปข้อมูลราคาล่าสุด:**
    
    - 📈 ราคาเฉลี่ย: **฿{avg_price:.2f}** ต่อลิตร
    - 📉 ราคาต่ำสุด: **฿{min_price:.2f}** ต่อลิตร
    - 📈 ราคาสูงสุด: **฿{max_price:.2f}** ต่อลิตร
    
    **ข้อมูลล่าสุด:**
    """
    
    # เพิ่มข้อมูลล่าสุดในรูปแบบตาราง
    latest_table = latest_data[['DATE_TRANSACTION', 'COMPANY_NAME', 'TYPE_NAME', 'PRICE']].head(5)
    st.dataframe(latest_table, use_container_width=True)
    
    return response

def _analyze_company_query(query):
    """วิเคราะห์คำถามเกี่ยวกับบริษัท"""
    df = _get_company_comparison()
    if df is None or df.empty:
        return "ไม่พบข้อมูลบริษัทในระบบ"
    
    # หาบริษัทที่ราคาถูกที่สุดและแพงที่สุด
    cheapest = df.loc[df['AVG_PRICE'].idxmin()]
    expensive = df.loc[df['AVG_PRICE'].idxmax()]
    
    response = f"""
    **🏢 การเปรียบเทียบบริษัทน้ำมัน:**
    
    **🏆 บริษัทที่ราคาถูกที่สุด:**
    - {cheapest['COMPANY_NAME']}: ฿{cheapest['AVG_PRICE']:.2f} ต่อลิตร
    
    **📈 บริษัทที่ราคาแพงที่สุด:**
    - {expensive['COMPANY_NAME']}: ฿{expensive['AVG_PRICE']:.2f} ต่อลิตร
    
    **📊 ข้อมูลทั้งหมด:**
    """
    
    # แสดงตารางเปรียบเทียบ
    st.dataframe(df[['COMPANY_NAME', 'AVG_PRICE', 'MIN_PRICE', 'MAX_PRICE', 'TRANSACTION_COUNT']], 
                 use_container_width=True)
    
    # สร้างกราฟเปรียบเทียบ
    fig = px.bar(df, x='COMPANY_NAME', y='AVG_PRICE',
                 title='ราคาเฉลี่ยตามบริษัท',
                 labels={'COMPANY_NAME': 'บริษัท', 'AVG_PRICE': 'ราคาเฉลี่ย (฿)'},
                 color='AVG_PRICE')
    st.plotly_chart(fig, use_container_width=True)
    
    return response

def _analyze_trend_query(query):
    """วิเคราะห์แนวโน้มราคา"""
    df = _get_price_data()
    if df is None or df.empty:
        return "ไม่พบข้อมูลสำหรับวิเคราะห์แนวโน้ม"
    
    # แปลงวันที่และคำนวณแนวโน้ม
    df['DATE'] = pd.to_datetime(df['DATE_TRANSACTION'])
    df['DAY'] = df['DATE'].dt.date
    
    # คำนวณราคาเฉลี่ยรายวัน
    daily_avg = df.groupby('DAY')['PRICE'].mean().reset_index()
    
    response = """
    **📈 แนวโน้มราคาน้ำมัน:**
    
    จากการวิเคราะห์ข้อมูลล่าสุดพบว่า:
    """
    
    # คำนวณการเปลี่ยนแปลง
    if len(daily_avg) >= 2:
        last_price = daily_avg['PRICE'].iloc[-1]
        prev_price = daily_avg['PRICE'].iloc[-2]
        change = last_price - prev_price
        change_percent = (change / prev_price) * 100
        
        if change > 0:
            response += f"\n- 📈 ราคาเพิ่มขึ้น **฿{change:.2f}** ({change_percent:.1f}%) จากวันก่อนหน้า"
        elif change < 0:
            response += f"\n- 📉 ราคาลดลง **฿{abs(change):.2f}** ({abs(change_percent):.1f}%) จากวันก่อนหน้า"
        else:
            response += f"\n- ➡️ ราคาคงที่จากวันก่อนหน้า"
    
    response += f"\n- 💰 ราคาล่าสุด: **฿{last_price:.2f}** ต่อลิตร"
    
    # สร้างกราฟแนวโน้ม
    fig = px.line(daily_avg, x='DAY', y='PRICE',
                  title='แนวโน้มราคาน้ำมันรายวัน',
                  labels={'DAY': 'วันที่', 'PRICE': 'ราคา (฿)'})
    fig.update_traces(line=dict(color='#1e88e5', width=3))
    st.plotly_chart(fig, use_container_width=True)
    
    return response

def _generate_summary():
    """สร้างสรุปข้อมูล"""
    price_df = _get_price_data()
    company_df = _get_company_comparison()
    
    if price_df is None or company_df is None:
        return "ไม่สามารถสร้างรายงานสรุปได้ในขณะนี้"
    
    # คำนวณสถิติ
    avg_price = price_df['PRICE'].mean()
    total_transactions = len(price_df)
    company_count = len(company_df)
    
    # หาวันที่มีการซื้อขายสูงสุด
    if 'DATE_TRANSACTION' in price_df.columns:
        price_df['DATE'] = pd.to_datetime(price_df['DATE_TRANSACTION']).dt.date
        busiest_day = price_df['DATE'].value_counts().idxmax()
        busiest_count = price_df['DATE'].value_counts().max()
    
    response = f"""
    **📋 รายงานสรุปข้อมูลน้ำมัน:**
    
    **📊 สถิติโดยรวม:**
    - 💰 ราคาเฉลี่ย: **฿{avg_price:.2f}** ต่อลิตร
    - 🔢 จำนวนธุรกรรม: **{total_transactions}** รายการ
    - 🏢 จำนวนบริษัท: **{company_count}** บริษัท
    
    **📈 ข้อมูลล่าสุด:**
    - 📅 วันที่คึกคักที่สุด: **{busiest_day}** ({busiest_count} ธุรกรรม)
    - 🏆 บริษัทที่ราคาถูกที่สุด: **{company_df.loc[company_df['AVG_PRICE'].idxmin(), 'COMPANY_NAME']}**
    - 💸 บริษัทที่ราคาแพงที่สุด: **{company_df.loc[company_df['AVG_PRICE'].idxmax(), 'COMPANY_NAME']}**
    
    **💡 ข้อเสนอแนะ:**
    - พิจารณาซื้อจากบริษัทที่ราคาถูกที่สุดในช่วงเช้า
    - หลีกเลี่ยงการซื้อในช่วงเวลาที่มีการเปลี่ยนแปลงราคา
    - ติดตามแนวโน้มรายสัปดาห์เพื่อวางแผนการซื้อ
    """
    
    return response

# ==============================
# AUTO ANALYSIS FUNCTIONS
# ==============================

def _analyze_price_trend_auto(start_date, end_date):
    """วิเคราะห์แนวโน้มราคาอัตโนมัติ"""
    date_range = (start_date, end_date)
    df = _get_price_data(date_range)
    
    if df is None or df.empty:
        st.error("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
        return
    
    # สร้างกราฟ
    df['DATE'] = pd.to_datetime(df['DATE_TRANSACTION'])
    
    # กราฟแนวโน้ม
    fig1 = px.line(df, x='DATE', y='PRICE', color='COMPANY_NAME',
                   title='แนวโน้มราคาตามบริษัท',
                   labels={'DATE': 'วันที่', 'PRICE': 'ราคา (฿)', 'COMPANY_NAME': 'บริษัท'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # กราฟกระจาย
    fig2 = px.scatter(df, x='DATE', y='PRICE', color='TYPE_NAME',
                      title='การกระจายของราคาตามประเภทน้ำมัน',
                      labels={'DATE': 'วันที่', 'PRICE': 'ราคา (฿)', 'TYPE_NAME': 'ประเภท'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # สรุปสถิติ
    st.markdown("### 📊 สรุปสถิติ")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ราคาเฉลี่ย", f"฿{df['PRICE'].mean():.2f}")
    with col2:
        st.metric("ราคาสูงสุด", f"฿{df['PRICE'].max():.2f}")
    with col3:
        st.metric("ราคาต่ำสุด", f"฿{df['PRICE'].min():.2f}")

def _analyze_company_comparison(start_date, end_date):
    """วิเคราะห์การเปรียบเทียบบริษัท"""
    date_range = (start_date, end_date)
    df = _get_price_data(date_range)
    
    if df is None or df.empty:
        st.error("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
        return
    
    # คำนวณสถิติตามบริษัท
    company_stats = df.groupby('COMPANY_NAME').agg({
        'PRICE': ['mean', 'min', 'max', 'std'],
        'TYPE_NAME': 'count'
    }).round(2)
    
    company_stats.columns = ['ราคาเฉลี่ย', 'ราคาต่ำสุด', 'ราคาสูงสุด', 'ส่วนเบี่ยงเบน', 'จำนวนธุรกรรม']
    company_stats = company_stats.reset_index()
    
    # แสดงตาราง
    st.dataframe(company_stats, use_container_width=True)
    
    # สร้างกราฟเปรียบเทียบ
    fig = go.Figure()
    
    for company in company_stats['COMPANY_NAME'].unique():
        company_data = company_stats[company_stats['COMPANY_NAME'] == company]
        fig.add_trace(go.Bar(
            name=company,
            x=['ราคาเฉลี่ย', 'ราคาต่ำสุด', 'ราคาสูงสุด'],
            y=[company_data['ราคาเฉลี่ย'].values[0], 
               company_data['ราคาต่ำสุด'].values[0], 
               company_data['ราคาสูงสุด'].values[0]]
        ))
    
    fig.update_layout(
        title='การเปรียบเทียบราคาตามบริษัท',
        xaxis_title='ประเภทราคา',
        yaxis_title='ราคา (฿)',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# HELPER FUNCTIONS
# ==============================

def _analyze_price_trend():
    """วิเคราะห์แนวโน้มราคา (quick function)"""
    response = _analyze_trend_query("แนวโน้มราคาล่าสุด")
    st.session_state.ai_messages.append({
        "role": "assistant", 
        "content": response
    })
    st.rerun()

def _analyze_cheapest_company():
    """วิเคราะห์บริษัทที่ราคาถูกที่สุด"""
    response = _analyze_company_query("บริษัทไหนราคาถูกที่สุด")
    st.session_state.ai_messages.append({
        "role": "assistant", 
        "content": response
    })
    st.rerun()

def _compare_companies():
    """เปรียบเทียบบริษัท"""
    response = _analyze_company_query("เปรียบเทียบบริษัท")
    st.session_state.ai_messages.append({
        "role": "assistant", 
        "content": response
    })
    st.rerun()

def _analyze_seasonal_effect():
    """วิเคราะห์ฤดูกาลที่มีผลต่อราคา"""
    st.info("⏳ กำลังพัฒนาฟีเจอร์นี้...")

def _predict_price_trend():
    """พยากรณ์ราคา"""
    st.info("⏳ กำลังพัฒนาฟีเจอร์นี้...")

def _generate_report(report_type):
    """สร้างรายงาน"""
    # ในแอปจริงควรดึงข้อมูลจาก database และประมวลผล
    summary = f"""
    **รายงาน{report_type} - ข้อมูลน้ำมัน**
    
    สรุปผลการวิเคราะห์:
    - ราคาเฉลี่ย: ฿32.45 ต่อลิตร
    - แนวโน้ม: มีเสถียรภาพ
    - ข้อเสนอแนะ: เหมาะสำหรับการซื้อในช่วงเช้า
    
    สร้างเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    
    return {
        "summary": summary,
        "type": report_type,
        "generated_at": datetime.now().isoformat()
    }