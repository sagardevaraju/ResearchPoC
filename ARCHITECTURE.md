# GeoSupply Copilot — System Architecture & Data Flow

> A high-level overview of how the system works, designed for non-technical audiences.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER (Web Browser)                         │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │               GeoSupply Copilot Dashboard                     │  │
│  │                                                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐  │  │
│  │  │ Trade    │ │ Shipment │ │ Risk      │ │ Alternate     │  │  │
│  │  │ Block    │ │ Health   │ │ Alerts    │ │ Sourcing      │  │  │
│  │  │ Scenario │ │ Overview │ │           │ │ Suggestions   │  │  │
│  │  └──────────┘ └──────────┘ └───────────┘ └───────────────┘  │  │
│  │                                                               │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │          Q&A Chat (Ask questions in plain English)      │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                               │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────────┐  │  │
│  │  │  Shipment Details    │  │  Supplier Details             │  │  │
│  │  │  (click to explore)  │  │  (click to explore)           │  │  │
│  │  └──────────────────────┘  └──────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                     User opens website /
                     asks a question
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION SERVER (Flask)                      │
│                         (app.py · Python)                            │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Core Intelligence Engines                   │  │
│  │                                                                │  │
│  │  ┌─────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │ Risk Detection  │    │ Smart Q&A (two approaches)       │  │  │
│  │  │                 │    │                                    │  │  │
│  │  │ • Scans news    │    │  1. AI Model (Mistral LLM)       │  │  │
│  │  │   for trade     │    │     ↕ Uses RAG to ground         │  │  │
│  │  │   block events  │    │       answers in real data        │  │  │
│  │  │ • Matches at-   │    │                                    │  │  │
│  │  │   risk shipments│    │  2. Built-in Fallback Engine      │  │  │
│  │  │ • Flags alerts  │    │     ↕ Rule-based answers if       │  │  │
│  │  │   by severity   │    │       AI is unavailable            │  │  │
│  │  └─────────────────┘    └──────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌─────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │ Alternative     │    │ RAG Pipeline                      │  │  │
│  │  │ Sourcing        │    │ (Retrieval-Augmented Generation)  │  │  │
│  │  │                 │    │                                    │  │  │
│  │  │ • Finds safe    │    │ • Converts all data into          │  │  │
│  │  │   suppliers     │    │   searchable text documents        │  │  │
│  │  │   outside       │    │ • Finds the most relevant          │  │  │
│  │  │   blocked       │    │   snippets for each question       │  │  │
│  │  │   countries     │    │ • Feeds context to the AI          │  │  │
│  │  │ • Ranks by      │    │   so it answers accurately         │  │  │
│  │  │   performance   │    │                                    │  │  │
│  │  └─────────────────┘    └──────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐  │  │
│  │  │ Safety & Validation Layer                                 │  │  │
│  │  │ • Checks AI answers against real data (no hallucinations) │  │  │
│  │  │ • Verifies supplier/shipment IDs actually exist           │  │  │
│  │  │ • Falls back to built-in engine if AI gives bad answers   │  │  │
│  │  └──────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────┬────────────────────────────────┬─────────────────────────┘
           │                                │
           ▼                                ▼
┌─────────────────────┐        ┌─────────────────────────┐
│   DATA LAYER        │        │   AI MODEL              │
│   (JSON Files)      │        │                          │
│                     │        │   Local LLM              │
│  ┌───────────────┐  │        │   running on your        │
│  │ 📰 News       │  │        │   machine via            │
│  │ Geopolitical  │  │        │   OpenAI-compatible API   │
│  │ events &      │  │        │                          │
│  │ trade blocks  │  │        │   (http://localhost:8085) │
│  └───────────────┘  │        └─────────────────────────┘
│  ┌───────────────┐  │
│  │ 🏭 Suppliers  │  │
│  │ Who they are, │  │
│  │ where they're │  │
│  │ located       │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ 🚢 Shipments  │  │
│  │ What's moving,│  │
│  │ from where,   │  │
│  │ delays        │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ 📊 Performance│  │
│  │ How reliable  │  │
│  │ each supplier │  │
│  │ has been      │  │
│  └───────────────┘  │
└─────────────────────┘
```

---

## 🔄 Data Flow — What Happens When You Use the Dashboard

### Flow 1: Opening the Dashboard (viewing the page)

```
 ┌──────┐       ① Open website        ┌────────────┐
 │ User │ ─────────────────────────▶  │ App Server  │
 │      │                              │             │
 │      │                              │  ② Load all │
 │      │                              │  data files │
 │      │                              │      │      │
 │      │                              │      ▼      │
 │      │                              │  ③ Analyze: │
 │      │                              │  • Detect   │
 │      │                              │    trade    │
 │      │                              │    blocks   │
 │      │                              │  • Flag     │
 │      │                              │    at-risk  │
 │      │                              │    shipments│
 │      │                              │  • Find     │
 │      │                              │    safer    │
 │      │                              │    suppliers│
 │      │                              │  • Summarize│
 │      │   ④ Send complete dashboard  │    shipment │
 │      │ ◀──────────────────────────  │    health   │
 └──────┘     with all insights        └────────────┘
```

**In plain English:**
1. You open the website in your browser
2. The server reads all the supply chain data (news, suppliers, shipments, performance)
3. It runs analysis to detect risks, flag affected shipments, and suggest alternatives
4. It sends back a complete dashboard with all the insights pre-computed

---

### Flow 2: Asking a Question (Q&A Chat)

```
 ┌──────┐  ① "Which supplier       ┌────────────┐       ┌───────────┐
 │ User │     has the most   ──▶   │ App Server  │       │  AI Model │
 │      │     delays?"              │             │       │           │
 │      │                           │ ② Build a   │       │           │
 │      │                           │ searchable   │       │           │
 │      │                           │ knowledge    │       │           │
 │      │                           │ base from    │       │           │
 │      │                           │ all data     │       │           │
 │      │                           │     │        │       │           │
 │      │                           │     ▼        │       │           │
 │      │                           │ ③ Find the   │       │           │
 │      │                           │ most relevant │      │           │
 │      │                           │ data snippets │      │           │
 │      │                           │ (RAG search)  │      │           │
 │      │                           │     │        │       │           │
 │      │                           │     ▼        │       │           │
 │      │                           │ ④ Send question ──▶ │           │
 │      │                           │   + relevant data    │ ⑤ Generate│
 │      │                           │                      │   answer  │
 │      │                           │ ⑥ Receive     ◀──── │   using   │
 │      │                           │   AI answer   │      │   context │
 │      │                           │     │         │      └───────────┘
 │      │                           │     ▼         │
 │      │                           │ ⑦ Validate:   │
 │      │                           │ • Are IDs real?│
 │      │                           │ • Are facts   │
 │      │                           │   grounded?   │
 │      │                           │     │         │
 │      │  ⑧ Display verified      │     ▼         │
 │      │ ◀──── answer + sources── │ ⑧ Return      │
 └──────┘                           └────────────┘

         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
         If AI is unavailable or gives a bad answer:
         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

 ┌──────┐                           ┌────────────┐
 │ User │                           │ App Server  │
 │      │                           │             │
 │      │                           │ Falls back  │
 │      │  Answer from built-in     │ to built-in │
 │      │ ◀──── rule engine ─────── │ Q&A rules   │
 └──────┘                           └────────────┘
```

**In plain English:**
1. You type a question like *"Which supplier has the most delays?"*
2. The server converts all supply chain data into a searchable knowledge base
3. It finds the **most relevant** data snippets for your question (this is "RAG" — Retrieval-Augmented Generation)
4. It sends your question **plus the relevant data** to the AI model
5. The AI generates a natural-language answer grounded in real data
6. The server **validates** the answer — checking that every supplier ID, shipment ID, and fact is real
7. If the AI is unavailable or gives a questionable answer, a **built-in rule engine** provides the answer instead
8. You see the verified answer along with the data sources it used

---

## 🧩 Component Summary

| Component | What It Does | Technology |
|---|---|---|
| **Dashboard UI** | Displays all insights in an interactive web page | HTML, CSS, JavaScript |
| **App Server** | The "brain" — runs all analysis and coordinates everything | Python (Flask) |
| **Risk Detection** | Scans news for geopolitical events, flags affected shipments | Python logic |
| **Alternative Sourcing** | Recommends safer suppliers outside blocked countries | Python logic |
| **RAG Search** | Finds the most relevant data to answer each question | TF-IDF (scikit-learn) |
| **AI Model (LLM)** | Generates natural-language answers from data context | Mistral (local, optional) |
| **Validation Layer** | Fact-checks AI answers against real data | Python logic |
| **Fallback Q&A** | Answers questions using rules when AI is unavailable | Python logic |
| **Data Files** | Synthetic supply chain data (news, suppliers, shipments, performance) | JSON files |

---

## 🛡️ Key Design Principles

1. **AI with guardrails** — The AI never answers in a vacuum. It only sees real data, and its answers are validated before reaching the user.

2. **Always available** — Even without the AI model running, the dashboard and Q&A still work using built-in rules.

3. **Transparent sourcing** — Every AI answer shows which data sources it used, so users can verify the reasoning.

4. **Self-contained** — All data is local (JSON files). No external databases or cloud services required for the core experience.

---

## 🌐 Deployment Overview

```
Your Computer
├── Python App Server (port 8000) ─── serves the dashboard
├── Local AI Model (port 8085) ─────── optional, for smarter Q&A
└── Data Files (data/) ─────────────── all supply chain information
```

> **To run:** Start the app with `python app.py` and open `http://localhost:8000` in your browser.  
> The AI model is **optional** — the system works without it using the built-in fallback engine.
