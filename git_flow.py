import subprocess
import sys

# Helper to run a shell command and print output
def run(cmd, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def main():
    commit_msg = input("Enter commit message: ")
    # Commit all changes
    run("git add .")
    run(f"git commit -m \"{commit_msg}\"")
    # Get current branch
    res = run("git rev-parse --abbrev-ref HEAD", check=False)
    current_branch = res.stdout.strip()
    if current_branch == "main":
        print("Already on main branch.")
    else:
        # Switch to main
        run("git checkout main")
        # Merge feature branch
        run(f"git merge {current_branch}")
        # Prompt to delete feature branch
        delete = input(f"Delete branch {current_branch}? (y/n): ")
        if delete.lower().startswith('y'):
            run(f"git branch -d {current_branch}")
    # Push main
    run("git push origin main")
    print("Done!")

if __name__ == "__main__":
    main()
