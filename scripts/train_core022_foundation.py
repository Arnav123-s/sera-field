"""Run or exactly resume one prospectively frozen coupled-owner teaching arm."""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.core_course import train

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('arm', choices=['credited','withheld'])
    args = parser.parse_args(); torch.set_num_threads(1); train(args.arm)
