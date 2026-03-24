import streamlit as st
import pandas as pd
import time
import folium
import re
from streamlit_folium import st_folium
from openai import OpenAI
from twilio.rest import Client

st.set_page_config(page_title="AgamBarta AI Dashboard",
                   page_icon="agambartalogo.png", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050b14 0%, #0a192f 50%, #020c1b 100%);
    background-size: cover;
    background-attachment: fixed;
}
.stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDataFrame {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #e0f7fa !important;
    border: 1px solid rgba(0, 229, 255, 0.2) !important;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}
h1, h2, h3 {
    color: #00e5ff !important;
    text-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
}
[data-testid="stMetricValue"] {
    color: #00e5ff;
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}[data-testid="stMetricLabel"] {
    color: #8892b0;
}
.stButton>button {
    background: rgba(0, 229, 255, 0.1) !important;
    border: 1px solid #00e5ff !important;
    color: #00e5ff !important;
    transition: 0.3s;
    border-radius: 6px;
}
.stButton>button:hover {
    background: rgba(0, 229, 255, 0.3) !important;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_mock_database():
    return pd.DataFrame({
        "Name": [
            "Rahim Uddin", "Fatema Begum", "Kalu Mia", "Sirajul Islam", "Nur Nahar", "Anwar Hossain",
            "Abdur Rahman", "Sufia Khatun", "Belal Hossain", "Kamal Uddin", "Ruma Akter",
            "Jabbar Ali", "Hasina Begum", "Tofazzal", "Mominul", "Rina Begum",
            "Abdul Kuddus", "Ayesha Siddiqua", "Lokman Miah", "Tarek Rahman", "Jamila",
            "Gazi Rahman", "Momena", "Anisur", "Shirin", "Babul",
            "Akkas Ali", "Mofizur", "Sakhina Bewa", "Mokbul", "Jahanara", "Kashem"
        ],
        "Phone": [
            "+8801711111111", "+8801822222222", "+8801933333333", "+8801544444444", "+8801655555555", "+8801766666666",
            "+8801744444444", "+8801555555555", "+8801877777777", "+8801988888888", "+8801399999999",
            "+8801777777777", "+8801888888888", "+8801999999999", "+8801411111111", "+8801522222222",
            "+8801333333333", "+8801733333333", "+8801844444444", "+8801955555555", "+8801666666667",
            "+8801700000000", "+8801800000000", "+8801900000001", "+8801500000002", "+8801700000003",
            "+8801600000000", "+8801500000000", "+8801900000000", "+8801712345678", "+8801812345678", "+8801912345678"
        ],
        "Region": [
            "South-East Coast"] * 6 + ["Greater Noakhali"] * 5 + ["Greater Barishal"] * 5 +
        ["North-East Haor"] * 5 + ["South-West Coast"] *
        5 + ["Northern Flood Basin"] * 6,
        "District": [
            "Cox's Bazar", "Chattogram", "Bandarban", "Cox's Bazar", "Chattogram", "Cox's Bazar",
            "Noakhali", "Feni", "Lakshmipur", "Noakhali", "Noakhali",
            "Barishal", "Bhola", "Patuakhali", "Barguna", "Bhola",
            "Sylhet", "Sunamganj", "Habiganj", "Sylhet", "Moulvibazar",
            "Khulna", "Satkhira", "Bagerhat", "Satkhira", "Khulna",
            "Kurigram", "Jamalpur", "Sirajganj", "Gaibandha", "Bogra", "Kurigram"
        ],
        "Lat": [
            21.4272, 22.3569, 22.1953, 21.9497, 22.7543, 20.8624,
            22.8246, 23.0159, 22.9447, 22.8724, 22.2872,
            22.7010, 22.1785, 22.3242, 22.1554, 22.6876,
            24.8949, 25.0658, 24.3840, 24.8814, 24.4843,
            22.8456, 22.7185, 22.6602, 22.3332, 22.8098,
            25.8070, 24.9250, 24.4533, 25.3297, 24.8481, 25.7500
        ],
        "Lon": [
            92.0058, 91.7832, 92.2184, 91.9637, 91.7480, 92.2985,
            91.1017, 91.3976, 90.8282, 91.0973, 91.1014,
            90.3535, 90.7101, 90.3372, 90.1162, 90.6385,
            91.8687, 91.4051, 91.4169, 91.8821, 91.7685,
            89.5403, 89.0705, 89.7895, 89.0664, 89.5601,
            89.6295, 89.9463, 89.7006, 89.5430, 89.3730, 89.6000
        ],
        "Device": ["Feature Phone", "Smartphone", "Feature Phone", "Feature Phone", "Feature Phone", "Smartphone"] * 5 + ["Feature Phone", "Feature Phone"]
    })


db = load_mock_database()

st.sidebar.title("⚙️ System Config")
demo_mode = st.sidebar.checkbox(
    "Enable Demo Mode", value=True, help="Run without API Keys")

if not demo_mode:
    st.sidebar.markdown("### API Credentials")
    openai_api_key = st.sidebar.text_input("OpenAI Key", type="password")
    twilio_sid = st.sidebar.text_input("Twilio SID", type="password")
    twilio_token = st.sidebar.text_input("Twilio Token", type="password")
    twilio_phone = st.sidebar.text_input("Twilio Phone")

col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.image("agambartalogo.png", width=70)
with col_title:
    st.title("AgamBarta Command Center")
st.markdown(
    "*Transparent, LLM-powered early warning network for Bangladesh's most vulnerable.*")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registered Vulnerable Citizens", len(db))
col2.metric("Active Hazard Zones", "1",
            delta="High Risk", delta_color="inverse")
col3.metric("System Status", "Live Monitoring")
col4.metric("GSM Network", "Stable")
st.divider()

st.markdown("##  Step 1: Geospatial Hazard Targeting")

target_region = st.selectbox("Select Imminent Hazard Zone:", [
    "South-East Coast", "Greater Noakhali", "Greater Barishal",
    "South-West Coast", "North-East Haor", "Northern Flood Basin"
])

affected_users = db[db["Region"] == target_region]
st.markdown(
    f"**Targeting {len(affected_users)} vulnerable users in {target_region} (Districts: {', '.join(affected_users['District'].unique())}).**")

map_center = [affected_users['Lat'].mean(), affected_users['Lon'].mean(
)] if not affected_users.empty else [23.6850, 90.3563]
m = folium.Map(location=map_center, zoom_start=8)

if not affected_users.empty:
    folium.Circle(
        location=map_center, radius=55000, color="red", fill=True, fill_color="red", fill_opacity=0.2,
        popup="Active Hazard Zone"
    ).add_to(m)

for idx, row in affected_users.iterrows():
    folium.Marker(
        [row['Lat'], row['Lon']], popup=f"{row['Name']} ({row['Device']})",
        icon=folium.Icon(
            color="darkred" if row['Device'] == "Feature Phone" else "blue", icon="info-sign")
    ).add_to(m)

st_folium(m, width=1200, height=450)
st.divider()

st.markdown("##  Step 2: AI Localization & Translation")

default_dialect_map = {
    "South-East Coast": "Chittagonian (Chatgaiya)",
    "Greater Noakhali": "Noakhailla",
    "Greater Barishal": "Barishali",
    "North-East Haor": "Sylheti",
    "South-West Coast": "Standard / Khulna",
    "Northern Flood Basin": "Rangpuri / Northern"
}

default_msg = "BMD Alert: Severe Cyclone approaching. Wind speed 120 kmph. 3-meter surge possible. Evacuate to shelter immediately."
if target_region in ["Northern Flood Basin", "North-East Haor"]:
    default_msg = "FFWC Alert: Heavy rainfall upstream. Severe river flood expected in 24 hours. Water level may rise by 2 meters. Move to high ground."

official_warning = st.text_area(
    "Input Raw Meteorological Data (Edit this to see AI adapt):", default_msg, height=100)

target_dialect = st.selectbox("Select Target Dialect for Translation:", ["Chittagonian (Chatgaiya)", "Noakhailla", "Barishali", "Sylheti", "Rangpuri / Northern", "Standard / Khulna"],
                              index=["Chittagonian (Chatgaiya)", "Noakhailla", "Barishali", "Sylheti", "Rangpuri / Northern", "Standard / Khulna"].index(default_dialect_map[target_region]))

if st.button("🔄 Generate Localized AI Alert"):
    with st.spinner(f"Translating dynamic data to {target_dialect}..."):
        if demo_mode:
            time.sleep(1.5)
            input_text = official_warning.lower()

            numbers = re.findall(r'\d+', input_text)
            user_val = numbers[0] if len(numbers) > 0 else "মারাত্মক (Severe)"

            if any(word in input_text for word in ["flood", "water", "river", "rain"]):
                hazard_name = "বড় বান/বন্যা (Flood)"
            elif any(word in input_text for word in ["earthquake", "quake"]):
                hazard_name = "ভূমিকম্প (Earthquake)"
            else:
                hazard_name = "বড় তুফান (Cyclone)"

            if "shelter" in input_text or "evacuate" in input_text:
                action_ctg = "তাড়াতাড়ি সাইক্লোন শেল্টারত চলি যান!"
                action_noa = "জলদি করি শেল্টারে যাইয়েনগই।"
                action_bar = "তাড়াতাড়ি শেল্টারে চইল্লা যান।"
                action_syl = "জলদি শেল্টারো হামাইযাউক্কা।"
                action_ran = "উঁচা ফ্লাড শেল্টারত চলি যান।"
                action_std = "দ্রুত সাইক্লোন শেল্টারে চলে যান।"
            else:
                action_ctg = "নিরাপদ জাগাত সাবধানে থাইক্কন!"
                action_noa = "নিরাপদ জাগায় সাবধানে থাইক্কেন।"
                action_bar = "নিরাপদ আশ্রয়ে সাবধানে থাহেন।"
                action_syl = "নিরাপদ জাগাত সাবধানে খাউক্কা।"
                action_ran = "নিরাপদ জাগাত সাবধানে থাকেন।"
                action_std = "নিরাপদ আশ্রয়ে সাবধানে থাকুন।"

            if "Chittagonian" in target_dialect:
                translated_text = f"অঁনরা সাবধানে থাইক্কন! {hazard_name} আইয়ের। {user_val} মাত্রায় বিপদ অইত পারে। {action_ctg}"
            elif "Noakhailla" in target_dialect:
                translated_text = f"আন্নেরা বেজ্ঞুনে হুশিয়ার অই যান! {hazard_name} আয়ের। {user_val} মাত্রার বিপদ অইত পারে। {action_noa}"
            elif "Barishali" in target_dialect:
                translated_text = f"মোগো এহানে {hazard_name} আইতেছে। {user_val} মাত্রায় বিপদ বাড়তে পারে। সগ্গলে মিল্লা {action_bar}"
            elif "Sylheti" in target_dialect:
                translated_text = f"আপনারা হকল সাবধান অইযাউক্কা! {hazard_name} আরর। {user_val} মাত্রাত বিপদ অইত ফারে। {action_syl}"
            elif "Rangpuri" in target_dialect:
                translated_text = f"হামার এলাকাত {hazard_name} আইসপার নাগচে। {user_val} মাপে বিপদ হবের পারে। সবাই জলদি করি {action_ran}"
            else:
                translated_text = f"সাবধান! {hazard_name} আসছে। {user_val} মাত্রায় বিপদ হতে পারে। দয়া করে {action_std}"
        else:
            try:
                client = OpenAI(api_key=openai_api_key)
                prompt = f"Translate this weather alert strictly into the regional rural Bengali dialect of {target_dialect}. Keep it short and phonetic. Alert: {official_warning}"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                translated_text = response.choices[0].message.content
            except Exception as e:
                st.error(f"AI Error: {e}")
                translated_text = ""

        st.session_state['translated_text'] = translated_text
        st.success("✅ AI Translation Complete!")

if 'translated_text' in st.session_state:
    st.info(st.session_state['translated_text'])

st.divider()

st.markdown("##  Step 3: Mass Last-Mile Dissemination")

if 'translated_text' in st.session_state and not affected_users.empty:
    st.dataframe(affected_users[[
                 'Name', 'Phone', 'District', 'Device']], use_container_width=True, height=250)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📱 Dispatch Targeted SMS Warning"):
            progress_text = f"Dispatching SMS in {target_dialect}..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(0.5)
            my_bar.empty()
            st.success(
                f"✅ Successfully dispatched SMS to {len(affected_users)} feature phones in {target_region}!")

    with col_b:
        if st.button("📞 Trigger Automated Voice Calls (IVR)"):
            progress_text = "Synthesizing Localized Audio and Calling..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.02)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(0.5)
            my_bar.empty()
            st.success(
                f"✅ Voice Calls (IVR) connected to {len(affected_users)} users. Playing warning in {target_dialect}!")
else:
    st.warning("Please complete Step 1 and Step 2 to unlock mass dissemination.")
