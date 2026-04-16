import os
import subprocess

filter_script = """
if [ "$GIT_COMMITTER_EMAIL" = "saranxzi@github.com" ]; then
    export GIT_COMMITTER_NAME="saranxzi"
    export GIT_COMMITTER_EMAIL="mrsaransharma9@gmail.com"
fi
if [ "$GIT_AUTHOR_EMAIL" = "saranxzi@github.com" ]; then
    export GIT_AUTHOR_NAME="saranxzi"
    export GIT_AUTHOR_EMAIL="mrsaransharma9@gmail.com"
fi
"""

cmd = [
    "git", "filter-branch", "-f", "--env-filter", filter_script, "--tag-name-filter", "cat", "--", "--all"
]

# Run using bash emulation if possible, since filter-branch scripts are shell scripts
try:
    # Need to run git inside bash space for string extrapolation. On windows, usually git bash provides 'sh'
    result = subprocess.run(
        ["git", "filter-branch", "-f", "--env-filter", filter_script, "--tag-name-filter", "cat", "--", "--all"],
        cwd="c:\\Saran\\nextprojects\\flightsim",
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
except Exception as e:
    print(str(e))
