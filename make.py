#!/usr/bin/env python3
# coding: utf-8

from __future__ import annotations
from typing import NewType, Union, List, Dict, Tuple, Any

import sys
import os
import os.path as fs
import subprocess as sp
import locale
import shutil
import glob


ExitCode = NewType("ExitCode", int)

IS_WINDOWS = "win32" in sys.platform.lower()

DEV_NULL = "nul" if IS_WINDOWS else "/dev/null"

TOOLS = {
    "sphinx-build": "sphinx-build",
    "hhc": "hhc.exe",
    }

DIRS = {
    "source": r"source",
    "build": r"build",
    "build_htmlhelp": r"build/chm",
    "build_latexpdf": r"build/pdf",
    "doctrees": r"build/doctrees",
    }


def main() -> ExitCode:
    cd = os.getcwd()
    os.chdir((fs.normpath if fs.isabs(__file__) else fs.abspath)(fs.dirname(__file__)))
    try:
        check_sphinx_build()
        if len(sys.argv) < 2:
            run([TOOLS["sphinx-build"], "-M", "help", DIRS["source"], DIRS["build"]], check=False)
            raise RuntimeError
        if IS_WINDOWS and "htmlhelp" in sys.argv:
            check_hhc()
        targets, opt = parse_argv()
        if "build" in opt:
            DIRS["build"] = opt["build"]
            DIRS["build_htmlhelp"] = DIRS["build_htmlhelp"].replace("build", opt["build"])
            DIRS["build_latexpdf"] = DIRS["build_latexpdf"].replace("build", opt["build"])
            DIRS["doctrees"] = DIRS["doctrees"].replace("build", opt["build"])
        if "clean" in targets:
            make_clean()
        for target in [t for t in targets if t != "clean"]:
            fn = globals().get(f"make_{target}", None)
            if fn is not None:
                fn(opt.get("tag", []))
            else:
                raise RuntimeError(f"unknown target '{target}'")
    except (RuntimeError, OSError, sp.SubprocessError) as err:
        if len(err.args) > 0:
            print(f"\nError: {err}")
        return ExitCode(1)
    finally:
        os.chdir(cd)
    return ExitCode(0)


def check_sphinx_build():
    try:
        cmd = os.environ.get("SPHINXBUILD", "sphinx-build")
        c = run(f"{cmd} >{DEV_NULL} 2>&1", shell=True, echo=False, check=False)
        if c >= 9009:
            print("""
The 'sphinx-build' command was not found. Make sure you have Sphinx
installed, then set the SPHINXBUILD environment variable to point
to the full path of the 'sphinx-build' executable. Alternatively you
may add the Sphinx directory to PATH.

If you don't have Sphinx installed, grab it from http://sphinx-doc.org/
""")
            raise RuntimeError
        TOOLS["sphinx-build"] = cmd
    except sp.SubprocessError as err:
        if len(err.args) > 0:
            print(f"\nError: {err}")


def check_hhc():
    try:
        cmd = os.environ.get("HHC", r"C:\Program Files (x86)\HTML Help Workshop\hhc.exe")
        c = run(["cmd.exe", "/c", cmd, DEV_NULL, f">{DEV_NULL}", "2>&1"], echo=False, check=False)
        if c != 0:
            print("""
The 'hhc.exe' tool was not found. Make sure you have HTML Help Workshop
installed, then set the HHC environment variable to point
to the full path of the 'hhc.exe' executable. Alternatively you
may add the HTML Help Workshop directory to PATH.

If you don't have HTML Help Workshop installed, grab it from
https://www.microsoft.com/en-us/download/details.aspx?id=21138
""")
            raise RuntimeError
        TOOLS["hhc"] = cmd
    except sp.SubprocessError as err:
        if len(err.args) > 0:
            print(f"\nError: {err}")


def parse_argv() -> Tuple[List[str], Dict[str, Any]]:
    arg = iter(sys.argv[1:])
    targets = []
    opt = {"unknown": []}
    try:
        while True:
            a = next(arg)
            if a.startswith("-"):
                tokens = a.lstrip("-").split("=", maxsplit=1)
                name = tokens[0]
                value = tokens[1] if len(tokens) == 2 else ""
                if name in ["t", "tag"]:
                    if len(value) <= 0:
                        value = next(arg)
                    opt["tag"] = opt.get("tag", []) + [t for t in value.split(",") if len(t) > 0]
                elif name in ["b", "bd", "build-dir"]:
                    if len(value) <= 0:
                        value = next(arg)
                    opt["build"] = value
                else:
                    opt["unknown"].append(name)
            else:
                targets.append(a)
    except StopIteration:
        if len(opt["unknown"]) > 0:
            print(f"\nError: unknown options")
            for o in opt["unknown"]:
                print(f"  '{o}'")
            raise RuntimeError
    return targets, opt


def make_clean():
    print("\n"
          "________________________________________\n"
          "\n"
          "Cleaning\n"
          "________________________________________\n")
    print(f"Removing '{DIRS['build']}'")
    if fs.exists(DIRS["build"]):
        shutil.rmtree(DIRS["build"])


def make_target(target: str, tags: List[str]):
    print(f"\n"
          f"________________________________________\n"
          f"\n"
          f"Building '{target}'\n"
          f"________________________________________\n")
    opt = []
    for t in tags:
        opt += ["-t", t]
    build_dir = DIRS.get(f"build_{target}", DIRS["build"])
    run([TOOLS["sphinx-build"], "-M", target, DIRS["source"], build_dir, "-d", DIRS["doctrees"]] + opt)


def make_html(tags: List[str]):
    make_target("html", ["MAKE_HTML"] + tags)
    if fs.exists("../lidiya-sokolova.github.io"):
        clean_dir("../lidiya-sokolova.github.io", excludes=[".git", ".nojekyll"])
        copy_dir(DIRS.get(f"build_html", DIRS["build"]) + "/html", "../lidiya-sokolova.github.io", excludes=[".buildinfo", "objects.inv"])


def make_htmlhelp(tags: List[str]):
    make_target("htmlhelp", ["MAKE_CHM"] + tags)
    d = fs.normpath(fs.join(DIRS["build_htmlhelp"], "htmlhelp"))
    for f in os.listdir(d):
        if f.endswith(".hhp"):
            run([TOOLS["hhc"], fs.join(d, f)], check=False)
    for f in os.listdir(d):
        if f.endswith(".chm"):
            shutil.move(fs.join(d, f), DIRS["build_htmlhelp"])


def make_latexpdf(tags: List[str]):
    make_target("latexpdf", ["MAKE_PDF"] + tags)
    d = fs.normpath(fs.join(DIRS["build_latexpdf"], "latex"))
    for f in os.listdir(d):
        if f.endswith(".pdf"):
            shutil.move(fs.join(d, f), DIRS["build_latexpdf"])


def run(cmd: Union[str, List[str]], cwd=None, check=True, shell=False, echo=True) -> ExitCode:
    cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
    if echo:
        print(f"Running `{cmd_str}`\n")
    encoding = locale.getpreferredencoding(False)
    with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=0, cwd=cwd, shell=shell) as p:
        died = False
        buf = ""
        while True:
            buf += p.stdout.read(4096).decode(encoding)
            if len(buf) > 0:
                lines = buf.splitlines(keepends=True)
                buf = "" if lines[-1].endswith(("\n", "\r")) else lines.pop()
                for l_ in lines:
                    print(l_, end="")
                if died and len(buf) > 0:
                    print(buf)
            if p.poll() is not None:
                if not died:
                    died = True
                    continue
                break
        if check and p.returncode != 0:
            raise sp.CalledProcessError(p.returncode, cmd_str, "")
        return ExitCode(p.returncode)


def endswith(s: str, suffixes: list[str]) -> bool:
    for sfx in suffixes:
        if s.endswith(sfx):
            return True
    return False


def scan_dir(path: str) -> Generator[os.DirEntry, None, None]:
    with os.scandir(path) as dir_iter:
        for dir_ent in dir_iter:
            yield dir_ent


def scan_all_files(path: str) -> Generator[os.DirEntry, None, None]:
    for entry in scan_dir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_all_files(entry.path)
        else:
            yield entry


def clean_dir(path: str, excludes: list[str]):
    for entry in scan_dir(path):
        if entry.is_dir(follow_symlinks=False):
            if not endswith(entry.path, excludes):
                shutil.rmtree(entry.path)
        else:
            if not endswith(entry.path, excludes):
                os.unlink(entry.path)


def copy_dir(src: str, dst: str, excludes: list[str]):
    pwd = os.getcwd()
    dst_ = fs.abspath(dst)
    try:
        os.chdir(src)
        for entry in scan_all_files("."):
            if entry.is_file(follow_symlinks=False):
                if not endswith(entry.path, excludes):
                    print(f"Copying '{entry.path}'")
                    os.makedirs(fs.join(dst_, fs.dirname(entry.path)), exist_ok=True)
                    shutil.copy2(entry.path, fs.join(dst_, entry.path))
    finally:
        os.chdir(pwd)


__all__ = []

if __name__ == "__main__":
    sys.exit(main())
