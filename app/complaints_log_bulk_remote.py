from typing import Optional, TypedDict
import pandas as pd
import math
import asyncio

from langgraph.graph import StateGraph, START, END

from app.complaints_log_single_sample import single_sample_graph
from app.helpers import _read_csv_file, _read_base64_file

from langgraph_sdk import get_client

from fastcore.parallel import parallel_async
from langgraph.pregel.remote import RemoteGraph


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
    use_fastcore: Optional[bool]


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

    lg_client = get_client()

    max_concurrency = config.get("configurable", {}).get("max_concurrency", 30)
    use_fastcore = config.get("configurable", {}).get("use_fastcore", False)

    print(f"Max concurrency: {max_concurrency}")
    print(f"Use fastcore: {use_fastcore}")

    if use_fastcore:
        # Using parallel requests, at most `max_concurrency` at a time
        remote_graph = RemoteGraph("complaints_log_single_sample", client=lg_client)

        all_results = await parallel_async(
            remote_graph.ainvoke,
            [{"input_dict": input} for input in inputs],
            n_workers=max_concurrency,
        )

    else:
        # Use LangGraph SDK to batch requests
        all_results = []
        total_num_requests = len(inputs)
        num_requests_processed = 0
        batch_size = max_concurrency
        num_batches = math.ceil(total_num_requests / batch_size)
        for i in range(0, total_num_requests, batch_size):
            print(f"Processing batch {i // batch_size + 1} of {num_batches}")
            batch_inputs = inputs[i : i + batch_size]
            print(f"Number of requests in batch: {len(batch_inputs)}")
            runs = await lg_client.runs.create_batch(
                [
                    {"assistant_id": "complaints_log_single_sample", "input": {"input_dict": input}}
                    for input in batch_inputs
                ]
            )
            batch_results = await asyncio.gather(
                *(lg_client.runs.join(r["thread_id"], r["run_id"]) for r in runs)
            )
            all_results.extend(batch_results)
            num_requests_processed += len(batch_results)
            print(
                f"Number of requests processed: {num_requests_processed} / {total_num_requests}"
            )

    return {
        "output": all_results,
    }


# Build the graph
bulk_gb = StateGraph(ComplaintsBulkStateSchema, BulkConfigSchema, input=ComplaintsBulkInputStateSchema, output=ComplaintsBulkOutputStateSchema)

bulk_gb.add_node("read_csv_file", read_csv_file_node)
bulk_gb.add_node("apply_single_sample_endpoint", apply_single_sample_endpoint_node)

bulk_gb.add_edge(START, "read_csv_file")
bulk_gb.add_edge("read_csv_file", "apply_single_sample_endpoint")
bulk_gb.add_edge("apply_single_sample_endpoint", END)

bulk_graph = bulk_gb.compile()
