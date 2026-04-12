import sys
import os

# Add the parent directory to sys.path to allow imports from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import app

def main():
    import uvicorn
    # Using import string so uvicorn can find the app in the root directory context
    uvicorn.run("environment:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
