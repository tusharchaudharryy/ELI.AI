import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime
from json import load, dump

load_dotenv()


Username = os.getenv("USERNAME")
AssistantName = os.getenv("ASSISTANT_NAME")
GeminiAPIKey = os.getenv("GEMINI_API_KEY") 

if not all([Username, AssistantName, GeminiAPIKey]):
    raise ValueError("Missing one or more required environment variables: USERNAME, ASSISTANT_NAME, GEMINI_API_KEY")


genai.configure(api_key=GeminiAPIKey)
model = genai.GenerativeModel('gemini-1.5-flash')  

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
SystemChatBot = [{"role": "system", "content": System}]

os.makedirs("Data", exist_ok=True)

if not os.path.exists("Data/ChatLog.json"):
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join([line for line in lines if line.strip()])

def ChatBot(Query):
    try:
        with open("Data/ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        context = System + "\n\n" + RealtimeInformation()
        full_prompt = context + "\n\nUser: " + Query

        response = model.generate_content(full_prompt)
        Answer = response.text

        messages.append({"role": "assistant", "content": Answer})

        with open("Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open("Data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ").strip()
        if user_input:
            print(ChatBot(user_input))
