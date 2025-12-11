import streamlit as st


st.set_page_config(page_title="AI Text & Image Tools", page_icon="📝")
st.title("AI Text & Image Tools")
st.write(
    "Use the sidebar to open Text Tools, Image Tools, or History. "
    "Enter your Google Gemini API Key here to enable the text tools."
)

st.sidebar.subheader("Google Gemini Settings")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password", key="sidebar_gemini_key")
if gemini_key:
    st.session_state["gemini_api_key"] = gemini_key
    st.sidebar.success("Gemini API Key saved.")
else:
    st.sidebar.info("Enter a Gemini API Key; other pages will reuse it automatically.")

# Hide the auto-generated top-level "app" entry in the sidebar nav
hide_sidebar_title = """
    <style>
        /* Hide the auto-generated root "app" entry in the sidebar nav */
        [data-testid="stSidebarNav"] ul li:nth-of-type(1) {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_sidebar_title, unsafe_allow_html=True)

st.subheader("Quick Links")
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_Text_Tools.py", label="Text Tools", icon="📝")
with col2:
    st.page_link("pages/2_Image_Tools.py", label="Image Tools", icon="🖼")
with col3:
    st.page_link("pages/3_History.py", label="History", icon="📜")
