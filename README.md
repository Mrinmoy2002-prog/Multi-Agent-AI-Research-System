# 🔬 Multi-Agent AI Research System

Welcome to the **Multi-Agent AI Research System**! This is an autonomous, deep-dive research engine that replaces hours of manual web searching, link scraping, report drafting, and self-editing with a coordinated pipeline of specialized AI agents and chains. 

Powered by **Mistral AI**, **LangChain**, and **Tavily**, the system spins up an autonomous research team right in your browser, unrolls a stunning retro-cyberpunk dashboard built with **Streamlit**, and hands you a beautifully formatted, publication-ready research report in seconds.

---

## ⚡ Features

* **Autonomous Research Team:** Leverages specialized AI agents working sequentially to gather intelligence, scrape deep content, write structured reports, and critique the final output.
* **Live Multi-Step Pipeline Tracking:** A custom-themed Streamlit UI renders real-time tracking indicators (`Scanning`, `Scraping`, `Drafting`, `Reviewing`) as the agents progress.
* **State-Aware Architecture:** Utilizes a unified `memory_state` dictionary pattern to securely pass contexts cleanly from agent to agent without string leaks.
* **Built-in Analytical Critic:** An automated editorial chain audits the report, grades it out of 10, highlights core strengths, and flags areas to improve.
* **One-Click Markdown Export:** Download the finalized report and critic feedback immediately as a clean, locally editable `.md` file.

---

## 🏗️ System Architecture & Workflow

The architecture follows a sequential State-Machine pattern. Each logical step isolates its responsibilities, pulls data dynamically using real-time external tool executions, and pushes its output straight into a central `memory_state` dictionary.

Here is the exact technical flow of data inside the system:

```text
                       ┌───────────────────────────────────────┐
                       │    [USER] Enter a Research Topic      │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │  [SYSTEM] Initialize memory_state {}  │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ STEP 1: SEARCH AGENT (Tavily Tool)                                        │
 ├───────────────────────────────────────────────────────────────────────────┤
 │  [Action]  Executes deep web sweep for live, authoritative context.      │
 │  [Memory]  Updates state ──► memory_state["search_results"]               │
 └─────────────────────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ STEP 2: READER AGENT (Scraper Tool)                                       │
 ├───────────────────────────────────────────────────────────────────────────┤
 │  [Action]  Parses step 1 text, picks top URL, extracts deep web raw text. │
 │  [Memory]  Updates state ──► memory_state["scraped_website_content"]     │
 └─────────────────────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
                       ┌───────────────────────────────────────┐
                       │   [MERGE] Combine Data Outputs        │
                       │   Unifies Search + Scraped Text       │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ STEP 3: WRITER CHAIN (Prompt | LLM | Parser)                              │
 ├───────────────────────────────────────────────────────────────────────────┤
 │  [Action]  Synthesizes unified data into clean, structured Markdown.      │
 │  [Memory]  Updates state ──► memory_state["final_report"]                 │
 └─────────────────────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ STEP 4: CRITIC CHAIN (Prompt | LLM | Parser)                              │
 ├───────────────────────────────────────────────────────────────────────────┤
 │  [Action]  Audits the report, assigns an explicit score, issues verdict. │
 │  [Memory]  Updates state ──► memory_state["feedback"]                     │
 └─────────────────────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
                       ┌───────────────────────────────────────┐
                       │ [APP.PY Frontend] Render Dashboard    │
                       │ Displays split tabs & Markdown body   │
                       └───────────────────────────────────────┘




🛠️ Local Installation & Setup
Want to run this system locally on your machine? Follow these straightforward setup steps:

1. Clone the Project

Bash
git clone [https://github.com/YOUR_USERNAME/Multi-Agent-AI-Research-System.git](https://github.com/YOUR_USERNAME/Multi-Agent-AI-Research-System.git)
cd Multi-Agent-AI-Research-System


2. Set Up Your Virtual Environment & Install Packages

Bash
# Create the environment named 'agent' to match your tree structure
python -m venv agent

# Activate the environment (Windows PowerShell)
.\agent\Scripts\Activate.ps1

# Activate the environment (Mac/Linux Terminal)
source agent/bin/activate

# Install all system dependencies
pip install -r requirements.txt


3. Configure Your Environment Variables

Create a file named .env in the root folder of your project and paste your active developer API keys:

Plaintext
MISTRAL_API_KEY=your_mistral_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here


4. Boot Up the Dashboard

Bash
streamlit run app.py


☁️ Cloud Deployment Note
This application is built for cloud architectures! It can be deployed effortlessly on Hugging Face Spaces using their free Docker container tier (CPU Basic).

When deploying to production, make sure to add your environment variables (MISTRAL_API_KEY, TAVILY_API_KEY, OPENWEATHER_API_KEY) safely through the platform's native secret configuration panel instead of uploading a .env file.

📄 License
Distributed under the MIT License. Feel free to fork, study, and expand this agent network!