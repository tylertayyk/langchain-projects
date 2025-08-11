from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

class IntelligentQA:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
        self.memory = ConversationBufferWindowMemory(k=5, return_messages=True)
        self.prompt = ChatPromptTemplate.from_messages([
            ('system', """
                You are a helpful AI assistant. Use the conversation history to provide contextual responses.
                If you don't know omething, say so clearly.
            """),
            ('placeholder', '{chat_history}'),
            ('human', '{question}')
        ])
        self.chain = (
            RunnablePassthrough.assign(chat_history=lambda x: self.memory.chat_memory.messages)
            | self.prompt
            | self.llm
        )
    
    def ask(self, question):
        response = self.chain.invoke({'question': question})
        # Save to memory
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(response.content)
        return response.content

    def clear_history(self):
        self.memory.clear()
    
if __name__ == '__main__':
    qa_app = IntelligentQA()
    print('Intelligent Q&A Assistant')
    print("Type 'clear' to reset conversation, 'quit' to exit\n")
    while True:
        question = input('You: ')
        if question.lower() == 'quit':
            break
        elif question.lower() == 'clear':
            qa_app.clear_history()
            print('Conversation history cleared\n')
            continue
        answer = qa_app.ask(question)
        print(f'Assistant: {answer}]\n')
