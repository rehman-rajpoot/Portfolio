import os
import json
import google.generativeai as genai

# Initialize Gemini client. Requires GEMINI_API_KEY environment variable.
def init_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True

_cached_model = None
def get_model_name():
    global _cached_model
    if _cached_model: return _cached_model
    try:
        # Ask Google for the list of available models for this specific API key/region
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                # Prefer flash or 1.5 if available
                if 'flash' in m.name or '1.5' in m.name:
                    _cached_model = m.name.replace('models/', '')
                    return _cached_model
        # Fallback to the first available gemini model
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                _cached_model = m.name.replace('models/', '')
                return _cached_model
    except Exception as e:
        print(f"Model List Error: {e}")
    return 'gemini-1.5-flash'

def triage_contact_message(name, email, subject, message):
    """
    Role 2: Smart Contact Triage using Gemini. Reads incoming messages and categorizes them.
    Returns dict: {'category': 'JOB OPPORTUNITY' | 'SPAM' | 'GENERAL INQUIRY', 'draft': 'Suggested reply...'}
    """
    if not init_gemini():
        return {"category": "UNCLASSIFIED", "draft": "GEMINI_API_KEY missing. Could not generate draft."}
    
    prompt = f"""
    You are an AI assistant for Abdul Rehman, a Computer and Hardware Engineer.
    You received a contact form submission:
    From: {name} ({email})
    Subject: {subject}
    Message: {message}
    
    Task 1: Categorize the message strictly as exactly one of: [JOB OPPORTUNITY], [SPAM], [GENERAL INQUIRY], or [COLLABORATION].
    Task 2: Draft a professional, welcoming reply on behalf of Abdul Rehman responding to the message.

    Respond in valid JSON format ONLY. Do not include markdown formatting or backticks around the json, JUST the valid JSON text:
    {{
        "category": "CATEGORY_HERE",
        "draft": "Draft text here"
    }}
    """
    try:
        # Use gemini-1.5-flash for very fast JSON response
        model = genai.GenerativeModel(get_model_name())
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean potential markdown formatting if model wraps it in ```json
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text.rsplit('\n', 1)[0]
        
        content = json.loads(text.strip())
        return content
    except Exception as e:
        print(f"Gemini Triage Error: {e}")
        return {"category": "UNCLASSIFIED", "draft": "Error generating AI response."}

def chat_with_recruiter(user_message, history=None):
    """
    Role 1: Recruiter Assistant Chatbot. Answers questions about Abdul.
    """
    if not init_gemini():
        return "I am currently offline. Please configure the GEMINI_API_KEY in your .env file to activate me!"
    
    system_instruction = """
    You are the official AI representative for Abdul Rehman's Portfolio. 
    Abdul is an expert Computer Engineer with experience in Embedded Systems (Arduino, ESP32), Python, C++, PCB Design, Web Development (Flask/React), and Data Structures.
    He has worked as an Open Contract Electrician handling 3-phase wiring and motors. He has strong problem-solving skills.
    
    Your goal is to answer questions enthusiastically and professionally on his behalf. Be concise, friendly, and always try to frame Abdul as an excellent candidate or engineer. Limit your responses to 2-3 short sentences.
    """
    
    prompt = f"System Rules:\n{system_instruction}\n\n"
    
    if history:
        for item in history:
            role = item.get("role", "user")
            content = item.get("content", "")
            prompt += f"{role.capitalize()}: {content}\n"
            
    prompt += f"User: {user_message}\nAssistant:"

    try:
        model = genai.GenerativeModel(get_model_name())
        response = model.generate_content(prompt)
        return response.text.replace('Assistant: ', '').strip()
    except Exception as e:
        print(f"Gemini Chat Error: {e}")
        return f"I ran into an error connecting to my deep learning core: {str(e)}"

def chat_with_recruiter_stream(user_message, history=None):
    """
    Role 1: Recruiter Assistant Chatbot (Streaming). Yields chunks of text.
    """
    if not init_gemini():
        yield "I am currently offline. Please configure the GEMINI_API_KEY in your .env file to activate me!"
        return
    
    system_instruction = """
    You are the official AI representative for Abdul Rehman's Portfolio. 
    Abdul is an expert Computer Engineer with experience in Embedded Systems (Arduino, ESP32), Python, C++, PCB Design, Web Development (Flask/React), and Data Structures.
    He has worked as an Open Contract Electrician handling 3-phase wiring and motors. He has strong problem-solving skills.
    
    Your goal is to answer questions enthusiastically and professionally on his behalf. Be concise, friendly, and always try to frame Abdul as an excellent candidate or engineer. Limit your responses to 2-3 short sentences.
    """
    
    prompt = f"System Rules:\n{system_instruction}\n\n"
    
    if history:
        for item in history:
            role = item.get("role", "user")
            content = item.get("content", "")
            prompt += f"{role.capitalize()}: {content}\n"
            
    prompt += f"User: {user_message}\nAssistant:"

    try:
        model = genai.GenerativeModel(get_model_name())
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"Gemini Chat Streaming Error: {e}")
        yield f"I ran into an error connecting to my deep learning core: {str(e)}"

def generate_hardware_code(prompt):
    """
    Role 3: Hardware Code Generator Demonstration.
    """
    if not init_gemini():
        return "Error: GEMINI_API_KEY missing. Cannot generate hardware code."
        
    system_instruction = """
    You are a master firmware and hardware engineer. The user will provide a hardware request or component name (e.g. 'Blink LED ESP32' or 'stepper motor driver').
    You must return a high-quality, minimal C++/Arduino code snippet that fulfills their request.
    Include brief wiring instructions in the comments at the top of the code.
    Only return markdown code blocks, do not include extensive explanations.
    """
    
    full_prompt = f"System Instruction:\n{system_instruction}\n\nUser Request: {prompt}"
    
    try:
        # Use pro for complex code architecture
        model = genai.GenerativeModel(get_model_name())
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Code Gen Error: {e}")
        return "Could not generate code."
