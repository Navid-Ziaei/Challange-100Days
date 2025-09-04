import os
import dotenv
import json
from openai import OpenAI

# Load environment variables from .env file
dotenv.load_dotenv()

# Get the API key and set up the client to connect to Metis AI
metis_api_key = os.getenv("API_KEY")
client = OpenAI(
    api_key=metis_api_key,
    base_url="https://api.metisai.ir/openai/v1"
)


# --- Step 1: Define your custom Python function with a parameter ---
def convert_usd_to_irr(amount: int):
    """
    Converts a given USD amount to IRR by multiplying it by a fixed rate.
    """
    # In a real application, this rate could be fetched from a live API
    fixed_rate = 970000
    total_irr = amount * fixed_rate

    # Return the final calculated amount as a JSON object
    return json.dumps({"total_in_irr": total_irr})


# --- Step 2: Describe the new function and its required parameters to the model ---
functions = [
    {
        "name": "convert_usd_to_irr",
        "description": "یک مبلغ مشخص از دلار آمریکا را به ریال ایران تبدیل می‌کند",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "مبلغ به دلار برای تبدیل شدن",
                }
            },
            "required": ["amount"],  # The 'amount' parameter is mandatory / پارامتر 'amount' اجباری است
        },
    }
]

# --- Step 3: Start the conversation with the user's prompt ---
messages = [
    {"role": "user", "content": "سلام، لطفا ۲۰۰ دلار رو به ریال تبدیل کن"}
]

# --- Step 4: First API call to see if the model wants to use the function ---
print(">>> Calling the model...")
response = client.chat.completions.create(
    model="gpt-4o",  # You can change this to your desired model
    messages=messages,
    functions=functions,
    function_call='auto'
)

response_message = response.choices[0].message

# --- Step 5: Check if the model decided to call our function ---
if response_message.function_call:
    function_name = response_message.function_call.name
    print(f">>> Model decided to call the function '{function_name}'.")

    # --- Step 6: Extract arguments and execute the function ---

    # Parse the JSON string of arguments the model provides
    arguments = json.loads(response_message.function_call.arguments)
    print(f">>> With arguments: {arguments}")

    # Call the function with the extracted arguments
    function_output = convert_usd_to_irr(amount=arguments.get("amount"))
    print(f">>> Function output: {function_output}")

    # Add the assistant's response (the function call) to the message history
    messages.append(response_message)

    # --- Step 7: Send the function's result back to the model ---
    messages.append({
        "role": "function",
        "name": function_name,
        "content": function_output
    })

    print(">>> Calling the model again with function result...")
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    print("\n--- Final Answer ---")
    print(final_response.choices[0].message.content)

else:
    print("\n--- Final Answer ---")
    print(response_message.content)