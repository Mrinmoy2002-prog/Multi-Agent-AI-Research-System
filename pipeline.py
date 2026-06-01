from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from rich import print

def run_research_pipeline(topic : str) -> dict:

    memory_state = {}

    # Step 1: Search for information
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": [
            ("user", f"Search for most recent and reliable information on the topic: {topic}")
        ]
    })

    memory_state["search_results"] = search_results["messages"][-1].content

    print("\n search result ",memory_state['search_results'])


    # Step 2: Read and extract key information
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{memory_state['search_results'][:800]}"
        )]
    })
    memory_state["scraped_website_content"] = reader_result["messages"][-1].content

    print("\nscraped website content: \n", memory_state['scraped_website_content'])


    # Step 3: Write a detailed research report
    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    combined_report = (
        f"SEARCH RESULTS : \n {memory_state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {memory_state['scraped_website_content']}"
    )

    # Step 4 : Generate the report using the writer chain
    report = writer_chain.invoke({
        "topic": topic,
        "research": combined_report
    })

    memory_state["final_report"] = report
    print("\nfinal r    eport: \n", memory_state['final_report'])


    # Step 5: Critique the report
    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    memory_state["feedback"] = critic_chain.invoke({
        "report": memory_state["final_report"]
    })

    print("\n critic report \n", memory_state['feedback'])

    return memory_state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)