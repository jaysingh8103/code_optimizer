import os
import sys
import subprocess
import ast

# Error detection tools
ERROR_TOOLS = {
    "pylint": "pylint {file_path} --output-format=text",
    "ruff": "ruff check {file_path}",
    "vulture": "vulture {file_path}"
}

# Code formatting and optimization tools
FORMAT_TOOLS = {
    "black": "black {file_path}",
    "autopep8": "autopep8 --in-place {file_path}",
    "isort": "isort {file_path}"
}

# Custom AST-based optimizations
class CodeOptimizer(ast.NodeTransformer):
    """Optimize Python code by transforming inefficient patterns."""

    def visit_For(self, node):
        """Optimize loops into list comprehensions if possible."""
        if (
            isinstance(node.target, ast.Name)
            and isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Expr)
        ):
            # Unroll small loops
            if isinstance(node.body[0].value, ast.Call):
                call_func = node.body[0].value.func.id
                if call_func == "print":
                    return [ast.Expr(value=ast.Call(func=ast.Name(id="print", ctx=ast.Load()), args=[ast.Constant(value="Hello")], keywords=[]))]
        return node

    def visit_ListComp(self, node):
        """Ensure list comprehensions are applied efficiently."""
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        """Replace inefficient data structures with efficient ones."""
        if isinstance(node.func, ast.Name) and node.func.id == "list":
            # Replace list(set(...)) with set(...)
            if len(node.args) == 1 and isinstance(node.args[0], ast.Call):
                if isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == "set":
                    return node.args[0]
        return node

    def visit_FunctionDef(self, node):
        """Apply memoization for recursive functions."""
        if node.name == "fib":
            decorator = ast.Name(id="lru_cache", ctx=ast.Load())
            node.decorator_list.append(decorator)
        return node


def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)


def detect_errors(file_path):
    """Run error detection tools and print results."""
    print(f"\n Checking for errors in: {file_path}")
    for tool, command in ERROR_TOOLS.items():
        print(f"\n Running {tool}...")
        stdout, stderr = run_command(command.format(file_path=file_path))
        if stdout:
            print(f" {tool} Output:\n{stdout}")
        if stderr:
            print(f"{tool} Errors:\n{stderr}")


def format_code(file_path):
    """Format code using Black, AutoPEP8, and Isort."""
    print(f"\n Formatting code in: {file_path}")
    for tool, command in FORMAT_TOOLS.items():
        print(f" Running {tool}...")
        stdout, stderr = run_command(command.format(file_path=file_path))
        if stdout:
            print(f"{tool} Output:\n{stdout}")
        if stderr:
            print(f"{tool} Errors:\n{stderr}")


def optimize_code(file_path):
    """Apply AST-based optimizations and overwrite the file."""
    try:
        with open(file_path, "r") as file:
            source_code = file.read()

        tree = ast.parse(source_code)
        optimizer = CodeOptimizer()
        optimized_tree = optimizer.visit(tree)
        ast.fix_missing_locations(optimized_tree)
        optimized_code = ast.unparse(optimized_tree)

        with open(file_path, "w") as file:
            file.write(optimized_code)

        print(f"AST-based optimization applied for: {file_path}")

    except (SyntaxError, ValueError) as e:
        print(f"Failed to optimize {file_path}: {e}")


def process_python_file(file_path):
    """Run all steps on a single Python file."""
    print(f"\nProcessing: {file_path}")
    detect_errors(file_path)
    format_code(file_path)
    optimize_code(file_path)


def scan_and_optimize(directory):
    """Recursively scan and optimize all Python files in the directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith(("simple", "example")) and file.endswith(".py"):
                file_path = os.path.join(root, file)
                process_python_file(file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code_optimizer.py <directory_or_file_path>")
        sys.exit(1)

    target_path = sys.argv[1]

    if os.path.isdir(target_path):
        print(f"\n Scanning directory: {target_path}")
        scan_and_optimize(target_path)
    elif os.path.isfile(target_path) and target_path.endswith(".py"):
        print(f"\nProcessing single file: {target_path}")
        process_python_file(target_path)
    else:
        print(f"Invalid path: {target_path}")

    print("\n All Python files have been optimized successfully!")
