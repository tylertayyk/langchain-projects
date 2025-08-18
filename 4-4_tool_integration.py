from langchain.tools import Tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

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

class ToolAgentState(TypedDict):
    user_request: str
    available_tools: List[str]
    selected_tool: str
    tool_inputs: dict
    tool_results: Annotated[List[str], operator.add]
    plan: str
    final_response: str

def analyze_request_for_tools(state: ToolAgentState):
    # Analyze user request to determine which tools might be needed
    request = state['user_request']
    # Simple keyword-based tool selection (in practice, use LLM)
    tool_keywords = {
        'calculate': ['calculate', 'math', 'compute', '+', '-', '*', '/'],
        'weather': ['weather', 'temperature', 'rain', 'sunny', 'cloudy'],
        'web_search': ['search', 'find', 'look up', 'research', 'latest'],
        'file_writer': ['save', 'write', 'file', 'document', 'store'],
    }
    selected_tools = []
    for tool, keywords in tool_keywords.items():
        if any(keyword in request.lower() for keyword in keywords):
            selected_tools.append(tool)
        # Default to web search if no specific tool identified
        if not selected_tools:
            selected_tools = ['web_search']
            plan = f"I will use {','.join(selected_tools)} to help with: {request}"
            return {
                'selected_tool': selected_tools[0], # Start with first tool
                'plan': plan,
            }

def prepare_tool_input(state: ToolAgentState):
    # Prepare the input for the selected tool
    tool = state['selected_tool']
    request = state['user_request']
    # Extract relevant information for each tool type
    if tool == 'calculator':
        # Extract mathematical expression
        # In practice, use LLM to parse the calculation request
        tool_input = request # Simplified
    elif tool == 'weather':
        # Extract location
        # Simple extraction (use NER in practice)
        words = request.split()
        location = 'New York' # default
        for i, word in enumerate(words):
            if word.lower() in ['in', 'for', 'at'] and i + 1 < len(words):
                location = words[i+1]
                break
        tool_input = location
    elif tool == 'web_search':
        tool_input = request
    elif tool == 'file_writer':
        # Parse filename and content
        tool_input = 'output.txt' # Simplified
    else:
        tool_input = request
    return {'tool_inputs': {'input': tool_input}}

def execute_tool(state: ToolAgentState):
    # Execute the selected tool with prepared inputs
    tool_name = state['selected_tool']
    tool_input = state['tool_inputs']['input']
    # Get tool and execute
    if tool_name in tools:
        tool = tools[tool_name]
        result = tool.func(tool_input)
    else:
        result = f'Tool {tool_name} not available'
    return {'tool_results': [f'{tool_name}: {result}']}

def evaluate_tool_result(state: ToolAgentState) -> str:
    # Evaluate if tool result satisfies the user's request
    results = state['tool_results']
    # Simple evaluation (in practice, use LLM to assess quality)
    if results and 'Error' not in results[-1]:
        return 'satisfied'
    else:
        return 'need_more_tools'

def select_next_tool(state: ToolAgentState):
    # Select another tool if needed
    # For simplicity, we'll just end here
    # In practice, agent could try alternative tools
    return {'final_response': 'I apologize, but I encoutnered an issue with the tools.'}

def generate_final_response(state: ToolAgentState):
    # Generate final resposne based on tool results
    request = state['user_request']
    results = state['tool_results']
    response = f"""
    I've completed your request: {request}
    Here's what I found:
    {chr(10).join(results)}
    Is there anything else you'd like me to help you with?
    """
    return {'final_response': response}

# Build tool-using agent
tool_workflow = StateGraph(ToolAgentState)
tool_workflow.add_node('analyze', analyze_request_for_tools)
tool_workflow.add_node('prepare', prepare_tool_input)
tool_workflow.add_node('execute', execute_tool)
tool_workflow.add_node('select_next', select_next_tool)
tool_workflow.add_node('respond', generate_final_response)
tool_workflow.set_entry_point('analyze')
tool_workflow.add_edge('analyze', 'prepare')
tool_workflow.add_edge('prepare', 'execute')

tool_workflow.add_conditional_edges(
    'execute',
    evaluate_tool_result,
    {
        'satisfied': 'respond',
        'need_more_tools': 'select_next',
    }
)
tool_workflow.add_edge('select_next', END)
tool_workflow.add_edge('response', END)
tool_agent = tool_workflow.compile()
