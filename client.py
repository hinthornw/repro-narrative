from langgraph_sdk import get_client
import asyncio

url = "https://xushu-fdd66e4f27c55f63aeac95cf5d7ba3bf.us.langgraph.app"
client = get_client(url=url)


async def main():
    await client.graphs.list()


if __name__ == "__main__":
    asyncio.run(main())
