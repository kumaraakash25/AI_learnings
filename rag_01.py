import os
import requests
import tempfile
import getpass
import logging
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLLECTION = "prompt_store"
EMBEDDING_MODEL = "text-embedding-3-large"

def get_openai_key():
    """Ensure OpenAI API key is set."""
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


def download_webpage(url: str) -> str:
    """Download webpage HTML and save to a temporary file."""
    logger.info("Downloading HTML content...")
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write(response.text)
        logger.info(f"Saved HTML to temporary file: {tmp_file.name}")
        return tmp_file.name


def load_and_split_document(file_path: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[Document]:
    """Load document using UnstructuredHTMLLoader and split it into chunks."""
    logger.info("Loading document...")
    loader = UnstructuredHTMLLoader(file_path)
    documents = loader.load()

    logger.info("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(documents)

    logger.info(f"Split into {len(split_docs)} chunks.")
    return split_docs


def create_vector_store(docs: list[Document], embedder) -> QdrantVectorStore:
    """Create and populate Qdrant vector store."""
    logger.info("Creating vector store and adding documents...")
    vector_store = QdrantVectorStore.from_documents(
        documents=docs,
        url="http://localhost:6333",
        collection_name=COLLECTION,
        embedding=embedder
    )
    logger.info("Documents successfully embedded and stored.")
    return vector_store


def perform_similarity_search(embedder, query: str):
    """Perform a similarity search using Qdrant."""
    logger.info("Loading existing vector store for retrieval...")
    retriever = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name=COLLECTION,
        embedding=embedder
    )

    logger.info(f"Performing similarity search for: {query}")
    results = retriever.similarity_search(query=query)
    for i, res in enumerate(results):
        logger.info(f"\n--- Result {i+1} ---\n{res.page_content}\n")
    return results


def main():
    try:
        get_openai_key()
        url = "https://medium.com/@aakashthesid/gen-ai-and-the-power-of-prompts-244941c19b33"
        file_path = download_webpage(url)

        split_docs = load_and_split_document(file_path)

        embedder = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Ingest into vector store
        create_vector_store(split_docs, embedder)

        # Search
        perform_similarity_search(embedder, query="What is zero shot prompt")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
