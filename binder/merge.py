import os
import shutil

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILENAME = os.path.join(CURRENT_PATH, 'output.txt')

if __name__ == "__main__":
    with open(OUTPUT_FILENAME, 'wb') as wfd:
        for root, dirs, files in os.walk(CURRENT_PATH):
            if root.endswith(os.sep+"US"):
                for filename in files:
                    if filename.endswith(".txt"):
                        with open(os.path.join(root, filename), 'rb') as fd:
                            shutil.copyfileobj(fd, wfd)
