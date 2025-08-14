# NOTE: This example is not working, but it shows that we can use LangChain to ask
# the agent to output structured data into a Python class
from langchain_core.output_parsers import(
    PydanticOutputParser,
)
from langchain.output_parsers.fix import OutputFixingParser
from langchain.output_parsers.retry import RetryOutputParser
from langchain_core.prompts import(
    ChatPromptTemplate,
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class SentimentType(str, Enum):
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'

class AnalysisResult(BaseModel):
    sentiment: SentimentType = Field(description='Overall sentiment of the text')
    confidence: float = Field(description='Confidence score between 0 and 1', ge=0, le=1)
    key_themes: List[str] = Field(description='Main themes identified in the text')
    summary: str = Field(description='Brief summary of the analysis')
    word_count: Optional[int] = Field(description='Approximate word count')
    @field_validator('key_themes')
    def validate_themes(cls, v):
        print('tyle')
        if len(v) < 1:
            raise ValueError('At least one theme must be identified')
        return v

class StructuredOutputProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
        # Different parser types
        # We are using pydantic_parser
        # self.json_parser = JsonOutputParser()
        self.pydantic_parser = PydanticOutputParser(pydantic_object=AnalysisResult)
        # Robust parsing with error handling
        """
        We are using retry_parser instead
        self.fixing_parser = OutputFixingParser.from_llm(
            parser=self.pydantic_parser,
            llm=self.llm,
        )
        """
        self.retry_parser = RetryOutputParser(
            parser=self.pydantic_parser,
            llm=self.llm,
            max_retries=3,
            retry_chain=RunnablePassthrough(),
        )

    def create_structured_analysis_chain(self, use_robust_parsing: bool = True):
        # Create chain that outputs structured analysis
        prompt = ChatPromptTemplate.from_template(
            """Text: {text}
            {format_instructions}
            Ensure your response is valid JSON that matches the required schema."""
        )
        # Choose parser based on robustness requirement (whether to use retry parser or pydantic parser)
        parser = self.retry_parser if use_robust_parsing else self.pydantic_parser
        chain = (
            prompt.partial(format_instructions=parser.get_format_instructions())
            | self.llm
            | parser
        )
        return chain
    
    # Note: This method is not used. This is just an example of how to create a custom output formatter
    def create_custom_output_formatter(self, output_schema: dict):
        # Create custom formatter for specific output needs
        def format_output(llm_response: str) -> dict:
            try:
                import json
                return json.loads(llm_response)
            except:
                # Fallback to structured extraction
                lines = llm_response.strip().split('\n')
                results = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace('', '_')
                        value = value.strip()
                        # Type conversion based on schema
                        if key in output_schema:
                            expected_type = output_schema[key]
                            if expected_type == float:
                                try:
                                    value = float(value)
                                except:
                                    value = 0.0
                            elif expected_type == int:
                                try:
                                    value = int(value)
                                except:
                                    value = 0
                            elif expected_type == list:
                                value = [v.strip() for v in value.split(',')]
                        results[key] = value
                return results
        return RunnableLambda(format_output)

if __name__ == '__main__':
    processor = StructuredOutputProcessor()
    # Structured analysis with robust parsing
    analysis_chain = processor.create_structured_analysis_chain(use_robust_parsing=True)
    text_to_analyze = """
    The new product launch exceeded expectations with 150% of target sales in the first quarter.
    Customer feedback has been overwhelmingly positive, particularly praising the intuitive user interface
    and robust performance. However, some concerns were arised about pricing competitiveness in the market.
    """
    result = analysis_chain.invoke({'text': text_to_analyze})
    print(f'Sentiment: {result.sentiment}')
    print(f'Confidence: {result.confidence}')
    print(f'Themes: {result.key_themes}')
