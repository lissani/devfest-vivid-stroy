import requests
import os
import sys

# ==========================
# CONFIG
# ==========================
API_URL = "https://api.k2think.ai/v1/chat/completions"
MODEL_NAME = "MBZUAI-IFM/K2-Think-v2"

# Read API key from environment variable
API_KEY = "IFM-I84hTB5NX6a1C9LN"

if not API_KEY:
    print("❌ Error: K2THINK_API_KEY environment variable not set.")
    print("Run this first:")
    print('  export K2THINK_API_KEY="your-api-key-here"')
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# ==========================
# FUNCTION TO CALL THE API
# ==========================
def send_message(message):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": message}
        ],
        "stream": False
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("❌ API Error:", response.status_code)
        print(response.text)
        return None

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("❌ Unexpected response format:")
        print(data)
        return None


# ==========================
# INTERACTIVE TEST LOOP
# ==========================
def main():
    print("🤖 K2 Think AI – Python Test Client")
    print("Type a message and press Enter.")
    print("Press Ctrl+C to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            reply = send_message(user_input)

            if reply:
                print("\nAI:", reply, "\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
