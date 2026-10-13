import ast

from flask import Flask, render_template, request

app = Flask(__name__)


def explain_code(source: str, language: str) -> list[str]:
    """Create a lightweight local walkthrough from recognizable code patterns."""
    explanations = []
    try:
        tree = ast.parse(source) if language == "Python" else None
    except SyntaxError:
        tree = None

    if tree:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in node.args.args]
                explanations.append(
                    f"Line {node.lineno}: defines the function '{node.name}'"
                    + (f", which accepts {', '.join(args)}." if args else ", with no arguments.")
                )
            elif isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                if names:
                    explanations.append(f"Line {node.lineno}: stores a value in {', '.join(names)}.")
            elif isinstance(node, ast.Return):
                explanations.append(f"Line {node.lineno}: sends a result back to the caller.")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    explanations.append(f"Line {node.lineno}: displays output in the console.")
                elif isinstance(node.func, ast.Attribute):
                    explanations.append(f"Line {node.lineno}: calls the '{node.func.attr}' method.")
            elif isinstance(node, (ast.If, ast.For, ast.While)):
                label = "checks a condition" if isinstance(node, ast.If) else "starts a loop"
                explanations.append(f"Line {node.lineno}: {label}.")

    if not explanations:
        for number, line in enumerate(source.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*")):
                continue
            if stripped.startswith(("def ", "function ", "async function ")):
                explanations.append(f"Line {number}: declares a function.")
            elif stripped.startswith(("if ", "if(", "elif ", "else", "switch ", "case ")):
                explanations.append(f"Line {number}: controls which code runs based on a condition.")
            elif stripped.startswith(("for ", "for(", "while ", "while(")):
                explanations.append(f"Line {number}: repeats code in a loop.")
            elif stripped.startswith(("import ", "from ", "#include")):
                explanations.append(f"Line {number}: brings in a library or module.")
            elif "print(" in stripped or "console.log(" in stripped:
                explanations.append(f"Line {number}: displays output.")
            elif "=" in stripped and not any(op in stripped for op in ("==", ">=", "<=", "!=")):
                explanations.append(f"Line {number}: assigns a value to a variable.")
            else:
                explanations.append(f"Line {number}: runs a statement or expression.")

    return explanations or ["Add some code to get a walkthrough."]


def find_issues(source: str, language: str) -> list[dict]:
    """Find Python syntax errors or basic bracket mismatches for other languages."""
    if not source.strip():
        return [{"line": None, "message": "Add or upload some code to start the review."}]

    if language == "Python":
        try:
            ast.parse(source)
        except SyntaxError as error:
            message = error.msg
            if error.text:
                message = f"{message}: {error.text.strip()}"
            return [{"line": error.lineno, "message": message}]
        return []

    pairs = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for char in line:
            if char in pairs:
                stack.append((char, line_number))
            elif char in pairs.values():
                if not stack or pairs[stack[-1][0]] != char:
                    return [{"line": line_number, "message": f"Unexpected closing bracket '{char}'."}]
                stack.pop()
    if stack:
        char, line_number = stack[-1]
        return [{"line": line_number, "message": f"Missing closing bracket '{pairs[char]}'."}]
    return []


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    selected_language = request.form.get("language", "Python")
    code = request.form.get("code", "")

    if request.method == "POST":
        issues = find_issues(code, selected_language)
        if issues and issues[0]["line"] is None:
            result = {"empty": True, "issues": issues, "explanations": []}
        else:
            result = {
                "empty": False,
                "issues": issues,
                "explanations": explain_code(code, selected_language),
                "count": len(issues),
            }

    return render_template("index.html", result=result, selected_language=selected_language, code=code)


if __name__ == "__main__":
    app.run(debug=True)
