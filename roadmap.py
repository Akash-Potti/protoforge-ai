import streamlit as st

def load_css(file_name):
    """Loads a CSS file and injects it into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_name}. Please check the file path.")

def create_card(title, description, content_html, badge_text=None, footer_note=None):
    card_html = f"""
    <div class="shadcn-card">
        <div class="card-header">
            <h3 class="card-title">{title}</h3>
            <p class="card-description">{description}</p>
        </div>
        <div class="card-content">
            {content_html}
        </div>
        <div class="card-footer">
            {'<span class="badge">' + badge_text + '</span>' if badge_text else ''}
            {'<span style="color: #64748b; font-size: 12px;">' + footer_note + '</span>' if footer_note else ''}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def parts_content(parts_data):
    part_icons = {
        "Arduino Uno": "🔧",
        "LED": "💡",
        "Resistor (220Ω)": "⚡"
    }
    if not parts_data:
        return "<em>No parts data loaded.</em>"
    html = '<ul class="parts-list">'
    for part in parts_data:
        icon = part_icons.get(part.get("name", ""), "🔹")
        doc_link = part.get("doc", "#")
        name = part.get("name", "Unknown Part")
        html += f'<li><div style="display: flex; align-items: center;"><span class="part-icon">{icon}</span><span class="part-name">{name}</span></div><a href="{doc_link}" class="doc-link" target="_blank">📚 Docs</a></li>'
    html += '</ul>'
    return html

def steps_content(steps_data):
    if not steps_data:
        return "<em>No steps data loaded.</em>"
    html = '<ul class="steps-list">'
    for i, step in enumerate(steps_data, 1):
        html += f'<li><div class="step-number">{i}</div><div class="step-content">{step}</div></li>'
    html += '</ul>'
    return html

def roadmap_page(parts_data=None, steps_data=None):
    st.set_page_config(page_title="Project Roadmap", page_icon="🗺️", layout="centered")
    load_css("style.css")
    load_css("shadcn_cards.css")

    st.title("🗺️ Project Roadmap")
    st.markdown("Visual overview of your hardware project journey.")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            create_card(
                title="🧰 Required Parts",
                description="Components needed for this project",
                content_html=parts_content(parts_data),
                badge_text=f"{len(parts_data) if parts_data else 0} parts",
                footer_note="Click on docs links for detailed specifications"
            )
        with col2:
            create_card(
                title="📋 Assembly Steps",
                description="Follow these steps to complete your project",
                content_html=steps_content(steps_data),
                badge_text=f"{len(steps_data) if steps_data else 0} steps",
                footer_note="Complete each step in order for best results"
            )

if __name__ == "__main__":
    roadmap_page()

