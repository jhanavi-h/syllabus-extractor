import streamlit as st
import anthropic
import json
import re
from pypdf import PdfReader
import io

from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("anthropic_api_key")

#API_KEY = anthropic_api_key

st.title("Syllabus Deadline Extractor")
st.write("Upload a PDF or paste your syllabus text below.")

uploaded_file = st.file_uploader("Upload syllabus PDF (optional)", type="pdf")
syllabus_text = st.text_area("Or paste your syllabus here", height=300)

if st.button("Extract Deadlines"):
    final_text = ""

    if uploaded_file and syllabus_text.strip():
        st.info("Both a PDF and text were provided — using the PDF.")
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        for page in reader.pages:
            final_text += page.extract_text()

    elif uploaded_file:
        st.info("Reading your PDF...")
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        for page in reader.pages:
            final_text += page.extract_text()
        if not final_text.strip():
            st.error("Couldn't extract text from this PDF. It may be scanned or image-based. Try pasting the text manually instead.")

    elif syllabus_text.strip():
        final_text = syllabus_text

    else:
        st.error("Please upload a PDF or paste some syllabus text first.")

    if final_text.strip():
        with st.spinner("Extracting deadlines..."):
            client = anthropic.Anthropic(api_key=API_KEY)
            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Extract all deadlines and assignments from this syllabus.
Return ONLY a JSON array with no explanation, no markdown, no code fences. Each item should have:
- "title": name of the assignment or exam
- "date": the due date as YYYY-MM-DD if possible, otherwise as written
- "description": one short sentence about what it is

If there are no deadlines or dates at all, return an empty array: []

Syllabus:
{final_text}"""
                    }
                ]
            )

            raw = message.content[0].text
            match = re.search(r'\[.*\]', raw, re.DOTALL)

            if not match:
                st.error("Something went wrong reading the response. Please try again.")
            else:
                deadlines = json.loads(match.group())

                if len(deadlines) == 0:
                    st.warning("No deadlines or dates were found in this syllabus. Make sure the document contains assignment or exam dates.")
                else:
                    st.success(f"Found {len(deadlines)} deadlines!")

                    for d in deadlines:
                        with st.expander(f"📅 {d['date']} — {d['title']}"):
                            st.write(d['description'])

                    ics_lines = ["BEGIN:VCALENDAR", "VERSION:2.0"]
                    for d in deadlines:
                        date = d['date'].replace("-", "")
                        ics_lines += [
                            "BEGIN:VEVENT",
                            f"SUMMARY:{d['title']}",
                            f"DTSTART;VALUE=DATE:{date}",
                            f"DTEND;VALUE=DATE:{date}",
                            f"DESCRIPTION:{d['description']}",
                            "END:VEVENT"
                        ]
                    ics_lines.append("END:VCALENDAR")
                    ics_content = "\n".join(ics_lines)

                    st.download_button(
                        label="Download .ics for Google Calendar",
                        data=ics_content,
                        file_name="deadlines.ics",
                        mime="text/calendar"
                    )