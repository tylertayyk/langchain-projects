from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ('system', 'You are a helpful AI assistant. Provide clear, concise answers.'),
    ('human', '{question}')
])
output_parser = StrOutputParser()
# Create chain using pipe operator
chain = prompt | llm | output_parser
# Use the application
def ask_question(question):
    response = chain.invoke({'question', question})
    return response
if __name__ == '__main__':
    while True:
        user_question = input("\nAsk a question (or 'quit' to exit): ")
        if user_question.lower() == 'quit':
            break
        answer = ask_question(user_question)
        print(f'\nAnswer: {answer}')
