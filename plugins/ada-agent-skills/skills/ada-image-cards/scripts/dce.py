import ast
def strip_unused(src):
    while True:
        tree = ast.parse(src)
        defs = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defs[node.name] = node
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                defs.setdefault(node.targets[0].id, node)
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                pass
        dead = [n for n in defs if n not in used and not n.startswith("__")]
        # keep names the runtime reads implicitly
        dead = [n for n in dead if n not in ("result",)]
        if not dead:
            return src
        tree.body = [n for n in tree.body if not (
            (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in dead) or
            (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in dead))]
        src = ast.unparse(tree)
