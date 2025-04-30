from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

# Define the state
class ComplaintsSingleSampleInputStateSchema(TypedDict):
    input_dict: dict

class ComplaintsSingleSampleOutputStateSchema(TypedDict):
    output: dict


class ComplaintsSingleSampleStateSchema(ComplaintsSingleSampleInputStateSchema, ComplaintsSingleSampleOutputStateSchema):
    inner_1: dict
    inner_2: dict
    inner_3: dict
    inner_4: dict

# Nodes - these nodes are just for demonstration purposes
# In the real scenario, these are also graphs or subgraphs
async def processing_1_node(state: ComplaintsSingleSampleStateSchema):
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Output the exact same input as you received. No changes, no additional information, no formatting, no explanation."),
        ("user", json.dumps(state["input_dict"])),
    ])
    chain = prompt | llm | StrOutputParser()
    res = await chain.ainvoke(state["input_dict"])

    return {
        "inner_1": {"a": 1},
    }

async def processing_2_node(state: ComplaintsSingleSampleStateSchema):
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Output the exact same input as you received. No changes, no additional information, no formatting, no explanation."),
        ("user", json.dumps(state["input_dict"])),
    ])
    chain = prompt | llm | StrOutputParser()
    res = await chain.ainvoke(state["input_dict"])

    return {
        "inner_2": {"b": 2},
    }

async def processing_3_node(state: ComplaintsSingleSampleStateSchema):

    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Output the exact same input as you received. No changes, no additional information, no formatting, no explanation."),
        ("user", json.dumps(state["input_dict"])),
    ])
    chain = prompt | llm | StrOutputParser()
    res = await chain.ainvoke(state["input_dict"])

    return {
        "inner_3": {"c": 3},
    }

async def processing_4_node(state: ComplaintsSingleSampleStateSchema):
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Output the exact same input as you received. No changes, no additional information, no formatting, no explanation."),
        ("user", json.dumps(state["input_dict"])),
    ])
    chain = prompt | llm | StrOutputParser()
    res = await chain.ainvoke(state["input_dict"])

    return {
        "inner_4": {"d": 4},
    }

async def merge_node(state: ComplaintsSingleSampleStateSchema):
    return {
        "output": {
            "o_1": state["inner_1"],
            "o_2": state["inner_2"],
            "o_3": state["inner_3"],
            "o_4": state["inner_4"],
        },
    }

# Build the graph
# gb = graph builder
single_sample_gb = StateGraph(ComplaintsSingleSampleStateSchema, input=ComplaintsSingleSampleInputStateSchema, output=ComplaintsSingleSampleOutputStateSchema)

single_sample_gb.add_node("processing_1", processing_1_node)
single_sample_gb.add_node("processing_2", processing_2_node)
single_sample_gb.add_node("processing_3", processing_3_node)
single_sample_gb.add_node("processing_4", processing_4_node)
single_sample_gb.add_node("merge", merge_node)

single_sample_gb.add_edge(START, "processing_1")
single_sample_gb.add_edge(START, "processing_2")
single_sample_gb.add_edge(START, "processing_3")
single_sample_gb.add_edge(START, "processing_4")


single_sample_gb.add_edge(
    [
        "processing_1",
        "processing_2",
        "processing_3",
        "processing_4",
    ],
    "merge",
)

single_sample_gb.add_edge("merge", END)

single_sample_graph = single_sample_gb.compile()
