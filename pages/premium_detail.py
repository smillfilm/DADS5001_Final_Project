import streamlit as st

def main():
    # Page configuration
    st.set_page_config(
        page_title="Oil Price Analysis Plans",
        page_icon="⛽",
        layout="wide"
    )
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .pricing-container {
        display: flex;
        gap: 1.5rem;
        margin: 2rem 0;
        justify-content: center;
    }
    
    .pricing-column {
        flex: 1;
        min-width: 280px;
        max-width: 350px;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        background: white;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .pricing-column::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    
    .pricing-column:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    }
    
    .free-column {
        border-top: 4px solid #6B7280;
    }
    
    .free-column::before {
        background: linear-gradient(90deg, #6B7280, #9CA3AF);
    }
    
    .pro-column {
        border-top: 4px solid #10a37f;
        transform: scale(1.02);
    }
    
    .pro-column::before {
        background: linear-gradient(90deg, #10a37f, #0d8c6c);
    }
    
    .pro-column:hover {
        transform: scale(1.02) translateY(-5px);
    }
    
    .enterprise-column {
        border-top: 4px solid #6C63FF;
    }
    
    .enterprise-column::before {
        background: linear-gradient(90deg, #6C63FF, #8B85FF);
    }
    
    .popular-badge {
        position: absolute;
        top: 15px;
        right: -30px;
        background: linear-gradient(45deg, #10a37f, #0d8c6c);
        color: white;
        padding: 0.4rem 2.5rem;
        font-size: 0.7rem;
        font-weight: 700;
        transform: rotate(45deg);
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
        z-index: 2;
    }
    
    .plan-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .plan-icon {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
    }
    
    .plan-name {
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #1a1a1a, #404040);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .free-name {
        background: linear-gradient(135deg, #6B7280, #9CA3AF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .pro-name {
        background: linear-gradient(135deg, #10a37f, #0d8c6c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .enterprise-name {
        background: linear-gradient(135deg, #6C63FF, #8B85FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .price-section {
        text-align: center;
        margin: 1.2rem 0;
        padding: 1.2rem;
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border-radius: 14px;
        border: 1px solid #F3F4F6;
    }
    
    .price-amount {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    
    .free-price {
        color: #6B7280;
        font-size: 1.4rem;
    }
    
    .pro-price {
        color: #10a37f;
    }
    
    .enterprise-price {
        color: #6C63FF;
    }
    
    .price-period {
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    
    .savings-badge {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-top: 0.3rem;
        display: inline-block;
    }
    
    .features-section {
        margin: 1.5rem 0;
    }
    
    .feature-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid #F3F4F6;
        min-height: 45px;
    }
    
    .feature-name {
        flex: 2;
        color: #374151;
        font-size: 0.8rem;
        font-weight: 500;
        line-height: 1.2;
    }
    
    .feature-status {
        flex: 1;
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        min-width: 40px;
    }
    
    .check-mark {
        color: #10a37f;
    }
    
    .x-mark {
        color: #EF4444;
    }
    
    .text-status {
        font-size: 0.75rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    .action-button {
        width: 100%;
        padding: 0.9rem 1.2rem;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .free-button {
        background: #6B7280;
        color: white;
    }
    
    .free-button:hover {
        background: #4B5563;
    }
    
    .pro-button {
        background: linear-gradient(135deg, #10a37f, #0d8c6c);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
    }
    
    .pro-button:hover {
        background: linear-gradient(135deg, #0d8c6c, #0a755a);
        box-shadow: 0 6px 20px rgba(16, 163, 127, 0.4);
    }
    
    .enterprise-button {
        background: linear-gradient(135deg, #6C63FF, #8B85FF);
        color: white;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }
    
    .enterprise-button:hover {
        background: linear-gradient(135deg, #5B52E8, #7A73FF);
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
    }
    
    .current-button {
        background: #D1D5DB;
        color: #6B7280;
        cursor: not-allowed;
    }
    
    .main-title {
        background: linear-gradient(135deg, #1a1a1a, #4B5563);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Ensure equal height for all columns */
    .pricing-column {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .features-section {
        flex-grow: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown("<h1 class='main-title' style='text-align: center; margin-bottom: 0.5rem; font-size: 2.2rem;'>⛽ Oil Price Analysis Plans</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 1rem; margin-bottom: 2rem;'>Choose the perfect plan for your oil price analysis needs</p>", unsafe_allow_html=True)

    # Create 3 equal columns
    col1, col2, col3 = st.columns(3)

    # Features data - same for all plans
    features_data = [
        ("Oil Price Data", "free", "up to 1 month", "pro", "up to 3 years", "enterprise", "up to 3 years"),
        ("Discount Coupon", "free", "X", "pro", "✓", "enterprise", "✓"),
        ("Compare Oil Type", "free", "X", "pro", "✓", "enterprise", "✓"),
        ("Compare Brand", "free", "X", "pro", "✓", "enterprise", "✓"),
        ("Agentic AI", "free", "X", "pro", "✓", "enterprise", "✓"),
        ("Backend User Data", "free", "X", "pro", "X", "enterprise", "✓"),
        ("Location Map", "free", "✓", "pro", "✓", "enterprise", "✓")
    ]

    # Column 1: FREE
    with col1:
        #st.markdown('<div class="pricing-column free-column">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="plan-header">', unsafe_allow_html=True)
        st.markdown('<div class="plan-icon">🆓</div>', unsafe_allow_html=True)
        st.markdown('<div class="plan-name free-name">FREE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Price
        st.markdown('<div class="price-section">', unsafe_allow_html=True)
        st.markdown('<div class="price-amount free-price">ฟรี</div>', unsafe_allow_html=True)
        st.markdown('<div class="price-period">เริ่มต้นใช้งาน</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Features
        st.markdown('<div class="features-section">', unsafe_allow_html=True)
        
        for feature_data in features_data:
            feature_name = feature_data[0]
            status = feature_data[2]
            
            if status == "✓":
                status_html = '<span class="check-mark">✓</span>'
            elif status == "X":
                status_html = '<span class="x-mark">✗</span>'
            else:
                status_html = f'<span class="text-status">{status}</span>'
                
            st.markdown(f'''
            <div class="feature-row">
                <div class="feature-name">{feature_name}</div>
                <div class="feature-status">
                    {status_html}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action Button
        st.button("เริ่มต้นใช้งาน", key="free_btn", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Column 2: PRO
    with col2:
        #st.markdown('<div class="pricing-column pro-column">', unsafe_allow_html=True)
        st.markdown('<div class="popular-badge">คุ้มค่า</div>', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="plan-header">', unsafe_allow_html=True)
        st.markdown('<div class="plan-icon">⚡</div>', unsafe_allow_html=True)
        st.markdown('<div class="plan-name pro-name">PRO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Price
        st.markdown('<div class="price-section">', unsafe_allow_html=True)
        st.markdown('<div class="price-amount pro-price">200฿</div>', unsafe_allow_html=True)
        st.markdown('<div class="price-period">ต่อเดือน</div>', unsafe_allow_html=True)
        st.markdown('<div class="price-amount pro-price" style="font-size: 1.1rem; margin-top: 0.3rem;">2,200฿<p style="font-size:12px; color:gray;" >(จากราคาปกติ 2,400฿)</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-period">ต่อปี</div>', unsafe_allow_html=True)
        st.markdown('<div class="savings-badge">ประหยัด 200฿</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Features
        st.markdown('<div class="features-section">', unsafe_allow_html=True)
        
        for feature_data in features_data:
            feature_name = feature_data[0]
            status = feature_data[4]
            
            if status == "✓":
                status_html = '<span class="check-mark">✓</span>'
            elif status == "X":
                status_html = '<span class="x-mark">✗</span>'
            else:
                status_html = f'<span class="text-status">{status}</span>'
                
            st.markdown(f'''
            <div class="feature-row">
                <div class="feature-name">{feature_name}</div>
                <div class="feature-status">
                    {status_html}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action Button
        if st.button("อัพเกรดเป็น PRO", key="pro_btn", use_container_width=True):
            st.success("🎉 กำลังดำเนินการอัพเกรดเป็นแผน PRO...")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Column 3: ENTERPRISE
    with col3:
        #st.markdown('<div class="pricing-column enterprise-column">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="plan-header">', unsafe_allow_html=True)
        st.markdown('<div class="plan-icon">🏢</div>', unsafe_allow_html=True)
        st.markdown('<div class="plan-name enterprise-name">ENTERPRISE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Price
        st.markdown('<div class="price-section">', unsafe_allow_html=True)
        st.markdown('<div class="price-amount enterprise-price">500฿</div>', unsafe_allow_html=True)
        st.markdown('<div class="price-period">ต่อเดือน</div>', unsafe_allow_html=True)
        st.markdown('<div class="price-amount enterprise-price" style="font-size: 1.1rem; margin-top: 0.3rem;">5,500฿<p style="font-size:12px; color:gray;">(จากราคาปกติ 6,000฿)</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-period">ต่อปี</div>', unsafe_allow_html=True)
        st.markdown('<div class="savings-badge">ประหยัด 500฿</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Features
        st.markdown('<div class="features-section">', unsafe_allow_html=True)
        
        for feature_data in features_data:
            feature_name = feature_data[0]
            status = feature_data[6]
            
            if status == "✓":
                status_html = '<span class="check-mark">✓</span>'
            elif status == "X":
                status_html = '<span class="x-mark">✗</span>'
            else:
                status_html = f'<span class="text-status">{status}</span>'
                
            st.markdown(f'''
            <div class="feature-row">
                <div class="feature-name">{feature_name}</div>
                <div class="feature-status">
                    {status_html}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action Button
        if st.button("ติดต่อฝ่ายขาย", key="enterprise_btn", use_container_width=True):
            st.success("🤝 ทีมงานฝ่ายขายจะติดต่อคุณเร็วๆ นี้!")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer section
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 0.85rem; margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 14px;'>
        <div style='font-weight: 600; color: #374151; margin-bottom: 0.8rem;'>💡 ข้อมูลเพิ่มเติม</div>
        <div style='display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 0.8rem; font-size: 0.8rem;'>
            <span>✓ รับประกันคืนเงินภายใน 7 วัน</span>
            <span>✓ การชำระเงินที่ปลอดภัย</span>
            <span>✓ สนับสนุนลูกค้า 24/7</span>
        </div>
        <div style='font-size: 0.8rem;'>
            มีคำถาม? 
            <a href="#" style='color: #6C63FF; text-decoration: none; font-weight: 600; margin: 0 0.3rem;'>ติดต่อเรา</a> 
            หรือ 
            <a href="#" style='color: #6C63FF; text-decoration: none; font-weight: 600; margin: 0 0.3rem;'>อ่านคำถามที่พบบ่อย</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()