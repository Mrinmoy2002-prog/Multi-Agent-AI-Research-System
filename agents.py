from dotenv import load_dotenv
import os
import requests
from tiktoken import model

load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient
from rich import print
from langchain.agents import create_agent 
from langchain.agents.middleware import wrap_tool_call
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import get_web_content, scrape_website_url

#model setup
llm = ChatMistralAI(model="mistral-small-latest", temperature=0)

# web_search_tool 
def build_search_agent():
    return create_agent(
        model=llm,
        tools = [get_web_content])


#web scrapper agent 

def build_reader_agent():
    return create_agent(
        model=llm,
        tools = [scrape_website_url]
    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()


if __name__ == "__main__":
    topic = "The impact of AI on the job market in 2024"
    memory_state = {}

    # Step 1: Search for information
    print("\n"+"="*50)
    print("step 1 - search agent is working ...")
    print("="*50)
    search_agent = build_search_agent()
    search_results = search_agent.invoke({
            "messages": [
                ("user", f"Search for most recent and reliable information on the topic: {topic}")
            ]
    })
    print("\n search result ",search_results["messages"][-1].content)


