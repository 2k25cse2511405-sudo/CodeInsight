from flask import Flask, render_template, request, jsonify
import ast
import re

app = Flask(__name__)

def analyze_python(source):
    findings = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "valid": False,
            "error": f"Syntax error on line {exc.lineno}: {exc.msg}",
            "complexity": "Unknown",
            "summary": "Fix the syntax error before analysis.",
            "findings": []
        }

    loop_depth = 0
    max_loop_depth = 0
    loop_count = 0
    has_sort = False
    recursive_functions = set()
    function_names = set()

    class Analyzer(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.max_depth = 0
            self.loops = 0
            self.sorts = 0
            self.func_stack = []

        def visit_For(self, node):
            self.loops += 1
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)
            if self.depth == 2:
                findings.append({
                    "severity": "warning",
                    "title": "Nested iteration detected",
                    "line": node.lineno,
                    "detail": "A loop inside another loop may increase runtime to O(n²) or more."
                })
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node):
            self.loops += 1
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)
            if self.depth == 2:
                findings.append({
                    "severity": "warning",
                    "title": "Nested loop detected",
                    "line": node.lineno,
                    "detail": "Nested loops can make runtime grow quickly as input size increases."
                })
            self.generic_visit(node)
            self.depth -= 1

        def visit_FunctionDef(self, node):
            function_names.add(node.name)
            self.func_stack.append(node.name)
            self.generic_visit(node)
            self.func_stack.pop()

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "sorted"):
                self.sorts += 1
            if isinstance(node.func, ast.Name) and node.func.id in function_names:
                recursive_functions.add(node.func.id)
            self.generic_visit(node)

    visitor = Analyzer()
    visitor.visit(tree)
    loop_count = visitor.loops
    max_loop_depth = visitor.max_depth
    has_sort = visitor.sorts > 0

    # A second pass catches direct self-recursion reliably.
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                   and call.func.id == node.name for call in ast.walk(node)):
                recursive_functions.add(node.name)

    if max_loop_depth >= 2:
        complexity = "O(n²) or higher"
        explanation = "Nested loops were found. The estimate assumes each loop scales with input size."
    elif max_loop_depth == 1 and has_sort:
        complexity = "O(n log n)"
        explanation = "A loop and a sorting operation were found; sorting often dominates at O(n log n)."
    elif max_loop_depth == 1:
        complexity = "O(n)"
        explanation = "A single loop was found; its work is assumed to scale linearly with input size."
    elif has_sort:
        complexity = "O(n log n)"
        explanation = "A sorting operation was found; common comparison sorts run in O(n log n)."
    elif recursive_functions:
        complexity = "Potentially exponential / depends on recurrence"
        explanation = "Recursion was detected. Exact complexity depends on the recurrence and branching."
    else:
        complexity = "O(1) (estimated)"
        explanation = "No scaling loop or sorting pattern was recognized."

    if not findings:
        findings.append({
            "severity": "success",
            "title": "No obvious nested-loop issue",
            "line": None,
            "detail": "The basic rule checks did not detect nested iteration."
        })

    if has_sort:
        findings.append({
            "severity": "info",
            "title": "Sorting operation detected",
            "line": None,
            "detail": "Sorting is commonly O(n log n). Check whether sorting is necessary or can be performed once."
        })

    if recursive_functions:
        findings.append({
            "severity": "warning",
            "title": "Recursion detected",
            "line": None,
            "detail": "Review the base case and recurrence; repeated recursive calls may cause high time or stack cost."
        })

    return {
        "valid": True,
        "complexity": complexity,
        "summary": explanation,
        "loops": loop_count,
        "max_loop_depth": max_loop_depth,
        "findings": findings
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"valid": False, "error": "Paste some code to analyze."}), 400
    if language != "python":
        return jsonify({
            "valid": False,
            "error": "This prototype currently analyzes Python code. Select Python or use the sample."
        }), 400
    return jsonify(analyze_python(code))

if __name__ == "__main__":
    app.run()
