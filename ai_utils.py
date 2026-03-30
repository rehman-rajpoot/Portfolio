import os
from openai import OpenAI
import json

# Initialize OpenAI client. Requires OPENAI_API_KEY environment variable.
def get_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def triage_contact_message(name, email, subject, message):
    """
    Role 2: Smart Contact Triage. Reads incoming messages and categorizes them.
    Returns dict: {'category': 'JOB OPPORTUNITY' | 'SPAM' | 'GENERAL INQUIRY', 'draft': 'Suggested reply...'}
    """
    client = get_client()
    if not client:
        return {"category": "UNCLASSIFIED", "draft": "OpenAI API key missing. Could not generate draft."}
    
    prompt = f"""
    You are an AI assistant for Abdul Rehman, a Computer and Hardware Engineer.
    You received a contact form submission:
    From: {name} ({email})
    Subject: {subject}
    Message: {message}
    
    Task 1: Categorize the message strictly as exactly one of: [JOB OPPORTUNITY], [SPAM], [GENERAL INQUIRY], or [COLLABORATION].
    Task 2: Draft a professional, welcoming reply on behalf of Abdul Rehman responding to the message.

    Respond in valid JSON format ONLY:
    {{
        "category": "CATEGORY_HERE",
        "draft": "Draft text here"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        content = json.loads(response.choices[0].message.content)
        return content
    except Exception as e:
        print(f"OpenAI Triage Error: {e}")
        return {"category": "UNCLASSIFIED", "draft": "Error generating AI response."}

def chat_with_recruiter(user_message, history=None):
    """
    Role 1: Recruiter Assistant Chatbot. Answers questions about Abdul.
    """
    client = get_client()
    if not client:
        return "I am currently offline. Please configure the OPENAI_API_KEY to activate me!"
    
    system_prompt = """
    You are the official AI representative for Abdul Rehman's Portfolio. 
    Abdul is an expert Computer Engineer with experience in Embedded Systems (Arduino, ESP32), Python, C++, PCB Design, Web Development (Flask/React), and Data Structures.
    He has worked as an Open Contract Electrician handling 3-phase wiring and motors. He has strong problem-solving skills.
    
    Your goal is to answer questions enthusiastically and professionally on his behalf. Be concise, friendly, and always try to frame Abdul as an excellent candidate or engineer. Limit your responses to 2-3 short sentences.
    """
    
    if history is None:
        history = []
        
    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Chat Error: {e}")
        return "I ran into an error connecting to my deep learning core."

def generate_hardware_code(prompt):
    """
    Role 3: Hardware Code Generator Demonstration.
    """
    client = get_client()
    if not client:
        return "Error: OpenAI API Key missing. Cannot generate hardware code."
        
    system_prompt = """
    You are a master firmware and hardware engineer. The user will provide a hardware request or component name (e.g. 'Blink LED ESP32' or 'stepper motor driver').
    You must return a high-quality, minimal C++/Arduino code snippet that fulfills their request.
    Include brief wiring instructions in the comments at the top of the code.
    Only return markdown code blocks, do not include extensive explanations.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Code Gen Error: {e}")
        return "Could not generate code."
