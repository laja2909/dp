from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dp.utils.helper import get_global_confs

def read_confs():
    configs = get_global_confs(Path(__file__).parent.joinpath('confs.json').as_posix())
    return configs

if __name__=='__main__':
    read_confs()