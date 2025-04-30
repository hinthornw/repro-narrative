from typing import Optional, TypedDict
import pandas as pd

from langgraph.graph import StateGraph, START, END

from app.subgraphs.complaints_log_single_sample import complaints_log_single_sample_subgraph
from app.helpers import _read_csv_file, _read_base64_file



# Define the state
class ComplaintsBulkInputStateSchema(TypedDict):
    file_url: Optional[str]
    file_base64: Optional[str]

class ComplaintsBulkOutputStateSchema(TypedDict):
    output: list[dict]

class ComplaintsBulkStateSchema(ComplaintsBulkInputStateSchema, ComplaintsBulkOutputStateSchema):
    input_df: pd.DataFrame

# Config
class BulkConfigSchema(TypedDict):
    max_concurrency: Optional[int]


# Nodes
async def read_csv_file_node(state: ComplaintsBulkStateSchema):
    if "file_url" in state and state["file_url"] is not None:
        print("Reading CSV file from URL.")
        df = _read_csv_file(state["file_url"])
    elif "file_base64" in state and state["file_base64"] is not None:
        print("URL not provided. Reading CSV file from base64.")
        df = _read_base64_file(state["file_base64"])
    else:
        raise ValueError("Either 'file_url' or 'file_base64' must be provided.")

    return {
        "input_df": df,
    }


async def apply_single_sample_endpoint_node(state: ComplaintsBulkStateSchema, config: BulkConfigSchema):
    inputs = (
        state["input_df"]
        .apply(
            lambda row: row.to_dict(),
            axis=1,
        )
        .tolist()
    )

    max_concurrency = config.get("configurable", {}).get("max_concurrency", 30)
    print(f"Max concurrency: {max_concurrency}")

    res = await complaints_log_single_sample_subgraph.abatch(
        [{"input_dict": input_dict} for input_dict in inputs],
        config={"max_concurrency": max_concurrency},
    )

    return {
        "output": res,
    }


# Build the graph
bulk_gb = StateGraph(ComplaintsBulkStateSchema, BulkConfigSchema, input=ComplaintsBulkInputStateSchema, output=ComplaintsBulkOutputStateSchema)

bulk_gb.add_node("read_csv_file", read_csv_file_node)
bulk_gb.add_node("apply_single_sample_endpoint", apply_single_sample_endpoint_node)

bulk_gb.add_edge(START, "read_csv_file")
bulk_gb.add_edge("read_csv_file", "apply_single_sample_endpoint")
bulk_gb.add_edge("apply_single_sample_endpoint", END)

bulk_graph = bulk_gb.compile()
