#!/usr/bin/env python3
"""Entry program for news-image-20261117.

Copies the front-page image held in this repository to the output
directory, as entry.png. Standard library only, no network, deterministic:
the same file is written on every run.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Fail loudly instead of shipping a truncated copy.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise SystemExit("entry.png copy is incomplete")


if __name__ == "__main__":
    main()
