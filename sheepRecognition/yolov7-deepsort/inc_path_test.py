from utils.general import custom_increment_path
from pathlib import Path

n = custom_increment_path(Path('/mnt/sda/goatData/images/image'), sep=' ')

print(n)
