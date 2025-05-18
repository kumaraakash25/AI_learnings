import streamlit as st
from datetime import date

st.title("Simple Daily Tracker")

entry_date = st.date_input("Date", value=date.today())
tasks_done = st.text_area("What did you do today?", height=150)
mood = st.selectbox("Mood", ["😃 Great", "🙂 Good", "😐 Okay", "😔 Meh", "😩 Bad"])

if st.button("Save Entry"):
    if tasks_done.strip():
        st.success("✅ Entry saved!")
        st.markdown("---")
        st.subheader(f"📋 Entry for {entry_date}")
        st.write(f"**Mood:** {mood}")
        st.write(f"**Tasks:**\n{tasks_done}")
    else:
        st.warning("Please write something before saving.")
