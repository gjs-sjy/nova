# Codebase X-Ray

**An X-ray machine for unfamiliar code.** Upload a Python project, and Codebase X-Ray reconstructs its architecture: every function, every call, every dependency. Using an AI API, it explains each function and answers the important question: if I change or delete this, what breaks?

---

## The problem
Every CS student has been handed a 30-file starter codebase with the instruction "implement the missing function." Every developer joining a new team faces the same wall. You don't know where anything is, what calls what, or what you'll break if you touch something. Reading files one by one takes hours.

## What it does
- **Reconstructs the architecture.** Upload a ZIP and get an interactive graph of every function and the calls between them.
- **Finds entry points and dead code.** Entry points (like `main`) are outlined in green. Functions nothing ever calls are outlined in red.
- **Click to inspect.** Click any function to see its source code, what it calls, and what calls it.
- **Shows the blast radius.** Ask "What breaks if I delete this?" and every directly and indirectly affected function lights up.
- **Explains it in plain English.** An AI assistant explains what a function does and what deleting it would affect, grounded in the computed graph.

## How it's different
Most AI code tools paste your code into a chatbot and hope the answer is right. **Codebase X-Ray computes first, then explains:**

1. **Python's `ast` module** parses the code structure without ever running it.
2. **NetworkX** builds a directed dependency graph. "What breaks" is exactly the set of a function's *ancestors* in that graph.
3. **The AI only explains** facts the graph already proved, and flags uncertainty (dynamic calls, decorators) instead of inventing dependencies.

Command-line tools like [pyan3](https://pypi.org/project/pyan3/) and [code2flow](https://pypi.org/project/code2flow/) generate static call-graph images, and [DeepWiki](https://deepwiki.com) generates AI documentation for GitHub repos. Codebase X-Ray combines real static analysis with an interactive, browser-based explorer and grounded AI explanations. It works on any ZIP, including course starter code that isn't on GitHub, with no install needed by the end user.

## How it works
```
ZIP upload ──► FastAPI ──► AST parser ──► NetworkX graph ──► JSON ──► React Flow graph
                                               │
                                               └──► impact analysis ──► OpenRouter LLM ──► plain-English explanation
```

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Graph visualization | React Flow (`@xyflow/react`) + dagre layout |
| Backend | Python + FastAPI |
| Code parsing | Python `ast` (static analysis, code is never executed) |
| Graph engine | NetworkX |
| AI explanations | OpenRouter API |

### API endpoints
| Endpoint | Purpose |
|---|---|
| `POST /upload` | Upload a ZIP, then parse, build the graph, and return nodes, edges, and stats |
| `POST /impact` | Given a function ID, return direct callers, all affected functions, and affected files |
| `POST /explain` | Given a function ID and mode (`explain` or `impact`), return an AI explanation |

---

## Running it locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- An [OpenRouter](https://openrouter.ai) API key (only needed for the AI explanations)

### 1. Backend
```bash
cd codebase-xray/backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then add your OpenRouter key and model to .env
uvicorn main:app --reload --port 8000
```
API docs are available at http://localhost:8000/docs.

### 2. Frontend (in a second terminal)
```bash
cd codebase-xray/frontend
npm install
npm run dev
```
Open http://localhost:5173.

### 3. Try it
Upload `codebase-xray/sample_project.zip`. You should see:
- `main` → `login`, `process_payment`
- `login` → `get_user`
- `process_payment` → `calculate_total`
- `main` marked as an **entry point**, and `unused_function` flagged as **unused**

Click `calculate_total` and choose **"What breaks if I delete this?"** It highlights `process_payment` (direct) and `main` (indirect).

---

## Limitations (we're honest about these)
- **Python only.** Other languages need a different parser.
- **Static analysis is an estimate, not a guarantee.** Dynamic calls, reflection, decorators, and plugin systems can hide dependencies.
- **Method calls are matched by name.** Ambiguous calls such as `obj.save()` with several `save` methods are skipped rather than guessed.
- **Projects are stored in memory**, so they're lost when the server restarts.

## What's next
- Support for JavaScript and C++ (via tree-sitter)
- "Execution path" view: trace the route from `main` to any function
- Run automatically on pull requests to show the blast radius of every change
- File-level view and circular-dependency detection

---

## Team
Built in 6 hours at NOVA.

- **[Yining Tang]**: parser (AST extraction)
- **[Aahana Jain]**: graph engine and API
- **[Herbert Qin]**: frontend and visualization
- **[Grace Shen]**: AI integration and demo

*AI coding assistants were used during development.*