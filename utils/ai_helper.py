import os
import google.generativeai as genai

# Fetch API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Show warning instead of crashing at import time
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ Warning: GEMINI_API_KEY not set. Gemini AI features will not work.")

# Helper to get and reuse the model safely
_model = None

def get_model():
    global _model
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is missing — cannot access Gemini API.")
    if _model is None:
        _model = genai.GenerativeModel('gemini-2.0-flash')
    return _model


def summarize_text(text):
    """
    Summarizes the complaint text into 2-3 lines.
    """
    gemini = get_model()
    prompt = f"Summarize this complaint in 2-3 lines:\n{text}"
    response = gemini.generate_content(prompt)
    return response.text.strip()


def suggest_category(text):
    """
    Suggests a category from predefined options based on complaint text.
    """
    gemini = get_model()
    prompt = (
        f"Suggest a category for this complaint:\n{text}\n"
        "Choose only from these options: Sanitation, Water, Road, Electricity, Public Safety, Other.\n"
        "Return just the category name, nothing else."
    )
    response = gemini.generate_content(prompt)
    return response.text.strip()
