#! /usr/bin/python3

from __future__ import annotations

import os
import subprocess
from typing import Iterator, Optional


class OpenSSLScraper:
    def __init__(self, devdir: str = ''):
        self.devdir = devdir
        self.binary = 'openssl'
        self.env = None
        if devdir:
            # call the binary in devdir with those libraries
            self.binary = devdir + '/apps/openssl'
            self.env = os.environ.copy()
            self.env['LD_LIBRARY_PATH'] = devdir
            self.env['OPENSSL_CONF'] = '/dev/null'
        version = subprocess.run(
            [self.binary, 'version'], text=True, capture_output=True, env=self.env
        ).stdout.split()[1].split('.')
        if version[2][-1].isalpha():
            patch = version[2].lstrip('0123456789')
            version[2] = version[2].replace(patch, '')
            self.version = tuple([int(v) for v in version] + [patch])
        else:
            self.version = tuple(int(v) for v in version)
        print(f"{self.binary} version: {self.version}")

    def help_cmd(self, subcmd: str = '') -> list[str]:
        if self.version < (1, 1):
            cmd = [self.binary, '-help']
            if subcmd:
                cmd.insert(1, subcmd)
                if subcmd == 'pkeyparam':
                    cmd[2] = '-in'  # '-help' doesn't work
        else:
            cmd = [self.binary, 'help']
            if subcmd:
                cmd.append(subcmd)
        return cmd

    def ossl_stderr(self, subcmd: str = '') -> Optional[str]:
        text = subprocess.run(
            self.help_cmd(subcmd), text=True, capture_output=True, env=self.env
        ).stderr
        if subcmd and not any(l.strip().startswith('-') for l in text.splitlines()):
            return None
        return text.replace('unknown option -help\n', '') \
            .replace('unknown option \'-help\'\n', '') \
            .replace('\r\n', '\n')

    def subcommands(self, main_help: str) -> Iterator[str]:
        for l in main_help.splitlines():
            if not l or 'commands' in l \
            or any(l.startswith(p) for p in (
                'WARNING:', 'openssl:Error:', 'unknown option'
            )):
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
