from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated

def reduce(a, b):
    if a is None:
        return b
    else:
        return a


async def complaints_log(state):
    llm = ChatOpenAI()
    await llm.ainvoke("Hey")


class State1(TypedDict):
   data: Annotated[dict, reduce]


graph0 = StateGraph(State1)
graph0.add_node(complaints_log)
graph0.add_edge(START, "complaints_log")
graph0 = graph0.compile()


graph1 = StateGraph(State1)
graph1.add_node("s1", graph0)
graph1.add_node("s2", graph0)
graph1.add_node("s3", graph0)
graph1.add_node("s4", graph0)
graph1.add_edge(START, "s1")
graph1.add_edge(START, "s2")
graph1.add_edge(START, "s3")
graph1.add_edge(START, "s4")
graph1 = graph1.compile()


async def process_rows(state):
    rows = [{"data": r} for r in state['rows']]
    print(rows)
    await graph1.abatch(rows, config={"max_concurrency": 30})

class State2(TypedDict):
   rows: list


graph2 = StateGraph(State2)
graph2.add_node(process_rows)
graph2.add_edge(START, "process_rows")
graph2.add_edge("process_rows", END)
agent = graph2.compile()