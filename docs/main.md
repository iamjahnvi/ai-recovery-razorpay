role: user (The Task): This represents the actual input or command you want the AI to execute. It triggers the model to perform the specific task using the persona established in the system prompt.

role: system (The Rulebook): This sets the AI's persona, boundaries, and overall behavior. By telling the model "You are a payment recovery assistant," you prime its neural network to adopt a specific professional tone, access relevant domain knowledge, and focus on billing-related problem-solving rather than general chit-chat.

<!-- Flow

Python payment dictionary
          ↓
      send to Groq
          ↓
     gpt model
          ↓
    analyze the payment
          ↓
      print answer
 -->


1. Python creates the payment event
< amount = 2000
failure_reason = bank_declined
previous_attempts = 0
minutes_since_failure = 10 />

2. Python sends the event to the LLM.

3. LLM reasons about the event

4. LLM gives us recommendation

# Question is why only these five taken into consideration?
# Becuase they impact the recovery process as of now

    failure_reason = payment["failure_reason"]
    attempts = payment["previous_attempts"]
    minutes = payment["minutes_since_failure"]
    tier= payment["customer_tier"]
    subscription= payment["subscription"]

uuid - universally unique identifiers(uuids)
-python built in uuid module
-standardized 128 bit numbers that are practically generated to be unique across space and time.

-uuid.uuid4 is a function in python's uuid module that generates a version 4 UUID using random numbers.

-indent=4 : it adds human readable formatting to the saved json file by identing nested elements by 4 spaces .
without , json.dump() saves all the data into a single compact hard-to-read file

-sort_keys = "True" means the key value pair inside json will be stored in a sorted format.

