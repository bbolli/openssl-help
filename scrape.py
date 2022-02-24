#! /usr/bin/python3

from __future__ import annotations

import subprocess
from typing import Iterator, Optional


def ossl_stderr(subcmd: str = '') -> Optional[str]:
    cmd = ['openssl', 'help']
    if subcmd:
        cmd.append(subcmd)
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode:
        return None
    return p.stderr.replace('\r\n', '\n')


def subcommands(main_help) -> Iterator[str]:
    for l in main_help.splitlines():
        if not l or 'commands' in l:
            continue
        yield from l.split()


def gather_help() -> Iterator[tuple[str, Optional[str]]]:
    main_help = ossl_stderr()
    yield '', main_help
    for subcmd in subcommands(main_help):
        yield '-' + subcmd, ossl_stderr(subcmd)


def write_help() -> None:
    for subcmd, text in gather_help():
        if text is None:
            continue
        print(subcmd, end=' ', flush=True)
        with open(f'openssl{subcmd}.txt', 'w') as f:
            f.write(text)
    print()

write_help()
