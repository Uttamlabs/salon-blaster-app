import streamlit as st
import pandas as pd
import requests
import time

# =========================================================================
# ⚠️ META CREDENTIALS
# =========================================================================
MY_ACCESS_TOKEN = st.secrets["MY_ACCESS_TOKEN"]
MY_PHONE_NUMBER_ID = st.secrets["MY_PHONE_NUMBER_ID"]
# =========================================================================

# --- INITIAL APP SETUP ---
st.set_page_config(page_title="blaster // tools", page_icon="⚡", layout="centered")

# --- COBALT.TOOLS AESTHETIC CSS INJECTION ---
st.markdown("""
    <style>
        /* Import a clean monospaced tech font */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
        
        /* Global typography resets */
        * {
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Main background and clean text color */
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        
        /* Title styling - clean, minimal, no emojis */
        .main-title {
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            letter-spacing: -1px;
            margin-bottom: 5px;
            text-transform: lowercase;
        }
        .subtitle {
            font-size: 0.85rem;
            text-align: center;
            color: #666666;
            margin-bottom: 40px;
        }

        /* Cobalt Style Inputs & Text boxes */
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
        }
        
        /* Custom styling for text inputs */
        .stTextInput input {
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
            padding: 12px !important;
            color: #000000 !important;
        }

        /* Pill-shaped, bold outlined buttons exactly like Cobalt */
        div.stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 2px solid #000000 !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease;
            width: auto !important;
            margin: 0 auto !important;
            display: block !important;
        }
        
        div.stButton > button:hover {
            background-color: #ffffff !important;
            color: #000000 !important;
            transform: translateY(-1px);
        }

        /* --- BULLETPROOF FILE UPLOADER PATCH --- */
        section[data-testid="stFileUploader"] {
            border: 2px dashed #000000 !important;
            border-radius: 16px !important;
            background-color: #fafafa !important;
        }
        
        /* Reset the button so Streamlit's layout engine handles it natively */
        section[data-testid="stFileUploader"] button {
            all: revert; /* Strips away our global button styles to stop overlap */
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: 'JetBrains Mono', monospace !important;
            padding: 4px 12px !important;
            cursor: pointer !important;
        }

        /* Hide the broken Material Icon text in the uploader button */
        span[data-testid="stIconMaterial"] {
            display: none !important;
        }
        /* ---------------------------------- */

        /* Hide default streamlit branding clutter */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Dataframe crisp styling */
        .stDataFrame {
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# --- THE VISUAL FRONTEND ---

# Minimal Header
st.markdown('<div class="main-title">wa.blaster</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">simple, zero-subscription bulk utility</div>', unsafe_allow_html=True)

# Configuration Field (Centered and clean)
template_name = st.text_input("template id", value="salon_test_msg") # Updated default

st.space = st.markdown("<br>", unsafe_allow_html=True)

# Drag and drop area
uploaded_file = st.file_uploader("", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("📋 **batch preview**")
    st.dataframe(df.head(), use_container_width=True)
    
    # Tiny sleek metric line
    st.markdown(f"**total contacts loaded:** `{len(df)}` // **template:** `{template_name}`")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The Cobalt-style pill button
    if st.button("execute blast"):
        if "PASTE_YOUR_" in MY_ACCESS_TOKEN or "PASTE_YOUR_" in MY_PHONE_NUMBER_ID:
            st.error("Credentials missing in code.")
        else:
            url = f"https://graph.facebook.com/v19.0/{MY_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {MY_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            progress_bar = st.progress(0)
            success_count = 0
            
            for index, row in df.iterrows():
                customer_name = str(row['Name'])
                phone_number = str(row['Phone'])
                
                # UPDATED PAYLOAD: Uses your active template with NO variables and "en" language
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {"code": "en"}, 
                        "components": []
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    success_count += 1
                else:
                    try:
                        error_details = response.json().get('error', {}).get('message', 'Unknown Error')
                    except:
                        error_details = response.text
                    st.error(f"❌ Failed sending to {customer_name}. Meta Error: {error_details}")
                
                progress_bar.progress(int(((index + 1) / len(df)) * 100))
                time.sleep(0.4)
                
            st.toast(f"Successfully sent {success_count} messages!", icon="🚀")
            st.success(f"done. {success_count} messages delivered.")
