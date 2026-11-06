# SENTINEL X — Interactive Regex-Based Cybersecurity Threat Detection & Automata Visualization Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=for-the-badge&logo=render)](https://sentinel-x-cybersecurity.onrender.com/)

🔗 **Live Application:** [https://sentinel-x-cybersecurity.onrender.com/](https://sentinel-x-cybersecurity.onrender.com/)

---

**Student PRN:** `202401110046`  
**Assigned Application Domain:** Cybersecurity  
**Core Academic Concepts:** Regular Expressions (RE), Nondeterministic Finite Automata (NFA), Deterministic Finite Automata (DFA), Thompson's Construction, Subset Construction, DFA Minimization (Partition Refinement), Regular Languages, Chomsky Hierarchy, Cybersecurity Pattern Detection.

---

## 1. Project Overview & Objectives

**SENTINEL X** is a web-based threat intelligence and formal language visualization platform. It connects practical cybersecurity defense (pattern matching against SQL Injection, Script Injection, Path Traversal, Command Injection, and Phishing URLs) with theoretical foundations from the Theory of Computation (ToC).

### Core Objectives:
1. **Practical Threat Detection:** Apply regular expressions to analyze suspect strings, URLs, shell commands, and payloads in real time.
2. **Deterministic Automata Synthesis:** Parse regular expressions and compile them into $\epsilon$-NFAs using **Thompson's Construction**.
3. **Power-Set Determinization:** Convert NFAs into DFAs using **Subset Construction** with explicit dead/trap state handling.
4. **State Machine Optimization:** Minimize DFAs using **Hopcroft's Partition-Refinement Algorithm** to eliminate redundant states.
5. **Interactive Execution Simulation:** Animate state transitions step-by-step across input strings $w \in \Sigma^*$ with visual graph highlighting.

---

## 2. Technology Stack

- **Backend:** Python 3.13, Flask 3.1 REST API, Python standard `re` module.
- **Automata Engine:** Pure Python algorithms (no external AI services, no third-party automata libraries):
  - Infix-to-postfix Shunting-Yard tokenizer with explicit concatenation insertion.
  - Thompson's Construction ($\epsilon$-NFA generator).
  - Subset Construction with $\epsilon$-closure computation.
  - Partition Refinement DFA minimization.
  - Step-by-step deterministic string simulator.
- **Frontend:** Semantic HTML5, CSS3 Custom Cyber Design System, Vanilla JavaScript (ES6+).
- **Visualization:**
  - **Cytoscape.js** for interactive directed graph visualization (pan, zoom, layout, state highlights).
  - **Chart.js** for telemetry dashboards (verdicts, category distribution, latency).
- **Storage:** Local Browser `localStorage` and `sessionStorage` for scan telemetry persistence.

---

## 3. Five Cybersecurity Detection Rules

| Rule ID | Category | Configured Regex Pattern | Threat Purpose & MITRE ID |
| :--- | :--- | :--- | :--- |
| **RULE-01** | SQL Injection | `(?i)(union\s+select\|or\s+1=1\|drop\s+table)` | Detects UNION extraction, tautology bypass (`or 1=1`), and DDL destruction (CWE-89 / T1190). |
| **RULE-02** | Script Injection (XSS) | `(?i)(<script\|javascript:\|onerror\s*=)` | Detects HTML tags, DOM event handlers, and script URI execution schemes (CWE-79 / T1059.007). |
| **RULE-03** | Directory Traversal | `(\.\./\|\.\.\\)` | Detects Unix (`../`) and Windows (`..\`) parent directory traversal attempts (CWE-22 / T1083). |
| **RULE-04** | Command Injection | `(?i)(rm\s+-rf\|powershell\s+-enc\|cmd\.exe)` | Flags destructive Unix deletion, base64-encoded PowerShell, and Windows shell calls (CWE-78 / T1059). |
| **RULE-05** | Phishing / Malicious URL | `(?i)(https?://[^\s]*(login\|verify\|secure)[^\s]*)` | Detects URLs embedding sensitive authentication keywords in domains or query parameters (CWE-20 / T1566.002). |

> **Academic Disclaimer:** These patterns are educational detection indicators. A regex match flags a suspicious indicator rather than proof of an exploit, and a non-match does not prove that an input is benign.

---

## 4. Automata Theory & Implementation Mechanics

### A. Thompson's Construction ($RE \to NFA$)
The engine transforms a regular expression into an equivalent $\epsilon$-NFA:
- **Base symbol $a$:** $s_0 \xrightarrow{a} s_1$
- **Concatenation $AB$:** Connects $accept(A) \xrightarrow{\epsilon} start(B)$
- **Alternation $A \mid B$:** Creates new start $S$ with $\epsilon \to start(A), start(B)$ and new accept $F$ with $\epsilon$ from $accept(A), accept(B)$
- **Kleene Star $A^*$:** Adds bypass $S \xrightarrow{\epsilon} F$, forward $\epsilon \to start(A)$, and feedback $accept(A) \xrightarrow{\epsilon} start(A)$

### B. Subset Construction ($NFA \to DFA$)
Computes the power-set representation:
1. $D_0 = \epsilon\text{-closure}(\{nfa.start\_state\})$
2. For each DFA state $S$ and symbol $c \in \Sigma$:
   $$\text{move}(S, c) = \bigcup_{s \in S} \{ s' \mid (s \xrightarrow{c} s') \in NFA \}$$
   $$\text{next\_state} = \epsilon\text{-closure}(\text{move}(S, c))$$
3. Identifies accepting states if $S \cap nfa.accept\_states \neq \emptyset$.
4. **Dead / Trap State:** If $\text{move}(S, c) = \emptyset$, transitions map to a non-accepting `DEAD` state where $\delta(DEAD, c) = DEAD$ for all $c \in \Sigma$.

### C. DFA Minimization (Partition Refinement)
Based on the Myhill-Nerode theorem:
1. Initial partition: $P_0 = [F, Q \setminus F]$ (Accepting vs Non-accepting).
2. Iteratively splits each group $G$ based on the transition signature:
   $$\text{sig}(q) = (\text{group}(\delta(q, c_1)), \dots, \text{group}(\delta(q, c_k)))$$
3. Replaces equivalent state groups with unique minimal quotient states ($M_0, M_1, \dots$).

---

## 5. Project Directory Structure

```
sentinel-x/
│
├── app.py                      # Flask Application Server & REST Endpoints
├── requirements.txt            # Python Dependencies (Flask, Pytest)
├── README.md                   # Comprehensive Technical & Academic Documentation
│
├── backend/
│   ├── __init__.py             # Package Initializer
│   ├── detection_rules.py      # 5 Cybersecurity Rule Definitions & Test Cases
│   ├── regex_engine.py         # Threat Scanning, Highlight Spans & Timing Engine
│   ├── regex_parser.py         # Shunting-Yard AST & Explicit Concat Tokenizer
│   ├── thompson_nfa.py         # Thompson's Construction NFA Generator
│   ├── subset_construction.py  # Subset Construction (NFA to DFA) with Dead State
│   ├── dfa_minimization.py     # Partition Refinement DFA Minimization Algorithm
│   └── simulator.py            # Step-by-Step Deterministic Trace Engine
│
├── templates/
│   ├── base.html               # Shared Cyber Dark Navy Base Layout
│   ├── index.html              # Phase 1: Landing Page
│   ├── scanner.html            # Phase 2: Threat Intelligence Scanner
│   ├── dashboard.html          # Phase 4: Telemetry Analysis Dashboard
│   ├── regex_lab.html          # Phase 5: Regex Laboratory & Rule Suite
│   ├── automata.html           # Phases 6 & 7: Automata Studio (NFA, DFA, Min)
│   ├── simulator.html          # Phase 8: Interactive DFA String Simulator
│   └── about.html              # Phase 9: Academic Documentation & Report
│
├── static/
│   ├── css/
│   │   └── style.css           # Premium Dark Navy Cybersecurity Design System
│   ├── js/
│   │   ├── main.js             # Cyber Canvas, Toasts, LocalStorage Telemetry
│   │   ├── scanner.js          # Scanner Controller & Quick Preview
│   │   ├── dashboard.js        # Chart.js Visualizations & History Inspector
│   │   ├── regex_lab.js        # Regex Tester & Rule Benchmark Suite Runner
│   │   ├── automata.js         # Cytoscape Graph & Transition Table Switcher
│   │   └── simulator.js        # Interactive Step-by-Step State Highlighting
│   └── vendor/
│       ├── cytoscape.min.js    # Self-Contained Graph Visualizer
│       └── chart.umd.min.js    # Self-Contained Chart Engine
│
└── tests/
    ├── __init__.py
    ├── test_regex.py           # Unit Tests: 5 Rules, 50 Test Cases, ReDoS
    ├── test_nfa.py             # Unit Tests: Thompson's Construction
    ├── test_dfa.py             # Unit Tests: Subset Construction & Dead State
    ├── test_minimization.py    # Unit Tests: Partition Refinement & Simulation
    └── test_api_integration.py# Integration Tests: All Flask Routes & REST Endpoints
```

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.13.2)
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### Step 1: Clone or Navigate to the Workspace
```bash
cd d:\SENTINEL-X
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Automated Tests
```bash
python -m pytest tests/ -v
```
*Expected: 42 passed in ~1.5 seconds.*

### Step 4: Launch the SENTINEL X Server
```bash
python app.py
```

### Step 5: Open in Your Web Browser
Visit:
```
http://127.0.0.1:5000
```

---

## 7. REST API Reference

| Endpoint | Method | Request Payload | Response Description |
| :--- | :--- | :--- | :--- |
| `/api/health` | GET | None | System status, PRN, and timestamp |
| `/api/rules` | GET | `?category=...` | All 5 detection rules and metadata |
| `/api/scan` | POST | `{"text": "...", "category": "all"}` | Matched rules, highlighted spans, execution latency |
| `/api/regex/test` | POST | `{"pattern": "...", "text": "..."}` | Custom regex matches, positions, ReDoS check |
| `/api/automata/nfa` | POST | `{"pattern": "(a\|b)*c"}` | Thompson NFA states, transition table, Cytoscape graph |
| `/api/automata/dfa` | POST | `{"pattern": "...", "include_dead_state": true}` | Subset DFA, initial state, accept states, trap state |
| `/api/automata/minimize`| POST | `{"pattern": "..."}` | Minimized DFA, reduction statistics, equivalence groups |
| `/api/automata/simulate`| POST | `{"pattern": "...", "input_string": "abbc"}` | Step-by-step transition trace, verdict, explanation |

---

## 8. Verification & Test Evidence

SENTINEL X has been verified across 42 automated test cases:
1. **Rule Verification:** 5 matching strings and 5 non-matching strings tested for each of the 5 rules (50 test strings total).
2. **Determinism Verification:** Tested that all subset-constructed DFAs possess at most one transition per (state, symbol) pair.
3. **Dead State Verification:** Verified that missing transitions correctly enter the non-accepting sink state and self-loop.
4. **Minimization Equivalence:** Verified that the minimized DFA accepts the exact same language as the un-minimized DFA.
5. **Simulator Verification:** Tested acceptance on matching strings, rejection on non-matching strings, and error handling for unrecognized alphabet symbols.

---

## 9. Academic Evaluation Certification

- **Student PRN:** `202401110046`
- **Course:** Theory of Computation
- **Project Domain:** Cybersecurity Threat Detection
- **Submission Date:** October 31, 2026
- **Status:** Complete, Tested, and Verified
