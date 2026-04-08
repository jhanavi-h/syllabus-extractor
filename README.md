# Syllabus Deadline Extractor

This tool takes a college syllabus, either pasted as plain text or uploaded as a PDF, and uses the Claude API to extract all key deadlines and assignments. Results are displayed in the browser as expandable rows and can be downloaded as a .ics file that imports directly into Google Calendar, Apple Calendar, or Outlook.

## How to run it

1. Clone this repo
2. Install dependencies: pip3 install streamlit anthropic pypdf python-dotenv
3. Create a .env file in the project folder with the following: ANTHROPIC_API_KEY="your-key-here"
4. Run the app: streamlit run app.py
5. Open your browser to the local URL that appears in the terminal