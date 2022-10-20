from utils.general import custom_increment_path
from pathlib import Path

n = custom_increment_path(Path('/media/server-goat/GoatData/goatImages/image'), sep=' ')

print(n)
