import streamlit as st
import duckdb
import hashlib
import re
from datetime import datetime
import os

st.set_page_config(page_title="Create Account", page_icon="👤", layout="centered")

st.title("Create Your Account")

# Initialize session state for form persistence
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        max-width: 500px;
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

def init_database():
    """Initialize DuckDB database and create users table if it doesn't exist"""
    try:
        # Connect to DuckDB (creates the file if it doesn't exist)
        conn = duckdb.connect('user_database.db')
        
        # Create users table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP
            )
        """)
        
        # Create sequence for user_id if it doesn't exist
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS user_id_seq START 1
        """)
        
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Get connection to DuckDB database"""
    try:
        return duckdb.connect('user_database.db')
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def check_existing_user(conn, username, email):
    """Check if username or email already exists"""
    try:
        query = """
        SELECT COUNT(*) FROM users 
        WHERE username = ? OR email = ?
        """
        result = conn.execute(query, (username, email)).fetchone()
        return result[0] > 0
    except Exception as e:
        st.error(f"Error checking existing user: {e}")
        return True

def create_user(conn, username, email, password_hash):
    """Insert new user into database"""
    try:
        query = """
        INSERT INTO users (user_id, username, email, password_hash, created_at, is_active)
        VALUES (nextval('user_id_seq'), ?, ?, ?, ?, ?)
        """
        conn.execute(query, (username, email, password_hash, datetime.now(), True))
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def main():
    # Initialize database
    if not init_database():
        st.error("Failed to initialize database. Please check the application.")
        return

    # Create form
    with st.form("signup_form"):
        st.subheader("Create New Account")
        
        username = st.text_input("Username", placeholder="Enter your username", max_chars=50)
        email = st.text_input("Email", placeholder="Enter your email", max_chars=100)
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms and Conditions")
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            # Validate form
            errors = []
            
            if not username:
                errors.append("Username is required")
            elif len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if not email:
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Please enter a valid email address")
            
            if not password:
                errors.append("Password is required")
            else:
                is_valid, password_msg = validate_password(password)
                if not is_valid:
                    errors.append(password_msg)
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if not agree_terms:
                errors.append("You must agree to the Terms and Conditions")
            
            # If no errors, proceed with user creation
            if not errors:
                conn = get_db_connection()
                if conn:
                    try:
                        # Check if user already exists
                        if check_existing_user(conn, username, email):
                            st.error("Username or email already exists. Please choose different credentials.")
                        else:
                            # Hash password and create user
                            password_hash = hash_password(password)
                            if create_user(conn, username, email, password_hash):
                                st.session_state.form_submitted = True
                                st.success("🎉 Account created successfully! You can now log in.")
                                # Clear form
                                st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error during user creation: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("Could not connect to database.")
            else:
                for error in errors:

                    st.error(error)
    
    # Password strength indicator
    if password:
        is_valid, message = validate_password(password)
        if is_valid:
            st.success("✅ " + message)
        else:
            st.warning("⚠️ " + message)

    # Terms and conditions link
    st.markdown("---")
    st.markdown("""
    **Terms and Conditions**
    - By creating an account, you agree to our privacy policy
    - You must be at least 13 years old to register
    - You are responsible for maintaining the confidentiality of your account
    """)
    
    # Debug info (optional - remove in production)
    if st.checkbox("Show debug info"):
        conn = get_db_connection()
        if conn:
            try:
                users = conn.execute("SELECT * FROM users").fetchall()
                st.write("Current users in database:", users)
            except Exception as e:
                st.write("Error reading users:", e)
            finally:
                conn.close()

if __name__ == "__main__":
    main()