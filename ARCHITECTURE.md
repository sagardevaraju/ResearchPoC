# GeoSupply Copilot — System Architecture & Data Flow# GeoSupply Copilot — System Architecture & Data Flow



> A high-level overview of how the system works, designed for non-technical audiences.> A high-level overview of how the system works, designed for non-technical audiences.



------



## 🏗️ System Architecture## 🏗️ System Architecture



The system has three layers: the **Dashboard** (what users see), the **Application Server** (the brain that runs all analysis), and the **Data & AI Layer** (where information and intelligence live).```

┌─────────────────────────────────────────────────────────────────────┐

```│                          USER (Web Browser)                         │

╔═══════════════════════════════════════════════════════════════════╗│                                                                     │

║                      USER  (Web Browser)                         ║│  ┌───────────────────────────────────────────────────────────────┐  │

║                                                                  ║│  │               GeoSupply Copilot Dashboard                     │  │

║   ┌──────────────┐ ┌──────────────┐ ┌────────────────────────┐  ║│  │                                                               │  │

║   │ Trade-Block   │ │  Shipment    │ │    Risk Alerts         │  ║│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐  │  │

║   │  Scenario     │ │  Health      │ │                        │  ║│  │  │ Trade    │ │ Shipment │ │ Risk      │ │ Alternate     │  │  │

║   └──────────────┘ └──────────────┘ └────────────────────────┘  ║│  │  │ Block    │ │ Health   │ │ Alerts    │ │ Sourcing      │  │  │

║   ┌──────────────┐ ┌────────────────────────────────────────┐   ║│  │  │ Scenario │ │ Overview │ │           │ │ Suggestions   │  │  │

║   │  Alternate    │ │  Q&A Chat                             │   ║│  │  └──────────┘ └──────────┘ └───────────┘ └───────────────┘  │  │

║   │  Sourcing     │ │  (ask questions in plain English)     │   ║│  │                                                               │  │

║   └──────────────┘ └────────────────────────────────────────┘   ║│  │  ┌────────────────────────────────────────────────────────┐  │  │

║   ┌─────────────────────────┐ ┌─────────────────────────────┐   ║│  │  │          Q&A Chat (Ask questions in plain English)      │  │  │

║   │  Shipment Details       │ │  Supplier Details            │   ║│  │  └────────────────────────────────────────────────────────┘  │  │

║   └─────────────────────────┘ └─────────────────────────────┘   ║│  │                                                               │  │

╚════════════════════════════════╤══════════════════════════════════╝│  │  ┌──────────────────────┐  ┌──────────────────────────────┐  │  │

                                 ││  │  │  Shipment Details    │  │  Supplier Details             │  │  │

                     User opens website│  │  │  (click to explore)  │  │  (click to explore)           │  │  │

                      or asks a question│  │  └──────────────────────┘  └──────────────────────────────┘  │  │

                                 ││  └───────────────────────────────────────────────────────────────┘  │

                                 ▼└──────────────────────────────┬──────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════╗                               │

║                   APPLICATION SERVER  (Python)                    ║                     User opens website /

║                                                                  ║                     asks a question

║   ┌──────────────────┐      ┌─────────────────────────────────┐  ║                               │

║   │ Risk Detection    │      │ Smart Q&A                       │  ║                               ▼

║   │                   │      │                                 │  ║┌─────────────────────────────────────────────────────────────────────┐

║   │ • Scans news for  │      │  Primary: AI-powered answers    │  ║│                      APPLICATION SERVER (Flask)                      │

║   │   trade-block     │      │  using RAG to stay grounded     │  ║│                         (app.py · Python)                            │

║   │   events          │      │  in real data                   │  ║│                                                                      │

║   │ • Flags at-risk   │      │                                 │  ║│  ┌────────────────────────────────────────────────────────────────┐  │

║   │   shipments       │      │  Fallback: Built-in rule        │  ║│  │                    Core Intelligence Engines                   │  │

║   │ • Assigns         │      │  engine if AI is unavailable    │  ║│  │                                                                │  │

║   │   severity        │      │                                 │  ║│  │  ┌─────────────────┐    ┌──────────────────────────────────┐  │  │

║   └──────────────────┘      └─────────────────────────────────┘  ║│  │  │ Risk Detection  │    │ Smart Q&A (two approaches)       │  │  │

║   ┌──────────────────┐      ┌─────────────────────────────────┐  ║│  │  │                 │    │                                    │  │  │

║   │ Alternative       │      │ RAG Pipeline                    │  ║│  │  │ • Scans news    │    │  1. AI Model (Mistral LLM)       │  │  │

║   │ Sourcing          │      │ (Retrieval-Augmented            │  ║│  │  │   for trade     │    │     ↕ Uses RAG to ground         │  │  │

║   │                   │      │  Generation)                    │  ║│  │  │   block events  │    │       answers in real data        │  │  │

║   │ • Finds safe      │      │                                 │  ║│  │  │ • Matches at-   │    │                                    │  │  │

║   │   suppliers       │      │ • Turns all data into           │  ║│  │  │   risk shipments│    │  2. Built-in Fallback Engine      │  │  │

║   │   outside blocked │      │   searchable documents          │  ║│  │  │ • Flags alerts  │    │     ↕ Rule-based answers if       │  │  │

║   │   countries       │      │ • Finds the most relevant       │  ║│  │  │   by severity   │    │       AI is unavailable            │  │  │

║   │ • Ranks by        │      │   snippets per question         │  ║│  │  └─────────────────┘    └──────────────────────────────────┘  │  │

║   │   performance     │      │ • Feeds context to AI so        │  ║│  │                                                                │  │

║   │                   │      │   answers stay accurate         │  ║│  │  ┌─────────────────┐    ┌──────────────────────────────────┐  │  │

║   └──────────────────┘      └─────────────────────────────────┘  ║│  │  │ Alternative     │    │ RAG Pipeline                      │  │  │

║   ┌───────────────────────────────────────────────────────────┐   ║│  │  │ Sourcing        │    │ (Retrieval-Augmented Generation)  │  │  │

║   │ Safety & Validation Layer                                  │   ║│  │  │                 │    │                                    │  │  │

║   │ • Checks AI answers against real data (no made-up facts)   │   ║│  │  │ • Finds safe    │    │ • Converts all data into          │  │  │

║   │ • Verifies every supplier/shipment ID actually exists      │   ║│  │  │   suppliers     │    │   searchable text documents        │  │  │

║   │ • Falls back to rule engine if AI gives a bad answer       │   ║│  │  │   outside       │    │ • Finds the most relevant          │  │  │

║   └───────────────────────────────────────────────────────────┘   ║│  │  │   blocked       │    │   snippets for each question       │  │  │

╚════════════════╤══════════════════════════════╤═══════════════════╝│  │  │   countries     │    │ • Feeds context to the AI          │  │  │

                 │                              ││  │  │ • Ranks by      │    │   so it answers accurately         │  │  │

                 ▼                              ▼│  │  │   performance   │    │                                    │  │  │

╔════════════════════════════╗   ╔══════════════════════════════════╗│  │  └─────────────────┘    └──────────────────────────────────┘  │  │

║     DATA LAYER             ║   ║     AI LAYER (Optional)          ║│  │                                                                │  │

║     (JSON Files)           ║   ║                                  ║│  │  ┌──────────────────────────────────────────────────────────┐  │  │

║                            ║   ║  Any LLM that exposes an         ║│  │  │ Safety & Validation Layer                                 │  │  │

║  📰 News                   ║   ║  OpenAI-compatible chat API      ║│  │  │ • Checks AI answers against real data (no hallucinations) │  │  │

║  Geopolitical events       ║   ║                                  ║│  │  │ • Verifies supplier/shipment IDs actually exist           │  │  │

║  & trade blocks            ║   ║  Examples:                       ║│  │  │ • Falls back to built-in engine if AI gives bad answers   │  │  │

║                            ║   ║  • Local model via Ollama        ║│  │  └──────────────────────────────────────────────────────────┘  │  │

║  🏭 Suppliers              ║   ║    or LM Studio                  ║│  └────────────────────────────────────────────────────────────────┘  │

║  Who they are &            ║   ║  • Cloud-hosted model endpoint   ║└──────────┬────────────────────────────────┬─────────────────────────┘

║  where they operate        ║   ║  • Any OpenAI-compatible API     ║           │                                │

║                            ║   ║                                  ║           ▼                                ▼

║  🚢 Shipments              ║   ║  Configured via environment      ║┌─────────────────────┐        ┌─────────────────────────┐

║  What's moving, from       ║   ║  variables — swap models         ║│   DATA LAYER        │        │   AI MODEL              │

║  where, and delays         ║   ║  without changing code           ║│   (JSON Files)      │        │                          │

║                            ║   ║                                  ║│                     │        │   Local LLM              │

║  📊 Performance            ║   ╚══════════════════════════════════╝│  ┌───────────────┐  │        │   running on your        │

║  How reliable each         ║│  │ 📰 News       │  │        │   machine via            │

║  supplier has been         ║│  │ Geopolitical  │  │        │   OpenAI-compatible API   │

╚════════════════════════════╝│  │ events &      │  │        │                          │

```│  │ trade blocks  │  │        │   (http://localhost:8085) │

│  └───────────────┘  │        └─────────────────────────┘

---│  ┌───────────────┐  │

│  │ 🏭 Suppliers  │  │

## 🔄 Data Flow — What Happens When You Use the Dashboard│  │ Who they are, │  │

│  │ where they're │  │

### Flow 1: Opening the Dashboard│  │ located       │  │

│  └───────────────┘  │

```│  ┌───────────────┐  │

  ┌──────┐                              ┌─────────────┐│  │ 🚢 Shipments  │  │

  │      │  ①  Open website             │             ││  │ What's moving,│  │

  │ User │ ───────────────────────────▶ │ App Server  ││  │ from where,   │  │

  │      │                              │             ││  │ delays        │  │

  │      │                              │ ② Load all  ││  └───────────────┘  │

  │      │                              │    data     ││  ┌───────────────┐  │

  │      │                              │      │      ││  │ 📊 Performance│  │

  │      │                              │      ▼      ││  │ How reliable  │  │

  │      │                              │ ③ Analyze   ││  │ each supplier │  │

  │      │                              │   • Detect  ││  │ has been      │  │

  │      │                              │     trade   ││  └───────────────┘  │

  │      │                              │     blocks  │└─────────────────────┘

  │      │                              │   • Flag    │```

  │      │                              │     at-risk │

  │      │                              │     items   │---

  │      │                              │   • Find    │

  │      │                              │     safer   │## 🔄 Data Flow — What Happens When You Use the Dashboard

  │      │                              │     sources │

  │      │                              │   • Build   │### Flow 1: Opening the Dashboard (viewing the page)

  │      │  ④  Complete dashboard       │     health  │

  │      │ ◀─────────────────────────── │     summary │```

  └──────┘     with all insights        └─────────────┘ ┌──────┐       ① Open website        ┌────────────┐

``` │ User │ ─────────────────────────▶  │ App Server  │

 │      │                              │             │

**In plain English:** │      │                              │  ② Load all │

1. You open the website in your browser. │      │                              │  data files │

2. The server reads all supply-chain data (news, suppliers, shipments, performance). │      │                              │      │      │

3. It runs analysis — detecting risks, flagging affected shipments, and finding alternatives. │      │                              │      ▼      │

4. It sends back a complete dashboard with all insights ready to view. │      │                              │  ③ Analyze: │

 │      │                              │  • Detect   │

--- │      │                              │    trade    │

 │      │                              │    blocks   │

### Flow 2: Asking a Question (Q&A Chat) │      │                              │  • Flag     │

 │      │                              │    at-risk  │

``` │      │                              │    shipments│

  ┌──────┐   ① "Which supplier       ┌─────────────┐      ┌──────────┐ │      │                              │  • Find     │

  │      │      has the most   ──▶   │             │      │          │ │      │                              │    safer    │

  │ User │      delays?"              │ App Server  │      │ AI Model │ │      │                              │    suppliers│

  │      │                            │             │      │(any LLM) │ │      │                              │  • Summarize│

  │      │                            │ ② Build a   │      │          │ │      │   ④ Send complete dashboard  │    shipment │

  │      │                            │   knowledge │      │          │ │      │ ◀──────────────────────────  │    health   │

  │      │                            │   base from │      │          │ └──────┘     with all insights        └────────────┘

  │      │                            │   all data  │      │          │```

  │      │                            │      │      │      │          │

  │      │                            │      ▼      │      │          │**In plain English:**

  │      │                            │ ③ Find the  │      │          │1. You open the website in your browser

  │      │                            │   most      │      │          │2. The server reads all the supply chain data (news, suppliers, shipments, performance)

  │      │                            │   relevant  │      │          │3. It runs analysis to detect risks, flag affected shipments, and suggest alternatives

  │      │                            │   snippets  │      │          │4. It sends back a complete dashboard with all the insights pre-computed

  │      │                            │      │      │      │          │

  │      │                            │      ▼      │      │          │---

  │      │                            │ ④ Question  │      │          │

  │      │                            │   + context ──────▶│ ⑤ Answer │### Flow 2: Asking a Question (Q&A Chat)

  │      │                            │             │      │   using  │

  │      │                            │ ⑥ Receive  ◀────── │   data   │```

  │      │                            │   answer    │      │          │ ┌──────┐  ① "Which supplier       ┌────────────┐       ┌───────────┐

  │      │                            │      │      │      └──────────┘ │ User │     has the most   ──▶   │ App Server  │       │  AI Model │

  │      │                            │      ▼      │ │      │     delays?"              │             │       │           │

  │      │                            │ ⑦ Validate  │ │      │                           │ ② Build a   │       │           │

  │      │                            │   • IDs     │ │      │                           │ searchable   │       │           │

  │      │                            │     real?   │ │      │                           │ knowledge    │       │           │

  │      │                            │   • Facts   │ │      │                           │ base from    │       │           │

  │      │   ⑧ Verified answer        │     match?  │ │      │                           │ all data     │       │           │

  │      │ ◀───── + sources ───────── │             │ │      │                           │     │        │       │           │

  └──────┘                            └─────────────┘ │      │                           │     ▼        │       │           │

 │      │                           │ ③ Find the   │       │           │

       ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │      │                           │ most relevant │      │           │

       If AI is unavailable or returns a bad answer: │      │                           │ data snippets │      │           │

       ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │      │                           │ (RAG search)  │      │           │

 │      │                           │     │        │       │           │

  ┌──────┐                            ┌─────────────┐ │      │                           │     ▼        │       │           │

  │ User │  Answer from built-in      │ App Server  │ │      │                           │ ④ Send question ──▶ │           │

  │      │ ◀──── rule engine ──────── │ (fallback)  │ │      │                           │   + relevant data    │ ⑤ Generate│

  └──────┘                            └─────────────┘ │      │                           │                      │   answer  │

``` │      │                           │ ⑥ Receive     ◀──── │   using   │

 │      │                           │   AI answer   │      │   context │

**In plain English:** │      │                           │     │         │      └───────────┘

1. You type a question like *"Which supplier has the most delays?"* │      │                           │     ▼         │

2. The server converts all supply-chain data into a searchable knowledge base. │      │                           │ ⑦ Validate:   │

3. It finds the **most relevant** data snippets for your question (this is called "RAG"). │      │                           │ • Are IDs real?│

4. It sends your question **plus the relevant data** to the AI model. │      │                           │ • Are facts   │

5. The AI generates a natural-language answer grounded in real data. │      │                           │   grounded?   │

6. The server **validates** the answer — checking that every ID and fact is real. │      │                           │     │         │

7. If the AI is unavailable or gives a questionable answer, a **built-in rule engine** provides the answer instead. │      │  ⑧ Display verified      │     ▼         │

8. You see the verified answer along with the data sources it used. │      │ ◀──── answer + sources── │ ⑧ Return      │

 └──────┘                           └────────────┘

---

         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

## 🧩 Component Summary         If AI is unavailable or gives a bad answer:

         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

| Component | What It Does | Technology |

|---|---|---| ┌──────┐                           ┌────────────┐

| **Dashboard UI** | Displays all insights in an interactive web page | HTML, CSS, JavaScript | │ User │                           │ App Server  │

| **App Server** | The "brain" — runs all analysis and coordinates everything | Python (Flask) | │      │                           │             │

| **Risk Detection** | Scans news for geopolitical events, flags affected shipments | Python logic | │      │                           │ Falls back  │

| **Alternative Sourcing** | Recommends safer suppliers outside blocked countries | Python logic | │      │  Answer from built-in     │ to built-in │

| **RAG Search** | Finds the most relevant data to answer each question | TF-IDF (scikit-learn) | │      │ ◀──── rule engine ─────── │ Q&A rules   │

| **AI Model** | Generates natural-language answers from data context | Any OpenAI-compatible LLM | └──────┘                           └────────────┘

| **Validation Layer** | Fact-checks AI answers against real data | Python logic |```

| **Fallback Q&A** | Answers questions using rules when AI is unavailable | Python logic |

| **Data Files** | Synthetic supply-chain data (news, suppliers, shipments, performance) | JSON files |**In plain English:**

1. You type a question like *"Which supplier has the most delays?"*

---2. The server converts all supply chain data into a searchable knowledge base

3. It finds the **most relevant** data snippets for your question (this is "RAG" — Retrieval-Augmented Generation)

## 🛡️ Key Design Principles4. It sends your question **plus the relevant data** to the AI model

5. The AI generates a natural-language answer grounded in real data

1. **Model-agnostic** — The system works with any Large Language Model that provides an OpenAI-compatible chat API. Swap models by changing an environment variable — no code changes required.6. The server **validates** the answer — checking that every supplier ID, shipment ID, and fact is real

7. If the AI is unavailable or gives a questionable answer, a **built-in rule engine** provides the answer instead

2. **AI with guardrails** — The AI never answers in a vacuum. It only sees real data, and its answers are validated before reaching the user.8. You see the verified answer along with the data sources it used



3. **Always available** — Even without any AI model running, the dashboard and Q&A still work using built-in rules.---



4. **Transparent sourcing** — Every AI answer shows which data sources it used, so users can verify the reasoning.## 🧩 Component Summary



5. **Self-contained** — All data is local (JSON files). No external databases or cloud services required for the core experience.| Component | What It Does | Technology |

|---|---|---|

---| **Dashboard UI** | Displays all insights in an interactive web page | HTML, CSS, JavaScript |

| **App Server** | The "brain" — runs all analysis and coordinates everything | Python (Flask) |

## 🌐 Deployment Overview| **Risk Detection** | Scans news for geopolitical events, flags affected shipments | Python logic |

| **Alternative Sourcing** | Recommends safer suppliers outside blocked countries | Python logic |

```| **RAG Search** | Finds the most relevant data to answer each question | TF-IDF (scikit-learn) |

Your Computer (or Server)| **AI Model (LLM)** | Generates natural-language answers from data context | Mistral (local, optional) |

├── Python App Server (port 8000) ──── serves the dashboard| **Validation Layer** | Fact-checks AI answers against real data | Python logic |

├── AI Model endpoint (configurable) ── optional, for smarter Q&A| **Fallback Q&A** | Answers questions using rules when AI is unavailable | Python logic |

│   (any OpenAI-compatible API)| **Data Files** | Synthetic supply chain data (news, suppliers, shipments, performance) | JSON files |

└── Data Files (data/) ──────────────── all supply-chain information

```---



> **To run:** Start the app with `python app.py` and open `http://localhost:8000` in your browser.## 🛡️ Key Design Principles

> The AI model is **optional** — the system works without it using the built-in fallback engine.

> Configure the AI endpoint via environment variables `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`.1. **AI with guardrails** — The AI never answers in a vacuum. It only sees real data, and its answers are validated before reaching the user.


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
