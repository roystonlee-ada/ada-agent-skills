import ast, sys, re
def minify(src):
    tree = ast.parse(src)
    out = ast.unparse(tree)
    lines = []
    for ln in out.split("\n"):
        stripped = ln.lstrip(" ")
        ind = (len(ln) - len(stripped)) // 4
        lines.append(" " * ind + stripped)
    return "\n".join(lines) + "\n"
if __name__ == "__main__":
    s = minify(open(sys.argv[1]).read()); open(sys.argv[2], "w").write(s); print(len(s.encode()))
