# Cost-Latency-LLM-Platform

A **real-time Streamlit dashboard** for monitoring and interacting with LLM (Large Language Model) queries. This project combines **semantic caching, model routing, async processing, and observability metrics** into a clean, interactive interface.

---

##  Features

- **Semantic Caching:** Reuse previous query responses using embedding similarity to reduce redundant API calls.  
- **Dynamic Model Routing:** Automatically routes queries to `gpt-3.5-turbo` or `gpt-4o-mini` based on query complexity/intent.  
- **Async Query Processing:** Concurrent execution of multiple queries for faster response times.  
- **Prompt Optimization:** Minimizes token usage by truncating long prompts.  
- **Token & Latency Tracking:** Monitors token usage, request latency, and cache hits.  
- **Metrics Dashboard:** Visualizes total requests, cache hits, average latency, token consumption, and model usage distribution in real-time.  
- **Retry & Resilience:** Implements retry with exponential backoff to handle API failures.  

---

##  Demo



https://github.com/user-attachments/assets/d2278965-6622-456c-8dab-21ae8a5b7f75



After running, the dashboard shows:

- Query input box (single or multiple queries)  
- Responses with cache hit indicators  
- Metrics dashboard with charts:  
  - Total Requests  
  - Cache Hits  
  - Average Latency  
  - Total Tokens Used  
  - Model Usage Distribution  

---

##  Folder Structure
llm-streamlit-dashboard/
│

├─ track.py       - Main Streamlit dashboard script

├─ README.md              -  Project documentation

├─ requirements.txt       - Optional: list of Python dependencies

