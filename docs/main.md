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

