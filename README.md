# 🤖 Multi-Source Research Agent

An agentic AI system that extends my [PDF RAG Assistant](https://github.com/khushikhurana15/rag-pdf-assistant)
with autonomous tool-selection: instead of a fixed retrieve→generate pipeline, an LLM-driven
agent decides **at runtime** whether to search uploaded PDFs, search the live web, run a
calculation, or admit it doesn't know — based on reasoning over the question itself, not
hardcoded routing rules.

Built to demonstrate the core skill agentic AI roles actually test for: giving an LLM a set
of capabilities and trusting it to choose between them correctly, rather than wiring up
`if/else` logic myself.

---

## 🧠 Agent vs. My Original RAG Pipeline — What Actually Changed

My RAG project has a **fixed control flow**: every question goes through the same steps
(condense → retrieve → confidence-gate → generate), regardless of what's being asked. The
only thing that varies is the data flowing through it, never the sequence of steps itself.

This project moves that control-flow decision into the LLM's hands. Given three tools and a
question, the agent reasons about which tool fits — and if its first choice comes back
empty-handed, it can decide to try another one before giving up. That decision-making loop
(reason → act → observe → reason again) is what makes this "agentic" rather than "a chatbot
with a search function."

---

## 🖼️ Demo

**Agent picks the right tool with no hardcoded rules — and explains why:**
> **Q:** What is the difference between bagging and boosting?
>
> *Agent reasoning: "I used the `rag_tool` because your question is about AI/ML concepts,
> which are covered in the provided PDF documents."*
>
> **A:** *(returned as a Markdown comparison table, sourced from the PDF corpus)*

**Same agent, different question, different tool — automatically:**
> **Q:** What is the latest RBI repo rate?
>
> *Agent reasoning: "I used the web search tool because the question asks for current,
> real-time information, which is outside the scope of the AI/ML interview prep documents."*
>
> **A:** The latest RBI repo rate is 5.25%.

**Math questions route to the calculator, not the LLM's own arithmetic:**
> **Q:** What is 18% of 45000?
>
> *Agent reasoning: "I used the calculator tool to find 18% of 45000."*
>
> **A:** 8100.0

**Testers can bring their own PDFs.** An in-app upload panel (under "Add a new PDF to the
knowledge base") lets anyone add their own documents to the vector store without touching any
code — the agent's `rag_tool` then searches across whatever's been uploaded, so the demo isn't
limited to my original two interview-prep PDFs.

---

## ⚙️ How It Works

```
User question
      │
      ▼
┌─────────────┐
│    AGENT    │  ← Gemini LLM, reasons over the question + tool descriptions
│ (ReAct loop)│     "Which tool fits this question, if any?"
└─────────────┘
      │
      ├──► rag_tool          — hybrid-search grounded PDF lookup (reused from my RAG project)
      │        └─ if confidence is low → agent decides whether to fall back to web search
      │
      ├──► web_search_tool   — DuckDuckGo search, for live/current information
      │
      ├──► calculator_tool   — sandboxed arithmetic, for numeric questions
      │
      └──► none of the above → agent says "I don't know" rather than guessing
      │
      ▼
Final answer + visible reasoning trace (which tool, and why)
```

Built with **LangChain's `create_agent`**, which implements the ReAct pattern
(Thought → Action → Observation, repeated until the model has enough to answer) without
requiring a hand-rolled loop. Tool selection is entirely prompt-driven: each tool's
docstring is the only thing the agent uses to decide when it applies — there is no keyword
matching or manual routing code anywhere in this project.

### Confidence-gated fallback (the actual differentiator)

The PDF tool doesn't silently fail when it finds nothing relevant — it returns an explicit
`LOW_CONFIDENCE` signal (reusing the confidence gate from my original RAG project) instead of
a plain "not found" message. The agent's system prompt tells it what that signal means and
that it's free to try `web_search_tool` next, rather than treating a failed PDF search as a
dead end. This turns a static threshold check (my RAG project's original behavior) into a
runtime decision the agent makes for itself.

---

## 🏗️ Architecture / File Structure

```
research-agent-project/
├── tools/
│   ├── rag_tool.py          ← wraps the RAG pipeline below as an agent tool
│   ├── web_search_tool.py   ← DuckDuckGo search wrapper (free, no API key)
│   └── calculator_tool.py   ← sandboxed arithmetic tool (regex-filtered, no raw eval)
├── agent/
│   └── agent_core.py        ← system prompt, tool registration, agent construction + invocation
├── loader.py                ← PDF loading + chunking (carried over from the RAG project)
├── embedder.py               ← Gemini embeddings + ChromaDB storage
├── retriever.py              ← vector search, BM25 hybrid search (RRF fusion), confidence gating
├── generator.py              ← question condensing, prompt construction, Gemini answer generation
├── chroma_db/                ← local vector store (built on first run, not committed)
├── app.py                   ← Streamlit UI — chat, reasoning trace, and PDF upload
├── .env                     ← GOOGLE_API_KEY (not committed)
├── requirements.txt
└── README.md
```

This repo is **self-contained** — it includes its own copy of the RAG pipeline (`loader.py`
through `generator.py`) rather than depending on the original
[PDF RAG Assistant](https://github.com/khushikhurana15/rag-pdf-assistant) repo, so it can be
cloned and run independently. The two projects share a common origin but are maintained as
separate repos going forward.

Each tool is a self-contained, independently testable function — the agent only orchestrates.
Any tool here could be replaced (e.g. Tavily instead of DuckDuckGo) without touching the agent
logic.

---

## 🛠️ Tech Stack

- **LangChain** (`langchain.agents.create_agent`) — agent construction, ReAct tool-calling loop
- **Google Gemini API** (free tier) — `gemini-flash-latest` as the reasoning/generation model
- **RAG pipeline** — ChromaDB + hybrid (BM25 + vector, RRF-fused) retrieval + confidence gating, carried over from my [PDF RAG Assistant](https://github.com/khushikhurana15/rag-pdf-assistant) project and included here as a self-contained module
- **`ddgs` (DuckDuckGo Search)** — free web search, no API key required
- **Streamlit** — UI, extended from the RAG project to also render the reasoning trace and support in-app PDF upload
- **Python's `re` module** — input sanitization for the calculator tool (no raw `eval`)

---

## 🚀 Setup & Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/khushikhurana15/research-agent-project.git
cd research-agent-project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```
Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

### 4. Add PDFs to the knowledge base
Two options:
- **Before launching:** place PDF(s) in the project root and run `python embedder.py` to
  build the initial `chroma_db/` vector store.
- **After launching:** use the "Add a new PDF to the knowledge base" panel in the app itself —
  no restart or re-embedding of existing documents needed.

At least one PDF (via either method) is needed before `rag_tool` has anything to search.

### 5. Launch the app
```bash
streamlit run app.py
```

### 6. (Optional) Run agent tests directly from the terminal
```bash
python -m agent.agent_core
```
Prints the reasoning trace (tool used, input, output) and final answer for a single test
question defined in the script — kept to one question per run to conserve free-tier quota.

---

## 🧪 Design Decisions Worth Highlighting

- **Confidence signal instead of a silent failure.** The RAG tool returns a distinct
  `LOW_CONFIDENCE: ...` string rather than a normal-looking "I don't know" answer, so the
  agent can tell the difference between "this is the final answer" and "this tool didn't
  help, try something else." A plain string return wouldn't let the agent make that
  distinction.
- **`use_hybrid=False` fixed inside the RAG tool.** Confidence gating depends on comparable
  distance scores, which only vector-only retrieval produces (RRF-fused hybrid rankings
  aren't directly comparable to a threshold) — documented as a known trade-off in the
  original RAG project too.
- **Stateless tool calls, agent-level history.** Each RAG tool call runs with `history=[]`
  so the tool stays independently testable; multi-turn context is the agent's
  responsibility, not baked into the tool.
- **Sandboxed calculator, not raw `eval()`.** Input is regex-filtered to numbers and
  operators only, and `eval()` is called with `__builtins__` stripped out — blocks
  arbitrary code execution (verified with an `"import os"` injection test).
- **Free-tier only.** DuckDuckGo search needs no API key; Gemini's free tier covers the
  reasoning model — the whole project is reproducible with zero paid services.
- **In-app PDF upload, not a fixed corpus.** Rather than shipping only my own two PDFs, the
  app lets anyone add documents at runtime — makes the repo actually testable by someone
  who clones it, instead of only demonstrating results against a corpus they can't inspect
  or extend.
- **Self-contained repo over a shared dependency.** This project includes its own copy of the
  RAG pipeline rather than importing from the original RAG project's repo — a small amount of
  duplication in exchange for the repo being clonable and runnable on its own, which matters
  more for a portfolio piece someone else will actually try to run.

---

## 🔧 Known Limitations / Future Improvements

- **No source-recency ranking in web search.** Tested with "who won the most recent T20
  World Cup?" — search results contained both a 2024 result and a (more recent) 2026 result,
  and the agent picked the older one, likely because it was mentioned more prominently
  across sources. The agent has no mechanism to parse dates from search snippets and
  prioritize the most recent one. A production version would need explicit date-extraction
  and recency-ranking logic before trusting web search results for anything time-sensitive.
- **Tool-choice correctness isn't guaranteed.** The agent follows the system prompt's
  decision rules, but this is LLM reasoning, not a deterministic router — there's no
  guarantee it picks the objectively "correct" tool on every input, only that it's
  reasoning over the right signals. This showed up early in testing: before a system-prompt
  fix, the agent refused a Bitcoin-price question outright (assuming it had no way to answer)
  instead of trying the web search tool it actually had access to.
- **No confidence gate on web search itself.** Unlike the RAG tool, `web_search_tool` never
  returns a "low confidence" signal — it always returns whatever DuckDuckGo gives back, even
  if the results are thin, off-topic, or contradictory. The agent has no built-in way to
  detect that its web results were poor.
- **Single-turn tool statelessness.** Because RAG tool calls don't carry conversation
  history, follow-up questions like "what about boosting?" (relying on prior turns) aren't
  automatically resolved the way they are in the original RAG project's UI-level condensing —
  this would need to be re-added at the agent/UI layer, not the tool layer.
- **No re-ranking or source-trust weighting for web results**, same limitation as the
  original RAG project's retrieval — carried over here since the underlying issue (all
  sources treated as equally reliable) is common to both.

---

## 📄 License

MIT — feel free to fork and adapt.