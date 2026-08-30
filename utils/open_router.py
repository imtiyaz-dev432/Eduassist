import os
import requests
import re 


def generate_admission_reply(user_message, faq_context, has_contact=False):
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "poolside/laguna-xs-2.1")

    if not api_key:
        return "AI service abhi configured nahi hai. Please coaching se directly contact karein."

    # 🔥 CHANGE 1: Agar FAQ khali hai toh AI ko strictly warn karo
    if not faq_context or not faq_context.strip():
        faq_context = "EMPTY. YOU DO NOT KNOW ANY COURSES, FEES, OR TIMINGS. DO NOT GUESS."

    if not has_contact:
        contact_instruction = """
If visitor has NOT shared name and phone number, always end the answer with:
"Demo class ya admission details ke liye apna naam aur mobile number share kar dijiye."
"""
    else:
        contact_instruction = """
Visitor has already shared name and phone number.
Do NOT ask again.

Always end with:
"Hamari team aapse jaldi contact karegi."
"""

    # 🔥 CHANGE 2: Prompt ko chhota aur extremely strict kar diya hai
    system_prompt = f"""
You are EduAssist AI, an admission assistant for a coaching institute.

CRITICAL RULES (FOLLOW STRICTLY):
1. You ONLY know the information provided in the 'Institute FAQ Context' below.
2. If a user asks about Courses, Fees, Timings, or Location, and it is NOT in the FAQ Context, YOU MUST NOT INVENT OR GUESS ANYTHING. NO EXCEPTIONS.
3. If the FAQ Context says 'EMPTY', you know ZERO information about the institute.
4. If you don't know the answer from the FAQ, reply EXACTLY with:
   "Iski exact detail abhi available nahi hai."
5. Reply in simple Hinglish.

Lead Capture Rule:
{contact_instruction}

Institute FAQ Context:
{faq_context}
"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.0,  # 🔥 CHANGE 3: Set to 0.0 (Zero Creativity = Zero Hallucination)
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "EduAssist AI"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print("Error Response:", response.text)

        response.raise_for_status()

        result = response.json()
        print("OpenRouter Response:", result)

        if "choices" not in result:
            return f"Invalid Response: {result}"

        message = result["choices"][0]["message"]["content"]
        clean_message=re.sub(r'<think>.*?</think>','',message,flags=re.DOTALL).strip() #sub=substitute . means koi bhi character and * means unlimited ti mes and ? means stop if reacher </think>
        print("Message:", message)
        if '</think>' in clean_message:
            clean_message=clean_message.split('</think>')[-1]

        return  clean_message

    except requests.exceptions.Timeout:
        print("OpenRouter Timeout")
        return "AI service response dene mein thoda time le rahi hai. Please dobara try karein."

    except requests.exceptions.HTTPError:
        print("HTTP Error:", response.text)
        return "AI service temporary unavailable hai. Please kuch der baad try karein."

    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return "Network issue ki wajah se AI response nahi mil paaya."

    except Exception as e:
        print("Unexpected Error:", e)
        return "Sorry, abhi AI response generate nahi ho pa raha."