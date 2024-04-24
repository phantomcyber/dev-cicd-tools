import sys
import os

print(f'hello! {sys.executable}')
print(f'HOST={os.environ.get("HOST_PYTHON_VERSION")}')
print(f'TARGETS={os.environ.get("TARGET_PYTHON_VERSIONS")}')
print(os.getcwd())
