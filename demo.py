from genagents.genagents import GenerativeAgent

# Load the sample agent
agent_folder = "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"
agent = GenerativeAgent(agent_folder)

print(f"Agent Name: {agent.get_fullname()}")

# Test categorical response
questions = {
    "Do you enjoy outdoor activities?": ["Yes", "No", "Sometimes"]
}
response = agent.categorical_resp(questions)
print(f"\nCategorical Response:")
print(f"Q: Do you enjoy outdoor activities?")
if isinstance(response, dict) and 'responses' in response:
    print(f"A: {response['responses'][0]}")
else:
    print(f"A: {response}")

# Test numerical response
questions = {
    "On a scale of 1 to 10, how much do you enjoy coding?": [1, 10]
}
response = agent.numerical_resp(questions, float_resp=False)
print(f"\nNumerical Response:")
print(f"Q: On a scale of 1 to 10, how much do you enjoy coding?")
if isinstance(response, dict) and 'responses' in response:
    print(f"A: {response['responses'][0]}")
else:
    print(f"A: {response}")

# Test open-ended question
dialogue = [
    ("Interviewer", "Tell me about your favorite hobby."),
]
response = agent.utterance(dialogue)
print(f"\nOpen-ended Response:")
print(f"Q: Tell me about your favorite hobby.")
print(f"A: {response}")