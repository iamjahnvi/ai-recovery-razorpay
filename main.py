from dotenv import load_dotenv
import os
load_dotenv()
# python, go inside .env and load the secrets.

from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)


payment = {
    "amount" : 2000 ,
    "failure_reason" : "bank_declined" ,
    "previous_attempts" : 0 ,
    "minutes_since_failure" : 10
}

response = client.chat.completions.create(
    model="" , 
    messages=[
        {"role":"system" , "content":"You are a payement recovery assistant."},
        {"role":"user" , "content":"Analyse this failed payment"}
    ]
)

print(response.choices[0].message.content);

