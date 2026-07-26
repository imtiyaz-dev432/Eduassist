import os
import requests


def generate_admission_reply(user_message, faq_context, has_contact=False):
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "poolside/laguna-xs-2.1")

    if not api_key:
        return "AI service abhi configured nahi hai. Please coaching se directly contact karein."

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

    system_prompt = f"""
You are EduAssist AI, an admission assistant for a coaching institute.

Rules:
1. Answer ONLY admission-related questions.
2. Allowed topics:
   - Courses
   - Fees
   - Batch timings
   - Syllabus
   - Demo class
   - Admission process
   - Contact details
3. Never answer:
   - Quiz answers
   - Assignment answers
   - Attendance
   - Student private data
   - Fee payment status
   - Admin information
4. Reply in simple Hinglish.
5. Keep answers short and helpful.
6. Use FAQ context whenever possible.
7. If exact information exists in FAQ, answer ONLY from FAQ.
8. Never invent:
   - Fees
   - Timings
   - Address
   - Phone number
   - Discounts
   - Course duration
9. If exact information is unavailable, reply:
   "Iski exact detail abhi available nahi hai. Demo class ya admission details ke liye apna naam aur mobile number share kar dijiye."
10. Use ₹ only if fee information exists in FAQ.

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
        "temperature": 0.3,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",   # Deployment ke time apni domain kar dena
        "X-Title": "EduAssist AI"
    }

    try:
     response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=30
    )

     print("Status Code:", response.status_code)

     if response.status_code != 200:
       print("Error Response:", response.text)

     response.raise_for_status()

     result = response.json()
     print("OpenRouter Response:", result)

     if "choices" not in result:
        return f"Invalid Response: {result}"

     message = result["choices"][0]["message"]
     print("Message:", message)

     return message["content"].strip()

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