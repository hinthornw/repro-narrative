# langgraph-mininal

Runs locally with `langgraph up`.

`/data` folder contains examples of input data:
- `.csv` files (for visual inspection, you likely don't need to look at it)
- `.base64.json` files than contain the same data as .csv files, but in the format the graph can easily parse both locally and on the remote.


## Graphs
The Graphs follow a very similar structured that we have in our real app. The prompts are changed to have stub values.

- `complaints_log_single_sample` -> processes a single complaint, a row from the app
- `complaints_log_bulk` -> processes the whole file. It invokes the subgraph locally.
- `complaints_log_bulk_remote` -> processes the whole file. Invokes the subgraph as a remote graph, thus should autoscale better.
    - It is parametrized with:
        - `max_concurrency` -> the maximum number of concurrent requests it would make. Default is `30`.
        - `use_fastcore` -> if `False` it will use the built in batching in `langgraph sdk`. If `True` it will make concurrent requests to the remote graph, limiting their number to `max_concurrency`. Defalut is `False`.

## Graphs with subgraphs
Our produciton agents contain nested subgraphs. It can happen that a graph calls a subgraph that calls another subgraph.

In the `/subgraph` folder, the logic is the same as in the parent folder, except that `single sample` graph calls subgraphs instead of `ChatOpenAI`.

`complaints_log_bulk_subgraph` is the closest here that we have in production.