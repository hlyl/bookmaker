import subprocess
import sys

if __name__ == "__main__":
    subprocess.run(["python", "src/main.py"] + sys.argv[1:])
