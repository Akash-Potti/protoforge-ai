import os
import asyncio
from google import genai
import httpx
from bs4 import BeautifulSoup

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
    "Given the user's project description, extract a Bill of Materials (BOM). "
    "If there is any ambiguity or missing information, ask an appropriate clarification question. "
    "If everything is clear, respond with 'BOM:' followed by a JSON array of items with fields: part, quantity, description."
)


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
