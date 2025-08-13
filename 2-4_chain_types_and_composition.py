from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.prompts import(
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI

# Sequential chain
def create_sequential_analysis_chain():
    # Step 1: Extract key information
    extraction_prompt = ChatPromptTemplate.from_template(
        'Extract key facts from this text: {text}'
    )
    # Step 2: Analyze sentiment
    sentiment_prompt = ChatPromptTemplate.from_template(
        'Analyze sentiment of these facts: {facts}'
    )
    # Step 3: Generate summary
    summary_prompt = ChatPromptTemplate.from_template(
        'Create executive summary based on facts: {facts} and sentiment: {sentiment}'
    )
    # Chain steps together
    chain = (
        {'text': RunnablePassthrough()}
        | RunnablePassthrough.assign(
            facts=extraction_prompt | ChatOpenAI() | StrOutputParser()
        )
        | RunnablePassthrough.assign(
            sentiment=sentiment_prompt | ChatOpenAI() | StrOutputParser()
        )
        | summary_prompt | ChatOpenAI() | StrOutputParser()
    )
    return chain

# Parallel chain - multiple operations on same input
def create_parallel_analysis_chain():
    return RunnableParallel({
        'summary': (
            ChatPromptTemplate.from_template('Summarize: {text}')
            | ChatOpenAI() | StrOutputParser()
        ),
        'sentiment': (
            ChatPromptTemplate.from_template('Analyze sentiment: {text}')
            | ChatOpenAI() | StrOutputParser()
        ),
        'keywords': (
            ChatPromptTemplate.from_template('Extract keywords: {text}')
            | ChatOpenAI() | StrOutputParser()
        ),
        'category': (
            ChatPromptTemplate.from_template('Categorize this text: {text}')
            | ChatOpenAI() | StrOutputParser()
        )
    })

# Router chain - conditional logic
def create_router_chain():
    def route_by_type(input_dict):
        content_type = input_dict['type'].lower()
        if content_type == 'technical':
            return ChatPromptTemplate.from_template(
                'Provide technical analysis with detailed explanations: {content}'
            )
        elif content_type == 'business':
            return ChatPromptTemplate.from_template(
                'Provide business analysis focusing on impact and strategy: {content}'
            )
        else:
            return ChatPromptTemplate.from_template(
                'Provide general analysis: {content}'
            )
    router_chain = (
        RunnableLambda(route_by_type)
        | ChatOpenAI()
        | StrOutputParser()
    )
    return router_chain
