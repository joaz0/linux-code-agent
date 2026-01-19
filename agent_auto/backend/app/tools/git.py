from subprocess import run

def git_status():
    return run("git status --short", shell=True, capture_output=True, text=True).stdout

def git_commit(message: str):
    run("git add .", shell=True)
    return run(f'git commit -m "{message}"', shell=True, capture_output=True, text=True).stdout
