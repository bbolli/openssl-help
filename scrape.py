#! /usr/bin/python3

from __future__ import annotations

import subprocess
from typing import Iterator, Optional


class OpenSSLScraper:

    def ossl_stderr(self, subcmd: str = '') -> Optional[str]:
        cmd = ['openssl', 'help']
        if subcmd:
            cmd.append(subcmd)
        p = subprocess.run(cmd, text=True, capture_output=True)
        if p.returncode:
            return None
        return p.stderr.replace('\r\n', '\n')

    def subcommands(self, main_help: str) -> Iterator[str]:
        for l in main_help.splitlines():
            if not l or 'commands' in l:
                continue
            yield from l.split()

    def gather_help(self) -> Iterator[tuple[str, Optional[str]]]:
        main_help = self.ossl_stderr()
        if main_help is None:
            return
        yield '', main_help
        for subcmd in self.subcommands(main_help):
            yield '-' + subcmd, self.ossl_stderr(subcmd)

    def write_help(self) -> None:
        for subcmd, text in self.gather_help():
            if text is None:
                continue
            print(subcmd, end=' ', flush=True)
            with open(f'openssl{subcmd}.txt', 'w') as f:
                f.write(text)
        print()


scraper = OpenSSLScraper()
scraper.write_help()
