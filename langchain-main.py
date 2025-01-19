import os
import getpass
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
def test_embedding(index):
    test_string = "ion: Tell me about yourself. Answer: Yo, I’m Ty. Born and raised "
    def get_embed_string(test_string: str):
        try:
            # Get embedding vector
            embedding_vector = embeddings.embed_query(test_string)
            return embedding_vector
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return None



    response = index.query(
        namespace="questions",
        vector=get_embed_string(test_string),
        top_k=1,
        include_values=True,
        include_metadata=True,
    )

# Load environment variables
load_dotenv()

# Set OpenAI API key if not present
if not os.environ.get("OPENAI_API_KEY"):
     # throw error
    print("OpenAI API key not found")
    exit(1)
if not os.environ.get("PINECONE_API_KEY"):
    print("Pinecone API key not found")
    exit(1)
# Initialize clients
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Setup vector store
USER_DB = "uofthacks12"
USER_NAMESPACE = "questions"


print([index_info["name"] for index_info in pc.list_indexes()])

index = pc.Index(USER_DB)
vector_store = PineconeVectorStore(
    index=index, 
    embedding=embeddings
)


from langchain_openai import OpenAI
from typing import List, Tuple

def get_reply_from_other_context(vector_store, k: int, text: str) -> str:
    try:
        # Get similar documents
        results = vector_store.similarity_search_with_score(
            text, 
            k=k, 
            namespace=USER_NAMESPACE
        )
        
        # Format context
        context = "\n".join([
            f"[Score: {score:.3f}] {doc.page_content}"
            for doc, score in results
        ])
        
        # Initialize LLM
        llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.5,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Generate response using context
        prompt = f"""Use the following context to answer the question.
        Context: {context}
        
        Question: {text}
        Answer:"""
        
        response = llm.predict(prompt)
        return response
        
    except Exception as e:
        print(f"Error in get_reply_from_other_context: {str(e)}")
        return "Sorry, I encountered an error processing your request."