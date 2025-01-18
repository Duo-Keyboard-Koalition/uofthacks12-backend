from typing import TypedDict, List, Annotated, Sequence, Dict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

class StoicState(TypedDict):
    messages: List[BaseMessage]
    control_analysis: Dict | None

def create_control_analyzer():
    # Initialize the model
    model = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Create the control analysis prompt
    control_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Stoic philosopher and advisor. Your task is to analyze situations and determine whether they are within or outside our control.

        Follow these Stoic principles:
        - Within our control: Our thoughts, judgments, intentions, attitudes, responses, and actions
        - Outside our control: Other people's actions, natural events, past events, and external circumstances
        - Partially within our control: Outcomes that we can influence but not completely control

        Provide your analysis in a structured format that can be parsed as JSON with these exact keys:
        {
            "control_category": "within"|"outside"|"partial",
            "reasoning": "your detailed explanation here",
            "stoic_advice": "your practical advice based on Stoic principles",
            "controllable_aspects": ["list of aspects within control"],
            "uncontrollable_aspects": ["list of aspects outside control"]
        }

        Ensure your response is ONLY the JSON structure with no additional text."""),
        ("human", "{input}")
    ])

    def analyze_control(state: StoicState) -> StoicState:
        # Get the last message
        last_message = state["messages"][-1].content
        
        # Generate the control analysis
        prompt = control_prompt.format_messages(input=last_message)
        response = model.invoke(prompt)
        
        # Parse the response as a dictionary
        try:
            import json
            analysis_dict = json.loads(response.content)
        except json.JSONDecodeError:
            analysis_dict = {
                "error": "Failed to parse response",
                "raw_response": response.content
            }
        
        # Update state with analysis
        state["control_analysis"] = analysis_dict
        state["messages"].append(AIMessage(content=str(analysis_dict)))
        
        return state

    # Create the graph
    workflow = StateGraph(StoicState)
    
    # Add the control analysis node
    workflow.add_node("analyze_control", analyze_control)
    
    # Create edges
    workflow.set_entry_point("analyze_control")
    workflow.add_edge("analyze_control", END)
    
    # Compile the graph
    chain = workflow.compile()
    
    return chain

def analyze_situation(situation: str) -> dict:
    # Initialize the chain
    chain = create_control_analyzer()
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=situation)],
        "control_analysis": None
    }
    
    # Run the analysis
    result = chain.invoke(initial_state)
    
    # Return just the analysis part
    return result["control_analysis"]
