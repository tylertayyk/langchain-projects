from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class ResearchState(TypedDict):
    research_topic: str
    source_checked: Annotated[List[str], operator.add]
    findings: Annotated[List[str], operator.add]
    current_focus: str
    research_complete: bool

def plan_research(state: ResearchState):
    # Create a research plan for the given topic
    topic = state['research_topic']
    # LLM generates research plan
    plan_prompt = f"""
    Research topic: {topic}
    Create a research plan by identifyng 3-4 key aspects to investigate.
    Return a focused resaerch area to start with.
    """
    # In practice, this would use an actual LLM
    focus_area = f'key_concepts_of_{topic.replace(' ', '_')}'
    return {
        'current_focus': focus_area,
        'findings': [f'Starting research on: {topic}']
    }

def gather_information(state: ResearchState):
    # Gather information about the current focus area
    focus = state['current_focus']
    # Simulate information gathering
    # In practice, this might call APIs, search databases, etc.
    new_finding = f'Found information about {focus}'
    source = f'source_for_{focus}'
    return {
        'findings': [new_finding],
        'sources_checked': [source],
    }

def analyze_progress(state: ResearchState):
    # Analyze research progress and decide next steps
    findings_count = len(state['findings'])
    sources_count = len(state['sources_checked'])
    # Simple completion logic
    if findings_count >= 5 or sources_count >= 3:
        return {
            'research_complete': True,
            'findings': ['Research phase complete'],
        }
    else:
        # Continue with next research area
        next_focus = f'advanced_aspects_{sources_count}'
        return {
            'current_focus': next_focus,
            'findings': [f'Continuing resaerch: {next_focus}']
        }

def should_continue_research(state: ResearchState) -> str:
    # Decide whether to continue research or finish
    if state['research_complete']:
        return 'synthesize'
    else:
        return 'gather_more'

def synthesize_findings(state: ResearchState):
    # Create final resaerch summary
    findings = state['findings']
    sources = state['sources_checked']
    summary = f"""
    Research summary for: {state['resaerch_topic']}
    Key Findings:
    {chr(10).join([f'- {finding}' for finding in findings])}
    Sources Consulted: {len(sources)}
    """
    return {
        'findings': [summary],
        'research_complete': True,
    }
# Build research agent graph
resaerch_workflow = StateGraph(ResearchState)
resaerch_workflow.add_node('plan', plan_research)
resaerch_workflow.add_node('gather', gather_information)
resaerch_workflow.add_node('analyze', analyze_progress)
resaerch_workflow.add_node('synthesize', synthesize_findings)
resaerch_workflow.set_entry_point('plan')
resaerch_workflow.add_edge('plan', 'gather')
resaerch_workflow.add_edge('gather', 'analyze')
resaerch_workflow.add_conditional_edges(
    'analyze',
    should_continue_research,
    {
        'gather_more': 'gather',
        'synthesize': 'synthesize',
    }
)
resaerch_workflow.add_edge('synthesize', END)
research_agent = resaerch_workflow.compile()
