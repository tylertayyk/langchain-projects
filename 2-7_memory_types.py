from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory,
    VectorStoreRetrieverMemory,
)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from typing import List
from dotenv import load_dotenv

load_dotenv()

class MemoryManager:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-3.5-turbo')
        self.embeddings = OpenAIEmbeddings()
        # Initialize different memory types
        self.memory_types = {
            'buffer': ConversationBufferMemory(return_messages=True),
            'window': ConversationBufferWindowMemory(k=5, return_messages=True),
            'summary': ConversationSummaryMemory(llm=self.llm, return_messages=True),
            'summary_buffer': ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=1000,
                return_messages=True
            )
        }
    
    def create_vector_memory(self, retriever_kwargs: dict=None):
        if retriever_kwargs is None:
            retriever_kwargs = {'k': 5}
        # Create vector store for memory
        vectorstore = FAISS.from_texts(
            [''], # Start with empty store
            embedding=self.embeddings,
        )
        retriever = vectorstore.as_retriever(**retriever_kwargs)
        vector_memory = VectorStoreRetrieverMemory(
            retriever=retriever,
            memory_key='chat_history',
            input_key='input',
        )
        return vector_memory

    def compare_memory_performance(self, conversation_history: List[tuple]):
        # Compare different memory types with sample conversation
        results = {}
        for name, memory in self.memory_types.items():
            # Reset memory
            memory.clear()
            # Add conversation history
            for human_msg, ai_msg in conversation_history:
                memory.chat_memory.add_user_message(human_msg)
                memory.chat_memory.add_ai_message(ai_msg)
            # Get memory content
            memory_content = memory.load_memory_variables({})
            results[name] = {
                'content': str(memory_content),
                'message_count': len(memory.chat_memory.messages),
                'memory_size': len(str(memory_content))
            }
        return results

if __name__ == "__main__":
    sample_conversation = [
        ("Hi, I'm working on a Python project", "Hello! I'd be happy to help with your Python project. What specific aspect are you working on?"),
        ("I need to build a web scraper", "Great! For web scraping in Python, you have several options like BeautifulSoup, Scrapy, or Selenium. What type of website are you scraping?"),
        ("It's an e-commerce site with dynamic content", "For dynamic content, I'd recommend using Selenium with a headless browser. This will handle JavaScript-rendered content effectively."),
        ("How do I handle rate limiting?", "For rate limitng, implement delays between requests, use rotating proxies, and respect robots.txt. You can also add exponential backoff for failed requests."),
    ]
    # Test memory performance
    manager = MemoryManager()
    memory_comparison = manager.compare_memory_performance(sample_conversation)
    for memory_type, stats in memory_comparison.items():
        print(f'{memory_type}: {stats['message_count']} messages, {stats['memory_size']} chars')
