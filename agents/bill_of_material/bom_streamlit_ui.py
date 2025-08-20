import streamlit as st
import json

# Load sourced parts from JSON file


def load_sourced_parts(json_path="sourced_parts.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading sourced parts: {e}")
        return []


st.title("BOM Parts Purchase Selector")

sourced_parts = load_sourced_parts()

if not sourced_parts:
    st.warning("No sourced parts found. Please run the BOM sourcing agent first.")
else:
    selected_parts = []
    for part in sourced_parts:
        st.subheader(f"{part['part']} (Qty: {part['quantity']})")
        options = part["options"]
        if options:
            option_labels = [
                f"{opt['name']} | ₹{opt['price']} | [Link]({opt['link']})" for opt in options]
            selected = st.radio(
                f"Select option for {part['part']}",
                option_labels,
                key=part['part']
            )
            # Find the selected option
            selected_idx = option_labels.index(selected)
            selected_parts.append({
                "part": part["part"],
                "quantity": part["quantity"],
                "selected_option": options[selected_idx]
            })
        else:
            st.info("No options available for this part.")

    if st.button("Confirm Purchase Selection"):
        st.success("You have selected the following parts to purchase:")
        total_cost = 0
        for item in selected_parts:
            opt = item["selected_option"]
            qty = int(item["quantity"])
            price = float(opt["price"])
            st.write(
                f"{item['part']} (Qty: {qty}) - {opt['name']} | ₹{price} | [Link]({opt['link']})")
            total_cost += price * qty
        st.markdown(f"**Total Cost: ₹{total_cost:.2f}**")
        # Optionally, save the user's selection to a file
        with open("selected_parts.json", "w", encoding="utf-8") as f:
            json.dump(selected_parts, f, indent=2, ensure_ascii=False)
        st.info("Selection saved to selected_parts.json")
