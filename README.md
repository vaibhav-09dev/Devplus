# DevPlus

> 🤖 Agentic Local Setup & Bug Diagnostics

**DevPlus** is a local-first developer reliability agent that automatically detects, diagnoses, and helps repair application startup failures.

Instead of manually reading stack traces and debugging configuration issues, DevPlus runs the application, captures the failure, sends the relevant error and project context to a **local Ollama LLM**, and converts the diagnosis into a structured repair action.

The actual modifications are performed by **deterministic Python fixers**, rather than allowing the LLM to directly edit files. This provides better control and makes the repair process safer and more predictable.

DevPlus also uses an **iterative repair loop**. After applying a fix, it runs the application again. If another error appears, the new error is diagnosed and repaired. This continues until the application starts successfully or the maximum number of repair attempts is reached.

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
