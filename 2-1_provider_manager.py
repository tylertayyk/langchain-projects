from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import asyncio
from dotenv import load_dotenv

load_dotenv()

class ProviderManager:
    def __init__(self):
        self.providers = {
            'openai_fast': ChatOpenAI(
                model='gpt-3.5-turbo',
                temperature=0.1,
                max_tokens=1000,
                request_timeout=30,
                max_retries=3,
            ),
            'openai_quality': ChatOpenAI(
                model='gpt-4',
                temperature=0.2,
                max_tokens=2000,
                request_timeout=60,
            ),
            'anthropic': ChatAnthropic(
                model='claude-3-sonnet-20240229',
                temperature=0.1,
                max_tokens=1500,
            )
        }

    async def parallel_inference(self, prompt: str, providers: list = None):
        # Run inference across multiple providers simultaneously
        if providers is None:
            providers = list(self.providers.keys())
        async def get_response(name, model):
            try:
                response = await model.ainvoke([HumanMessage(content=prompt)])
                return name, response.content, None
            except Exception as e:
                return name, None, str(e)
        # Execute requests in parallel
        tasks = [
            get_response(name, self.providers[name])
            for name in providers
            if name in self.providers
        ]
        results = await asyncio.gather(*tasks)
        return {name: {'response': response, 'error': error} for name, response, error in results}

    def failover_inference(self, prompt: str, provider_order: list = None):
        # Try providers in order until one succeeds
        if provider_order is None:
            provider_order = ['openai_fast', 'anthropic', 'openai_quality']
        for provider_name in provider_order:
            try:
                model = self.providers[provider_name]
                response = model.invoke([HumanMessage(content=prompt)])
                return {
                    'response': response.content,
                    'provider': provider_name,
                    'error': None
                }
            except Exception as e:
                continue
        return {
            'response': None,
            'provider': None,
            'error': 'All providers failed',
        }

async def demo_provider_management():
    manager = ProviderManager()
    # Parallel comparison
    results = await manager.parallel_inference('Explain quantum computing in simple terms')
    for provider, result in results.items():
        print(f'{provider}: {result['response']}')
    # Failover for reliability
    result = manager.failover_inference('What is machine learning?')
    print(f'Response from {result['provider']}: {result['response'] if result['response'] else result['error']}')

if __name__ == '__main__':
    asyncio.run(demo_provider_management())
