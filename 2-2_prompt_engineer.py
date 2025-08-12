from langchain_core.prompts import(
    ChatPromptTemplate,
    PromptTemplate,
    FewShotPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class PromptEngineer:
    def __init__(self):
        self.few_shot_examples = {
            'sentiment_analysis': [
                {'input': 'Ilove this product!', 'output': 'Positive'},
                {'input': 'This is terrible quality.', 'output': 'Negative'},
                {'input': "It's okay, nothing special.", 'output': 'Neutral'}
            ],
            'code_explanation': [
                {
                    'input': 'def factorial(n): return 1 if n <= 1 else n * factorial(n-1)',
                    'output': 'This is a recursive function that calculates factorial by multiplying n with factorial of (n-1), with base case returning 1 for n <= 1.',
                }
            ]
        }
    
    def create_few_shot_template(self, task_type: str, example_count: int = 3):
        examples = self.few_shot_examples.get(task_type, [])[:example_count]
        example_template = PromptTemplate.from_template(
            'Input: {input}\nOutput: {output}'
        )
        few_shot_template = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_template,
            prefix='Here are examples of the task:',
            suffix='Now complete this task:\nInput: {input}\nOutput:',
            input_variables=['input'],
        )
        return few_shot_template
    
    def create_chain_of_thought_template(self, domain: str):
        return ChatPromptTemplate.from_messages([
            ('system', f"""
                You are an expert in {domain}. When solving problems:
                1. Break down the problem into steps
                2. Show your reasoning for each step
                3. Provide the final answer clearly
                Always think step b y step and explain your reasoning.
            """),
            ('human', '{problem}'),
        ])
    
    def create_role_based_template(self, role: str, task_description: str):
        return ChatPromptTemplate.from_messages([
            ('system', f"""
                You are a {role}. Your expertise includes:
                - Deep knowledge in your field
                - Professional communication style
                - Practical, actionable advice
                Task: {task_description}
            """),
            ('human', '{input}'),
            ('human', 'Please provide a comprehensive response based on your expertise.'),
        ])

if __name__ == '__main__':
    # Usage examples
    engineer= PromptEngineer()
    # Few-shot learning for sentiment analysis
    sentiment_template = engineer.create_few_shot_template('sentiment_analysis')
    sentiment_prompt = sentiment_template.format(input='This movie was amazing!')
    # Chain of thought for problem solving
    cot_template = engineer.create_chain_of_thought_template('mathematics')
    math_prompt = cot_template.format(problem='Solve: 2x + 5 = 15')
    # Role-based prompting
    doctor_template = engineer.create_role_based_template(
        'medical doctor',
        'Provide health advice based on symptoms',
    )
    doctor_prompt = doctor_template.format(input='I have a headache and fever.')
    print('sentiment_prompt', sentiment_prompt)
    print('math_prompt', math_prompt)
    print('doctor_prompt', doctor_prompt)
