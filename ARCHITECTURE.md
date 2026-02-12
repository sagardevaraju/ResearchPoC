# GeoSupply Copilot — System Architecture & Data Flow

> A high-level overview of how the system works, designed for non-technical audiences.

---

## System Architecture

The system has three layers:

- **Dashboard** — what users see in their browser
- **Application Server** — the brain that runs all analysis
- **Data & AI Layer** — where information and intelligence live

```
+------------------------------------------------------------------+
|                       USER (Web Browser)                          |
|                                                                  |
|  +--------------+ +--------------+ +-------------------------+  |
|  | Trade-Block  | |   Shipment   | |      Risk Alerts        |  |
|  |   Scenario   | |    Health    | |                         |  |
|  +--------------+ +--------------+ +-------------------------+  |
|  +--------------+ +------------------------------------------+  |
|  |   Alternate  | |   Q&A Chat                               |  |
|  |   Sourcing   | |   (ask questions in plain English)       |  |
|  +--------------+ +------------------------------------------+  |
|  +------------------------+ +-----------------------------+     |
|  |   Shipment Details     | |   Supplier Details          |     |
|  +------------------------+ +-----------------------------+     |
+-------------------------------+----------------------------------+
                                |
                    User opens website
                     or asks a question
                                |
                                v
+------------------------------------------------------------------+
|                  APPLICATION SERVER (Python)                       |
|                                                                   |
|  +-------------------+       +--------------------------------+   |
|  | Risk Detection    |       | Smart Q&A                      |   |
|  |                   |       |                                |   |
|  | - Scans news for  |       |  Primary: AI-powered answers   |   |
|  |   trade-block     |       |  using RAG to stay grounded    |   |
|  |   events          |       |  in real data                  |   |
|  | - Flags at-risk   |       |                                |   |
|  |   shipments       |       |  Fallback: Built-in rule       |   |
|  | - Assigns         |       |  engine if AI is unavailable   |   |
|  |   severity        |       |                                |   |
|  +-------------------+       +--------------------------------+   |
|  +-------------------+       +--------------------------------+   |
|  | Alternative       |       | RAG Pipeline                   |   |
|  | Sourcing          |       | (Retrieval-Augmented           |   |
|  |                   |       |  Generation)                   |   |
|  | - Finds safe      |       |                                |   |
|  |   suppliers       |       | - Turns all data into          |   |
|  |   outside blocked |       |   searchable documents         |   |
|  |   countries       |       | - Finds the most relevant      |   |
|  | - Ranks by        |       |   snippets per question        |   |
|  |   performance     |       | - Feeds context to AI so       |   |
|  |                   |       |   answers stay accurate         |   |
|  +-------------------+       +--------------------------------+   |
|  +------------------------------------------------------------+   |
|  | Safety & Validation Layer                                   |   |
|  | - Checks AI answers against real data (no made-up facts)    |   |
|  | - Verifies every supplier/shipment ID actually exists       |   |
|  | - Falls back to rule engine if AI gives a bad answer        |   |
|  +------------------------------------------------------------+   |
+-----------------+-----------------------------+-------------------+
                  |                             |
                  v                             v
+---------------------------+   +----------------------------------+
|      DATA LAYER           |   |      AI LAYER (Optional)         |
|      (JSON Files)         |   |                                  |
|                           |   |  Any LLM that exposes an         |
|  News                     |   |  OpenAI-compatible chat API      |
|  Geopolitical events      |   |                                  |
|  and trade blocks         |   |  Examples:                       |
|                           |   |  - Local model via Ollama        |
|  Suppliers                |   |    or LM Studio                  |
|  Who they are and         |   |  - Cloud-hosted model endpoint   |
|  where they operate       |   |  - Any OpenAI-compatible API     |
|                           |   |                                  |
|  Shipments                |   |  Configured via environment      |
|  What is moving, from     |   |  variables -- swap models        |
|  where, and delays        |   |  without changing code           |
|                           |   |                                  |
|  Performance              |   +----------------------------------+
|  How reliable each        |
|  supplier has been        |
+---------------------------+
```

---

## Data Flow

### Flow 1: Opening the Dashboard

```
  +------+                              +--------------+
  |      |  (1) Open website            |              |
  | User | ---------------------------> | App Server   |
  |      |                              |              |
  |      |                              | (2) Load all |
  |      |                              |     data     |
  |      |                              |       |      |
  |      |                              |       v      |
  |      |                              | (3) Analyze  |
  |      |                              |   - Detect   |
  |      |                              |     trade    |
  |      |                              |     blocks   |
  |      |                              |   - Flag     |
  |      |                              |     at-risk  |
  |      |                              |     items    |
  |      |                              |   - Find     |
  |      |                              |     safer    |
  |      |                              |     sources  |
  |      |  (4) Complete dashboard      |   - Build    |
  |      | <--------------------------- |     health   |
  +------+     with all insights        |     summary  |
                                        +--------------+
```

**In plain English:**

1. You open the website in your browser.
2. The server reads all supply-chain data (news, suppliers, shipments, performance).
3. It runs analysis — detecting risks, flagging affected shipments, and finding alternatives.
4. It sends back a complete dashboard with all insights ready to view.

---

### Flow 2: Asking a Question (Q&A Chat)

```
  +------+  (1) "Which supplier      +--------------+      +-----------+
  |      |      has the most  -----> |              |      |           |
  | User |      delays?"             | App Server   |      | AI Model  |
  |      |                           |              |      | (any LLM) |
  |      |                           | (2) Build a  |      |           |
  |      |                           |   knowledge  |      |           |
  |      |                           |   base from  |      |           |
  |      |                           |   all data   |      |           |
  |      |                           |      |       |      |           |
  |      |                           |      v       |      |           |
  |      |                           | (3) Find the |      |           |
  |      |                           |   most       |      |           |
  |      |                           |   relevant   |      |           |
  |      |                           |   snippets   |      |           |
  |      |                           |      |       |      |           |
  |      |                           |      v       |      |           |
  |      |                           | (4) Question |      |           |
  |      |                           |   + context  -----> | (5) Build |
  |      |                           |              |      |   answer  |
  |      |                           | (6) Receive  <----- |   using   |
  |      |                           |   answer     |      |   data    |
  |      |                           |      |       |      +-----------+
  |      |                           |      v       |
  |      |                           | (7) Validate |
  |      |                           |   - IDs real?|
  |      |                           |   - Facts    |
  |      |  (8) Verified answer      |     match?   |
  |      | <-------- + sources ----- |              |
  +------+                           +--------------+

       - - - - - - - - - - - - - - - - - - - - - - -
       If AI is unavailable or returns a bad answer:
       - - - - - - - - - - - - - - - - - - - - - - -

  +------+                           +--------------+
  | User |  Answer from built-in     | App Server   |
  |      | <---- rule engine -------- | (fallback)   |
  +------+                           +--------------+
```

**In plain English:**

1. You type a question like "Which supplier has the most delays?"
2. The server converts all supply-chain data into a searchable knowledge base.
3. It finds the most relevant data snippets for your question (this is called "RAG").
4. It sends your question plus the relevant data to the AI model.
5. The AI generates a natural-language answer grounded in real data.
6. The server validates the answer — checking that every ID and fact is real.
7. If the AI is unavailable or gives a questionable answer, a built-in rule engine provides the answer instead.
8. You see the verified answer along with the data sources it used.

---

## Component Summary

| Component | What It Does | Technology |
|---|---|---|
| **Dashboard UI** | Displays all insights in an interactive web page | HTML, CSS, JavaScript |
| **App Server** | The "brain" — runs all analysis and coordinates everything | Python (Flask) |
| **Risk Detection** | Scans news for geopolitical events, flags affected shipments | Python logic |
| **Alternative Sourcing** | Recommends safer suppliers outside blocked countries | Python logic |
| **RAG Search** | Finds the most relevant data to answer each question | TF-IDF (scikit-learn) |
| **AI Model** | Generates natural-language answers from data context | Any OpenAI-compatible LLM |
| **Validation Layer** | Fact-checks AI answers against real data | Python logic |
| **Fallback Q&A** | Answers questions using rules when AI is unavailable | Python logic |
| **Data Files** | Synthetic supply-chain data (news, suppliers, shipments, performance) | JSON files |

---

## Key Design Principles

1. **Model-agnostic** — Works with any Large Language Model that provides an OpenAI-compatible chat API. Swap models by changing an environment variable — no code changes required.

2. **AI with guardrails** — The AI never answers in a vacuum. It only sees real data, and its answers are validated before reaching the user.

3. **Always available** — Even without any AI model running, the dashboard and Q&A still work using built-in rules.

4. **Transparent sourcing** — Every AI answer shows which data sources it used, so users can verify the reasoning.

5. **Self-contained** — All data is local (JSON files). No external databases or cloud services required for the core experience.

---

## Deployment Overview

```
Your Computer (or Server)
|-- Python App Server (port 8000) ------ serves the dashboard
|-- AI Model endpoint (configurable) --- optional, for smarter Q&A
|   (any OpenAI-compatible API)
|-- Data Files (data/) ----------------- all supply-chain information
```

**To run:** Start the app with `python app.py` and open `http://localhost:8000` in your browser.

The AI model is **optional** — the system works without it using the built-in fallback engine. Configure the AI endpoint via environment variables `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`.
