import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def ollama_status():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return response.ok
    except requests.RequestException:
        return False

def generate_answer(question, profile, retrieved):
    language = profile.get("language", "English")
    context_text = "\n\n".join(
        f"[{i+1}] {item['title']}: {item['text']}" for i, item in enumerate(retrieved)
    )
    if not context_text:
        context_text = "No matching local reference passage was found. Clearly say that the answer is general guidance and ask the farmer to consult a local agricultural expert."
    prompt = f"""You are KrishiMitra, a cautious agricultural information assistant.
Answer in {language}. Use simple, practical language suitable for farmers.
Farmer context: state={profile.get('state')}; crop={profile.get('crop')}; soil={profile.get('soil')}; season={profile.get('season')}.
Question: {question}
Retrieved reference passages:
{context_text}

Instructions:
1. Prioritize the retrieved passages. Do not invent facts, scheme eligibility, pesticide names, dosages or chemical mixtures.
2. If the sources do not support a specific answer, say what is unknown and recommend contacting the local KVK/agriculture officer.
3. Give a short explanation, safe next steps, and what extra details would improve the advice.
4. For suspected pest/disease symptoms, explain that text-only diagnosis is uncertain.
5. Do not claim to have checked live weather, market prices or current scheme status.
"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if answer:
            return answer, f"Local LLM ({MODEL}) + RAG"
    except requests.RequestException:
        pass
    # Transparent fallback: keeps the app demonstrable without pretending to be an LLM.
    if retrieved:
        bullets = "\n".join(f"- {x['text']}" for x in retrieved[:3])
        answer = (
            f"**Reference-based information (LLM is currently unavailable):**\n\n{bullets}\n\n"
            "These passages are retrieved from the project's sample knowledge base. "
            "This fallback does not generate a personalized diagnosis. Please share crop stage, "
            "symptoms and location, and verify any treatment with your local KVK."
        )
    else:
        answer = (
            "I could not connect to the local LLM and found no matching reference passage. "
            "Start Ollama and download the configured model, or add trusted agricultural PDF/TXT references. "
            "For crop-specific treatment, consult your local KVK or agriculture officer."
        )
    return answer, "Reference retrieval fallback (LLM not connected)"
