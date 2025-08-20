import os
import asyncio
from google import genai
import httpx
from bs4 import BeautifulSoup
import json

# Initialize Gemini client (Google AI Studio key)
client = genai.Client(api_key="")

# --- Gemini helper ---------------------------------------------------------- #


async def call_gemini(conversation, retries=3, delay=2):
    prompt_text = ""
    for m in conversation:
        prompt_text += f"{m['role'].upper()}: {m['content']}\n"

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text
            )
            return response.text.strip()
        except Exception as e:
            # retry only for 503 or server errors
            if "503" in str(e) and attempt < retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
            else:
                raise e


async def fetch_part_options(part_name: str, client: httpx.AsyncClient):
    """
    Query the findparts search API and return the 3 cheapest options.
    Returns a list of tuples: (title, price, url)
    """
    # URL encode the part name
    query = part_name.replace(' ', '%20')
    url = f"https://search.findparts.in/search?q={query}&filters=%7B%22vendors%22%3A%5B%5D%7D"

    r = await client.get(url)
    data = r.json()

    # Extract list of hits
    hits = data.get("hits", [])

    # Extract name, price and url for each hit
    results = []
    for hit in hits:
        src = hit.get("_source", {})
        title = src.get("title")
        price = src.get("price")
        link = src.get("url")
        # Only use entries that have both a price and link
        if title and price and link:
            results.append((title, price, link))

    # Sort by price (ascending)
    results.sort(key=lambda x: x[1])

    # Return the 3 cheapest
    return results[:3]


PROMPT_INSTRUCTION = (
    "You are a hardware engineering assistant. "
    "Given the user's project description, extract a Bill of Materials (BOM) consisting of electronic components and hardware parts. "
    "Infer the necessary parts based on the project's objective, budget, microcontroller, skill level, and any additional information provided. "
    "If there is any ambiguity or missing information, ask an appropriate clarification question. "
    "If everything is clear, respond with 'BOM:' followed by a JSON array of items with fields: part, quantity, description.\n\n"
    "Example:\n"
    "Project Description: Objective: Build a smart home lighting system. Budget: $100. Microcontroller: ESP32. Skill Level: Intermediate. Additional Info: Needs to be controllable via a mobile app.\n"
    "BOM: [\n"
    "  {\"part\": \"ESP32 Development Board\", \"quantity\": 1, \"description\": \"Main microcontroller for the system\"},\n"
    "  {\"part\": \"LED Strip (WS2812B)\", \"quantity\": 5, \"description\": \"Addressable RGB LED strip for lighting\"},\n"
    "  {\"part\": \"5V Power Supply\", \"quantity\": 1, \"description\": \"Power supply for ESP32 and LED strip\"},\n"
    "  {\"part\": \"Breadboard\", \"quantity\": 1, \"description\": \"For prototyping and connections\"},\n"
    "  {\"part\": \"Jumper Wires\", \"quantity\": 1, \"description\": \"For connecting components\"}\n"
    "]"
)

async def generate_bom_and_source_parts(project_description):
    conversation = [
        {"role": "user", "content": PROMPT_INSTRUCTION},
        {"role": "user", "content": project_description}
    ]
    async with httpx.AsyncClient() as http_client:
        response_text = await call_gemini(conversation)
        print(f"[DEBUG] Gemini response_text: {response_text}")
        if not response_text.startswith("BOM:"):
            return None, "Clarification needed: " + response_text
        bom_json = response_text[len("BOM:"):].strip()
        try:
            bom = json.loads(bom_json)
            print(f"[DEBUG] Parsed BOM: {bom}")
        except Exception as e:
            print(f"[ERROR] Could not parse BOM JSON: {e}")
            return None, "Could not parse BOM JSON."
        sourced_parts = []
        for item in bom:
            part_name = item["part"]
            options = await fetch_part_options(part_name, http_client)
            print(f"[DEBUG] Options for {part_name}: {options}")
            option_list = [
                {"name": name, "price": price, "link": link}
                for name, price, link in options
            ]
            sourced_parts.append({
                "part": part_name,
                "quantity": item["quantity"],
                "options": option_list
            })
        # Save to file
        with open("sourced_parts.json", "w", encoding="utf-8") as f:
            json.dump(sourced_parts, f, indent=2, ensure_ascii=False)
        return sourced_parts, None


async def main():
    conversation = [{"role": "user", "content": PROMPT_INSTRUCTION}]
    print("Hardware Sourcing Agent (type 'exit' to quit)\n")

    async with httpx.AsyncClient() as http_client:
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break

            # Add user's input to conversation
            conversation.append({"role": "user", "content": user_input})

            # Call Gemini
            response_text = await call_gemini(conversation)
            conversation.append({"role": "model", "content": response_text})

            # If response starts with 'BOM:' → we have the parts list
            if response_text.startswith("BOM:"):
                # Parse JSON BOM
                import json
                bom_json = response_text[len("BOM:"):].strip()
                try:
                    bom = json.loads(bom_json)
                except Exception:
                    print("❗ Could not parse BOM JSON.")
                    print(response_text)
                    return

                # Fetch cheapest options for each part
                print("\nSourcing parts from findpart.in ...\n")
                sourced_parts = []
                for item in bom:
                    part_name = item["part"]
                    options = await fetch_part_options(part_name, http_client)
                    print(f"{part_name} (qty {item['quantity']})")
                    option_list = []
                    for idx, (name, price, link) in enumerate(options, start=1):
                        print(f"  {idx}. {name} — ₹{price}  →  {link}")
                        option_list.append(
                            {"name": name, "price": price, "link": link})
                    sourced_parts.append({
                        "part": part_name,
                        "quantity": item["quantity"],
                        "options": option_list
                    })
                    print()
                # Store sourced parts in JSON file
                import json
                with open("sourced_parts.json", "w", encoding="utf-8") as f:
                    json.dump(sourced_parts, f, indent=2, ensure_ascii=False)
                print("Sourced parts saved to sourced_parts.json\n")
                break

            else:
                # Otherwise this is a clarifying question
                print(f"Gemini: {response_text}")

if __name__ == "__main__":
    asyncio.run(main())
