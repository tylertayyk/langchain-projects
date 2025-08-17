from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class ProblemState(TypedDict):
    original_problem: str
    problem_breakdown: Annotated[List[str], operator.add]
    solutions: Annotated[List[str], operator.add]
    current_subproblem: str
    solved_subproblems: Annotated[List[str], operator.add]
    final_solution: str

def decompose_problem(state: ProblemState):
    # Break complex problem into manageable subproblems
    problem = state['original_problem']
    # Simulate problem decomposition
    subproblems = [
        f'Understand the core issue in: {problem}',
        f'Identify key constraints for: {problem}',
        f'Generate potential approaches for: {problem}',
        f'Evaluate feasibility of solutions for: {problem}',
    ]
    return {
        'problem_breakdown': subproblems,
        'current_subproblem': subproblems[0]
    }

def solve_subproblem(state: ProblemState):
    # Work on the current subproblem
    subproblem = state['current_subproblem']
    # Simulate solving the subproblem
    solution = f'Solution approach for: {subproblem}'
    return {
        'solutions': [solution],
        'solving_subproblems': [subproblem],
    }

def check_completion(state: ProblemState) -> str:
    # Check if all subproblems are solved
    total_subproblems = len(state['problem_breakdown'])
    solved_count = len(state['solved_subproblems'])
    if solved_count >= total_subproblems:
        return 'integrate'
    else:
        return 'continue'

def get_next_subproblem(state: ProblemState):
    # Move to the next unsolved subproblem
    solved = set(state['solved_subproblems'])
    breakdown = state['problem_breakdown']
    # Find next unsolved subproblem
    for subproblem in breakdown:
        if subproblem not in solved:
            return {'current_subproblem': subproblem}
    return {'current_subproblem': ''}

def integrate_solutions(state: ProblemState):
    # Combine subproblem solutions into final solution
    solutions = state['solutions']
    original_problem = state['original_problem']
    final_solution = f"""
    Complete solution for: {original_problem}
    Approach:
    {chr(10).join([f'{i+1}. {solution}' for i, solution in enumerate(solutions)])}
    This integrated approach addresses all aspects of the original problem.
    """
    return {'final_solution': final_solution}

# Build problem-solving agent
problem_workflow = StateGraph(ProblemState)
problem_workflow.add_node('decompose', decompose_problem)
problem_workflow.add_node('solve', solve_subproblem)
problem_workflow.add_node('next', get_next_subproblem)
problem_workflow.add_node('integrate', integrate_solutions)
problem_workflow.set_entry_point('decompose')
problem_workflow.add_edge('decompose', 'solve')
problem_workflow.add_conditional_edges(
    'solve',
    check_completion,
    {
        'continue': 'next',
        'integrate': 'integrate',
    }
)
problem_workflow.add_edge('next', 'solve')
problem_workflow.add_edge('integrate', END)
problem_solver = problem_workflow.compile()
