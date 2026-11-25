import streamlit as st
from pathlib import Path
from src.rag import KnowledgeBase
from src.llm import generate_answer, ollama_status
from src.utils import load_documents, SUPPORTED_LANGUAGES

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "knowledge_base"

st.set_page_config(page_title="KrishiMitra AI", page_icon="🌾", layout="wide")
st.title("🌾 KrishiMitra AI")
st.caption("Multilingual Farmer Advisory Assistant | GenAI + LLM + Retrieval-Augmented Generation")

with st.sidebar:
    st.header("Farmer details")
    language = st.selectbox("Preferred language", list(SUPPORTED_LANGUAGES.keys()), index=0)
    state = st.selectbox("State", ["Karnataka", "Tamil Nadu", "Andhra Pradesh", "Telangana", "Maharashtra", "Other"])
    crop = st.selectbox("Main crop", ["Rice", "Ragi", "Maize", "Cotton", "Tomato", "Chilli", "Sugarcane", "Other"])
    soil = st.selectbox("Soil type (optional)", ["Not sure", "Red soil", "Black soil", "Alluvial soil", "Laterite soil", "Sandy soil", "Clay soil"])
    season = st.selectbox("Growing season", ["Not specified", "Kharif", "Rabi", "Summer"])
    st.divider()
    st.subheader("LLM connection")
    status = ollama_status()
    if status:
        st.success("Ollama is reachable")
    else:
        st.warning("Ollama not detected. Start Ollama to enable LLM answers.")
    st.caption("Default model: llama3.2:3b")
    st.caption("Run `ollama pull llama3.2:3b` in a terminal.")

@st.cache_resource
def get_kb():
    return KnowledgeBase(DATA_DIR)

kb = get_kb()
st.info("Ask about crop care, soil health, irrigation, pest management or agricultural schemes. Answers are generated from retrieved reference material where possible.")

tab_chat, tab_docs, tab_about = st.tabs(["💬 Ask KrishiMitra", "📄 Add reference documents", "ℹ️ About"])

with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Reference material"):
                    for source in msg["sources"]:
                        st.markdown(f"- **{source['title']}** — {source['excerpt']}")

    prompt = st.chat_input("Example: How can I manage yellowing leaves in my rice crop?")
    if prompt:
        context = {
            "language": language, "state": state, "crop": crop,
            "soil": soil, "season": season
        }
        hits = kb.search(prompt, top_k=4)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Finding relevant guidance and preparing an answer..."):
                answer, mode = generate_answer(prompt, context, hits)
                st.markdown(answer)
                st.caption(f"Response mode: {mode}")
                sources = [{"title": h["title"], "excerpt": h["text"][:240] + ("..." if len(h["text"]) > 240 else "")} for h in hits]
                if sources:
                    with st.expander("Reference material"):
                        for source in sources:
                            st.markdown(f"- **{source['title']}** — {source['excerpt']}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

    st.caption("Tip: Include crop stage, symptoms, location and recent weather for more useful guidance.")

with tab_docs:
    st.subheader("Upload agricultural reference material")
    uploaded = st.file_uploader("Upload PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True)
    if st.button("Index uploaded documents", disabled=not uploaded):
        added = 0
        for item in uploaded:
            try:
                chunks = load_documents(item.name, item.getvalue())
                kb.add_chunks(chunks)
                added += len(chunks)
            except Exception as exc:
                st.error(f"Could not process {item.name}: {exc}")
        st.success(f"Added {added} text sections to this session's knowledge base.")
    st.warning("Use trusted sources such as agricultural university publications, KVK material and official government advisories. Uploaded documents are indexed in memory for this session.")

with tab_about:
    st.markdown("""
### What this project demonstrates
- **Large Language Model:** Ollama-hosted Llama 3.2 generates conversational answers.
- **RAG:** TF-IDF retrieval finds relevant passages from the local agricultural knowledge base.
- **Generative AI:** Produces contextual explanations, action checklists and follow-up questions.
- **Multilingual interaction:** The selected language is included in the LLM prompt; ask in your preferred language.
- **Document intelligence:** Upload PDF/TXT reference material and retrieve from it.

### Important limitations
This is an educational prototype, not a substitute for a qualified agronomist or official local advisory. Pest and disease diagnosis from text alone is uncertain. Verify pesticide choices, dosage, waiting periods and scheme eligibility with your local Krishi Vigyan Kendra (KVK), agriculture department or licensed expert. Never mix or apply chemicals based only on an AI answer.
""")
