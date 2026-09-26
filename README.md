# Devplus

> Agentic Local Setup & Bug Diagnostics

DevPulse is a local-first developer reliability agent that detects,
diagnoses, and safely repairs application startup failures.

It uses a local Ollama LLM for diagnosis and deterministic Python
fixers for controlled repair.

## ✨ Features

- 🔍 Automatic project scanning
- 🤖 Local AI diagnosis using Ollama
- 🧠 Evidence-based confidence scoring
- 🔧 Controlled automatic repairs
- 👨‍💻 Human approval before modifications
- 🔄 Iterative repair loop
- 📦 Python dependency installation
- ⚙️ Environment variable fixes
- 📝 JSON configuration fixes
- 🖥️ System dependency detection
- 🔁 Automatic verification after every repair
- 📊 Repair diagnostics

## 🏗️ Architecture

```text
                         👨‍💻 Developer
                              │
                              ▼
                     ┌─────────────────┐
                     │   devplus.py    │
                     │   Orchestrator  │
                     └────────┬────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             ┌─────────────┐    ┌─────────────────┐
             │ scanner.py  │    │                 │
             │             │    │                 │
             │ Discover    │    │ Map dependencies│
             │ project     │    │ & config        │
             └──────┬──────┘    └────────┬────────┘
                    │                    │
                    └─────────┬──────────┘
                              ▼
                     ┌─────────────────┐
                     │   runner.py     │
                     │                 │
                     │ Run application │
                     └────────┬────────┘
                              │
                       ┌──────┴──────┐
                       │             │
                    SUCCESS        ERROR
                       │             │
                       ▼             ▼
                      🎉      ┌───────────────┐
                              │   agent.py    │
                              │               │
                              │ Ollama / Qwen │
                              │   Diagnosis   │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   Confidence  │
                              │   + Evidence  │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │    Human      │
                              │    Approval   │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   fixer.py    │
                              │               │
                              │  Safe Repair  │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   runner.py   │
                              │    Verify     │
                              └───────┬───────┘
                                      │
                           ┌──────────┴──────────┐
                           │                     │
                        SUCCESS                ERROR
                           │                     │
                           ▼                     │
                           🎉                    │
                                                 │
                              ◄──────────────────┘
                                  Next attempt
