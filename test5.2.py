import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime
import pytz

# 🔐 API key gắn trực tiếp
GEMINI_API_KEY = "AIzaSyBBRBfkvzjngvok5MT6yqveb7hY6Gk8b7k"
WEATHER_API_KEY = "e7c8cefb28a5ab6d805c8bfe89f59375"

# ⚙️ Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# 🕒 Lấy giờ Việt Nam chính xác
def get_current_time_vietnam():
    try:
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        now = datetime.now(tz)
        return now.strftime("%H:%M:%S")
    except:
        return None

# 📆 Lấy ngày hôm nay theo tiếng Việt
def get_current_date_vietnam():
    try:
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        now = datetime.now(tz)
        weekdays = {
            0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư",
            3: "Thứ Năm", 4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"
        }
        weekday = weekdays[now.weekday()]
        return f"Hôm nay là {weekday}, ngày {now.day} tháng {now.month} năm {now.year}."
    except:
        return None

# 🌡️ Lấy thời tiết
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=vi"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return None
        temp = response["main"]["temp"]
        weather = response["weather"][0]["description"]
        return f"Nhiệt độ hiện tại ở {city.title()} là {temp}°C, trời {weather}."
    except:
        return None

# 🚀 Giao diện
st.set_page_config(page_title="Gemini Chatbot ", page_icon="🌤️")
st.title("🤖 Gemini Chatbot ")

# Lưu lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ô nhập câu hỏi
query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    query_lower = query.lower()
    reply = ""

    # Nếu hỏi về thời tiết
    if "nhiệt độ" in query_lower or "thời tiết" in query_lower:
        for word in query_lower.split():
            result = get_weather(word)
            if result:
                reply = result
                break

    # Nếu hỏi về thời gian hoặc ngày hôm nay
    elif "mấy giờ" in query_lower or "thời gian" in query_lower or "hôm nay là" in query_lower or "ngày mấy" in query_lower:
        if "ngày" in query_lower or "thứ" in query_lower:
            reply = get_current_date_vietnam()
        elif "giờ" in query_lower or "mấy giờ" in query_lower:
            time_now = get_current_time_vietnam()
            reply = f"Bây giờ là {time_now} (giờ Việt Nam)"
        else:
            # Nếu không rõ → trả cả ngày + giờ
            date = get_current_date_vietnam()
            time = get_current_time_vietnam()
            reply = f"{date}, bây giờ là {time} (giờ Việt Nam)"

    # Nếu không phải thời gian/thời tiết → dùng Gemini
    if not reply:
        reply = model.generate_content(query).text

    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})