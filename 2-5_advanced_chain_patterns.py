from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.prompts import(
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class AdvancedChainBuilder:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-3.5-turbo')
    
    def create_feedback_loop_chain(self, max_iterations: int = 3):
        def refine_response(state):
            iteration = state.get('iteration', 0)
            if iteration >= max_iterations:
                return state['current_response']
            if iteration == 0:
                prompt = ChatPromptTemplate.from_template(
                    'Provide initial response to: {question}'
                )
                response = (prompt | self.llm | StrOutputParser()).invoke(state)
            else:
                prompt = ChatPromptTemplate.from_template(
                    'Improve this response based on crtiteria: {criteria}\n'
                    'Current response: {current_response}\n'
                    'Original question: {question}'
                )
                response = (prompt | self.llm | StrOutputParser()).invoke(state)
            # Evaluate response quality
            eval_prompt = ChatPromptTemplate.from_template(
                'Rate this response quality (1-10) and suggest improvement\n'
                'Question: {question}\nResponse: {response}'
            )
            evaluation = (eval_prompt | self.llm | StrOutputParser()).invoke({
                'question': state['question'],
                'response': response,
            })
            # Check if refinement needed
            if '10' in evaluation or iteration >= max_iterations - 1:
                return response
            else:
                return refine_response({
                    **state,
                    'current_response': response,
                    'criteria': evaluation,
                    'iteration': iteration + 1
                })
        return RunnableLambda(refine_response)

    def create_multi_perspective_chain(self):
        perspectives = {
            'analytical': 'Analyze this from a logical, data-driven perspective: {topic}',
            'creative': 'Explor this topic creatively and imaginatively: {topic}',
            'practical': 'Provide practical, actionable insights on: {topic}',
            'critical': 'Critically examine potential issues with: {topic}',
        }
        # Generate all perspectives in parallel
        perspective_chain = RunnableParallel({
            name: (
                ChatPromptTemplate.from_template(template)
                | self.llm
                | StrOutputParser()
            )
            for name, template in perspectives.items()
        })
        # Synthesize perspectives
        synthesis_prompt = ChatPromptTemplate.from_template(
            """Synthesize these different perspectives into a comprehensive analysis:
            Analytical perspective: {analytical}
            Creative perspective: {creative}
            Practical perspective: {practical}
            Critical perspective: {critical}
            Provide a balanced synthesis that incorporates insights from all perspectives.
            """
        )
        full_chain = (
            perspective_chain
            | synthesis_prompt
            | self.llm
            | StrOutputParser()
        )
        return full_chain

if __name__ == '__main__':
    builder = AdvancedChainBuilder()
    # Feedback loop for iterative improvement
    feedback_chain = builder.create_feedback_loop_chain(max_iterations=2)
    result = feedback_chain.invoke({
        'question': 'How can AI improve healthcare?',
        'iteration': 0,
    })
    # Multi-perspective analysis
    perspective_chain = builder.create_multi_perspective_chain()
    analysis = perspective_chain.invoke({
        'topic': 'remote work in the post-pandemic era',
    })
    print('Feedback Loop Result:', result)
    print('\n\n')
    print('Multi-Perspective Analysis:', analysis)
