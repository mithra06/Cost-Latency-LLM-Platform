# filename: llm_dashboard.py

import streamlit as st
import asyncio
import time
import numpy as np
from openai import OpenAI
import nest_asyncio
nest_asyncio.apply()
# ---------------------------
# 🔹 LLM Client
# ---------------------------
client = OpenAI(api_key="your api key")

# ---------------------------
# 🔹 Cache
# ---------------------------
cache = []

# ---------------------------
# 🔹 Metrics Tracker
# ---------------------------
class Metrics:
    def __init__(self):
        self.total_requests = 0
        self.cache_hits = 0
        self.total_latency = 0
        self.total_tokens = 0
        self.model_usage = {}

    def log_request(self, latency, tokens, model, cache_hit=False):
        self.total_requests += 1
        self.total_latency += latency
        self.total_tokens += tokens

        if cache_hit:
            self.cache_hits += 1

        if model:
            self.model_usage[model] = self.model_usage.get(model, 0) + 1

    def get_summary(self):
        avg_latency = self.total_latency / max(self.total_requests, 1)
        return {
            "Total Requests": self.total_requests,
            "Cache Hits": self.cache_hits,
            "Avg Latency (s)": round(avg_latency, 2),
            "Total Tokens": self.total_tokens,
            "Model Usage": self.model_usage
        }

metrics = Metrics()

# ---------------------------
# 🔹 Helper Functions
# ---------------------------
def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)

def is_similar(vec1, vec2, threshold=0.9):
    sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return sim > threshold

def choose_model(query):
    keywords = ["explain", "compare", "difference", "detailed"]
    if any(k in query.lower() for k in keywords):
        return "gpt-4o-mini"
    return "gpt-3.5-turbo"

def optimize_prompt(query):
    return query[:200]

async def call_llm(model, prompt, retries=3):
    for i in range(retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception as e:
            await asyncio.sleep(2 ** i)
    raise Exception("LLM call failed after retries")

# ---------------------------
# 🔹 Process Query Async
# ---------------------------
semaphore = asyncio.Semaphore(3)

async def process_query(query):
    async with semaphore:
        start = time.time()

        optimized_query = optimize_prompt(query)
        embedding = get_embedding(optimized_query)

        # Check cache
        for old_query, q_emb, ans in cache:
            if is_similar(embedding, q_emb):
                metrics.log_request(latency=0, tokens=0, model=None, cache_hit=True)
                return ans, True

        # Route model
        model = choose_model(query)

        # Call LLM
        response = await call_llm(model, optimized_query)
        answer = response.choices[0].message.content

        # Cache it
        cache.append((query, embedding, answer))

        end = time.time()
        latency = end - start

        # Log metrics
        metrics.log_request(
            latency=latency,
            tokens=response.usage.total_tokens,
            model=model,
            cache_hit=False
        )

        return answer, False

# ---------------------------
# 🔹 Run multiple queries
# ---------------------------
async def run_queries(queries):
    tasks = [process_query(q) for q in queries]
    return await asyncio.gather(*tasks)

# ---------------------------
# 🔹 Streamlit App
# ---------------------------
st.set_page_config(page_title="LLM Dashboard", layout="wide")
st.title("🚀 LLM System Dashboard")

query_input = st.text_area("Enter one or multiple queries (one per line):")
if st.button("Run Queries") and query_input.strip():
    queries = [q.strip() for q in query_input.split("\n") if q.strip()]

    with st.spinner("Processing queries..."):
        results = asyncio.run(run_queries(queries))

    # Show results
    st.subheader("💬 Responses")
    for q, (r, cache_hit) in zip(queries, results):
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {r}")
        st.markdown(f"*Cache Hit:* {'Yes' if cache_hit else 'No'}")
        st.markdown("---")

    # Show dashboard metrics
    st.subheader("📊 Metrics Dashboard")
    summary = metrics.get_summary()
    st.metric("Total Requests", summary["Total Requests"])
    st.metric("Cache Hits", summary["Cache Hits"])
    st.metric("Avg Latency (s)", summary["Avg Latency (s)"])
    st.metric("Total Tokens", summary["Total Tokens"])

    st.subheader("Model Usage Distribution")
    st.bar_chart(summary["Model Usage"])