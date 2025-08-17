from langchain.tools import Tool
from typing import Optional
import requests
import json

def web_search_tool(query: str) -> str:
    # Search the web for information
    return f"Search results for '{query}': [Simulated search results]"

def calculator_tool(expression: str) -> str:
    # Perform mathematical calculations
    try:
        # Safe evaluation for basic math
        result = eval(expression.replace('^', '**'))
        return f'Result: {result}'
    except Exception as e:
        return f'Error in calculation: {str(e)}'

def weather_tool(location: str) -> str:
    # Get weather information for a location
    # Simulate weather API call
    return f'Weather in {location}: Sunny, 72F'

def file_writer_tool(filename: str, content: str) -> str:
    # Write content to a file
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f'Successfully wrote to {filename}'
    except Exception as e:
        return f'Error writing file: {str(e)}'
    
# Register tools
tools = {
    'web_search': Tool(
        name='web_search',
        description='Search the web for current information on any topic',
        func=web_search_tool,
    ),
    'calculator': Tool(
        name='calculator',
        descriptio='Perform mathematical calculations',
        func=calculator_tool,
    ),
    'weather': Tool(
        name='weather',
        description='Get current weather for any location',
        func=weather_tool,
    ),
    'file_writer': Tool(
        name='file_writer',
        description='Write text content to a file',
        func=file_writer_tool,
    )
}
