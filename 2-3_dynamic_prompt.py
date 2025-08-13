from langchain_core.prompts import(
    PromptTemplate,
)

class DynamicPromptBuilder:
    def __init__(self):
        self.base_templates = {
            'analysis': 'Anlyze the following {content_type}: {content}',
            'summary': 'Summarize the following {content_type} in {length}: {content}',
            'comparison': 'Compare {item1} and {item2} in terms of {criteria}',
            'explanation': 'Explain {concept} for someone with {background} background',
        }
        self.modifiers = {
            'professional': 'Use professional, formal language.',
            'casual': 'Use conversational, friendly language.',
            'technical': 'Include technical details and terminology.',
            'simple': 'Use simple language that anyone can understand.',
            'detailed': 'Provide comprehensive, detailed information.',
            'brief': 'Keep the response concise and to the point.',
        }
    
    def build_prompt(self, task_type: str, content_vars: dict, style_modifiers: list = None, custom_instructions: str = None):
        if task_type not in self.base_templates:
            raise ValueError(f'Unknown task type: {task_type}')
        base_prompt = self.base_templates[task_type]
        style_instructions = ''
        if style_modifiers:
            style_parts = [self.modifiers.get(mod, mod) for mod in style_modifiers]
            style_instructions = ' '.join(style_parts)
        full_template_parts = [base_prompt]
        if style_instructions:
            full_template_parts.append(f'Style requirements: {style_instructions}')
        if custom_instructions:
            full_template_parts.append(f'Additional instructions: {custom_instructions}')
        full_template = '\n\n'.join(full_template_parts)
        # Create template and format
        template = PromptTemplate.from_template(full_template)
        return template.format(**content_vars)
    
if __name__ == '__main__':
    builder = DynamicPromptBuilder()
    prompt = builder.build_prompt(
        task_type='analysis',
        content_vars={
            'content_type': 'quarterly financial report',
            'content': 'Revenue increased by 15% to $2.1M...',
        },
        style_modifiers=['professional', 'detailed'],
        custom_instructions='Focus on growth trends and potential risks.',
    )
    print('prompt:', prompt)
