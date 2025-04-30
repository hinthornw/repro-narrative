
from typing import TypedDict
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

from langgraph.graph import StateGraph, START, END


# State
class SubgraphTemplateInputStateSchema(TypedDict):
    input_dict: dict

class SubgraphTemplateOutputStateSchema(TypedDict):
    output: dict

class SubgraphTemplateStateSchema(SubgraphTemplateInputStateSchema, SubgraphTemplateOutputStateSchema):
    pass


# Nodes
async def subgraph_template_node(state: SubgraphTemplateInputStateSchema):
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Output the exact same input as you received. No changes, no additional information, no formatting, no explanation."),
        ("user", "{text}"),
    ])
    chain = prompt | llm | StrOutputParser()
    res = await chain.ainvoke(json.dumps(state["input_dict"]))

    return {
        "output": {},
    }

# Build the graph
subgraph_template_gb = StateGraph(SubgraphTemplateStateSchema)

subgraph_template_gb.add_node("subgraph_template_node", subgraph_template_node)

subgraph_template_gb.add_edge(START, "subgraph_template_node")
subgraph_template_gb.add_edge("subgraph_template_node", END)


# Subgraphs
subgraph1 = subgraph_template_gb.compile()

subgraph2 = subgraph_template_gb.compile()

subgraph3 = subgraph_template_gb.compile()

subgraph4 = subgraph_template_gb.compile()

