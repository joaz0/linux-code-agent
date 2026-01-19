from pathlib import Path

def read_file(path: str):
    return Path(path).read_text()

def write_file(path: str, content: str):
    Path(path).write_text(content)
    return {"written": path}

def list_files(root: str = "."):
    return [str(p) for p in Path(root).rglob("*") if p.is_file()]