from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

Settings.llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY")
)

Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-base")

def create_query_engine(index: VectorStoreIndex):
    return index.as_query_engine(similarity_top_k=5)


def ask_question(query_engine, question: str) -> str:
    print(f"\n Question : {question}")
    print(" Recherche en cours...")

    prompt = f"""You are a helpful assistant. Answer based on the context.
If the question is in French, answer in French.
If the question is in English, answer in English.
Question: {question}"""

    response = query_engine.query(prompt)
    return str(response)