# CodeInsight — AI-Based Code Review & Time Complexity Analyzer

A student-level Flask web prototype for static analysis of Python source code.

## Features
- Paste Python code and submit it for analysis.
- Parse source using Python's `ast` module (code is not executed).
- Estimate complexity from recognized loop depth and sorting patterns.
- Flag nested loops and recursion; display beginner-friendly explanations.
- Responsive browser UI with sample code and findings report.

## Run locally
1. Install Python 3.9+.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000

## Scope / limitations
This is a rule-based static-analysis prototype, not a hosted AI service. It currently analyzes Python only. Big-O estimates are heuristic and depend on recognizable patterns; it does not prove correctness, detect every bug, or execute submitted code.
