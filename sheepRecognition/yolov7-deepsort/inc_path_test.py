from utils.general import custom_increment_path
from pathlib import Path

n = custom_increment_path(Path("goat/image"), sep=' ')

print(n)