# complaints/utils/genai.py

import google.generativeai as genai

genai.configure(api_key="AIzaSyACNX0dTD1sigImYxt-llBxWdu6chty38s")

model = genai.GenerativeModel("gemini-2.0-flash")

def get_tone(complaint_text):
    prompt = f"""Analyze the tone of this complaint and return one of: Angry, Polite, Urgent, Neutral.
Complaint: "{complaint_text}" """
    response = model.generate_content(prompt)
    return response.text.strip()
def tone_to_emoji(tone: str) -> str:
    tone = tone.lower()
    if "angry" in tone or "frustrated" in tone:
        return "😡"
    elif "happy" in tone or "satisfied" in tone:
        return "😊"
    elif "neutral" in tone:
        return "😐"
    elif "sad" in tone:
        return "😢"
    else:
        return "🤔"  # Unknown


def get_priority(complaint_text):
    prompt = f"""Assign a priority score (1–5) based on urgency and tone.
Complaint: "{complaint_text}" """
    response = model.generate_content(prompt)
    return int("".join(filter(str.isdigit, response.text)))

def generate_auto_response(complaint_text):
    tone = get_tone(complaint_text)
    priority = get_priority(complaint_text)
    
    # Generate a more natural, contextual response based on tone and priority
    prompt = f"""
You are a helpful assistant. Based on the following complaint, write a polite acknowledgment message that reflects the urgency and tone of the complaint. 
Avoid repeating the complaint text verbatim. Do not include priority labels or explicit tone descriptions in the message.
Complaint: "{complaint_text}"
Tone: "{tone}"

The response should:
- Be respectful and professional.
- Acknowledge the issue clearly.
- Imply urgency if needed based on tone.
"""


    response = model.generate_content(prompt)
    return response.text.strip()
def is_toxic(content: str) -> bool:
    toxic_keywords = ["idiot", "stupid", "useless", "hate", "corrupt", "fraud", "moron"]
    content = content.lower()
    return any(word in content for word in toxic_keywords)

from sentence_transformers import SentenceTransformer, util 

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def is_duplicate_complaint(new_description, existing_descriptions, threshold=0.75):
    embeddings = embed_model.encode([new_description] + existing_descriptions, convert_to_tensor=True)
    new_embedding = embeddings[0]
    existing_embeddings = embeddings[1:]

    similarities = util.cos_sim(new_embedding, existing_embeddings)
    max_sim = max(similarities[0].tolist())
    return max_sim > threshold, max_sim

