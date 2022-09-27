#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : cmd_template.py
@Time    : 2022/09/25 21:45:48
@Author  : Roderick Chan
@Email   : ch22166@163.com
@Desc    : subcommand template
'''

from genericpath import isfile
import os
import click
import subprocess
from datetime import datetime
from pwncli.cli import pass_environ

def _which(p):
    return os.system("which " + p + " >/dev/null 2>&1") == 0

def generate_cli_exp(ctx, directory):
    content = """#!/usr/bin/env python3
# Date: {}
# Link: https://github.com/RoderickChan/pwncli
# Usage:
#     Debug : python3 exp.py debug elf-file-path -t -b malloc
#     Remote: python3 exp.py remote elf-file-path ip:port
#     Qemu  : python3 exp.py qemu ./pwn --tmux
#     Qemu  : python3 exp.py qemu ./pwn -L ./libs --tmux

from pwncli import *
cli_script()
{}

io: tube = gift.io
elf: ELF = gift.elf
libc: ELF = gift.libc

CurrentGadgets.set_find_area(find_in_elf=True, find_in_libc=False, do_initial=False)

def cmd(i, prompt):
    sla(prompt, i)

def add():
    cmd('1')
    #......

def edit():
    cmd('2')
    #......

def show():
    cmd('3')
    #......

def dele():
    cmd('4')
    #......


ia()
"""
    exp_path = os.path.join(directory, "exp.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            exit(0)

    set_remote_file = None
    for file in os.listdir(directory):
        if not os.path.isfile(file):
            continue

        if file.startswith("libc.so") or file.startswith("libc-2."):
            set_remote_file = os.path.join(directory, file)
            with open(set_remote_file, "rb") as f:
                data = f.read(4)
                if data != b"\x7fELF":
                    set_remote_file = None
                else:
                    set_remote_file = file
            break
    if set_remote_file:
        add_remote = "set_remote_libc('{}')".format(set_remote_file)
    else:
        add_remote = ""

    content = content.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), add_remote)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate exp file: {}".format(exp_path))


def generate_nocli_exp(ctx, directory):
    content = """#!/usr/bin/env python3
# Date: {}
# Link: https://github.com/RoderickChan/pwncli

from pwncli import *

{}
context.binary = '{}'
context.log_level = 'debug'
context.timeout = 5

gift.io = process('{}')
# gift.io = remote('127.0.0.1', 13337)
gift.elf = ELF('{}')
gift.libc = ELF('{}')

io: tube = gift.io
elf: ELF = gift.elf
libc: ELF = gift.libc

def debug(gdbscript="", stop=False):
    if isinstance(io, process):
        if stop:
            pause()
        gdb.attach(io, gdbscript=gdbscript)

CurrentGadgets.set_find_area(find_in_elf=True, find_in_libc=False, do_initial=False)

def cmd(i, prompt):
    sla(prompt, i)

def add():
    cmd('1')
    #......

def edit():
    cmd('2')
    #......

def show():
    cmd('3')
    #......

def dele():
    cmd('4')
    #......


ia()
"""
    exp_path = os.path.join(directory, "exp_nocli.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            exit(0)

    libc_file = ""
    elf_file = ""
    for file in os.listdir(directory):
        if not os.path.isfile(file):
            continue
        with open(file, "rb") as f:
            data = f.read(4)
            if data != b"\x7fELF":
                continue
            if file.startswith("libc.so") or file.startswith("libc-2."):
                libc_file =  os.path.join(directory, file)
            else:
                if file.startswith("ld.so") or file.startswith("ld-2."):
                    pass
                else:
                    elf_file = os.path.join(directory, file)


    terminal = "context.terminal = "
    if _which("tmux"):
        terminal += "['tmux', 'splitw', '-h']"
    elif _which('gnome-terminal'):
        terminal += "['tmux', '--', 'sh', '-c']"
    else:
        terminal = ""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = content.format(current_time, terminal, elf_file, elf_file, elf_file, libc_file)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate nocli exp file: {}".format(exp_path))


def generate_pwn_exp(ctx, directory):
    content = """#!/usr/bin/env python3
# Date: {}

from pwn import *

{}
context.binary = '{}'
context.log_level = 'debug'
context.timeout = 5

io = process('{}')
# io = remote('127.0.0.1', 13337)
elf = ELF('{}')
libc = ELF('{}')

def debug(gdbscript="", stop=False):
    if isinstance(io, process):
        if stop:
            pause()
        gdb.attach(io, gdbscript=gdbscript)

stop = pause
S = pause
leak = lambda name, address: log.info("{{}} ===> {{}}".format(name, hex(address)))
s   = io.send
sl  = io.sendline
sla = io.sendlineafter
sa  = io.sendafter
slt = io.sendlinethen
st  = io.sendthen
r   = io.recv
rn  = io.recvn
rr  = io.recvregex
ru  = io.recvuntil
ra  = io.recvall
rl  = io.recvline
rs  = io.recvlines
rls = io.recvline_startswith
rle = io.recvline_endswith
rlc = io.recvline_contains
ia  = io.interactive
ic  = io.close
cr  = io.can_recv


def cmd(i, prompt):
    sla(prompt, i)

def add():
    cmd('1')
    #......

def edit():
    cmd('2')
    #......

def show():
    cmd('3')
    #......

def dele():
    cmd('4')
    #......


ia()
"""
    exp_path = os.path.join(directory, "exp_pwn.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            exit(0)

    libc_file = ""
    elf_file = ""
    for file in os.listdir(directory):
        if not os.path.isfile(file):
            continue
        with open(file, "rb") as f:
            data = f.read(4)
            if data != b"\x7fELF":
                continue
            if file.startswith("libc.so") or file.startswith("libc-2."):
                libc_file =  os.path.join(directory, file)
            else:
                if file.startswith("ld.so") or file.startswith("ld-2."):
                    pass
                else:
                    elf_file = os.path.join(directory, file)


    terminal = "context.terminal = "
    if _which("tmux"):
        terminal += "['tmux', 'splitw', '-h']"
    elif _which('gnome-terminal'):
        terminal += "['tmux', '--', 'sh', '-c']"
    else:
        terminal = ""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = content.format(current_time, terminal, elf_file, elf_file, elf_file, libc_file)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate pwn exp file: {}".format(exp_path))



@click.command(name='template', short_help="Generate template file by pwncli.")
@click.argument('filetype', type=str, default=None, required=False, nargs=1)
@pass_environ
def cli(ctx, filetype):
    """
    FILETYPE: cli/nocli

    \b
    pwncli template cli
    pwncli template nocli
    pwncli template pwn
    """
    ctx.verbose = 2
    if not ctx.fromcli:
        ctx.abort("template-command --> Please use the command in cli instead of a script!")
    
    if filetype == "nocli":
        generate_nocli_exp(ctx, ".")
    elif filetype == "pwn":
        generate_pwn_exp(ctx, ".")
    else:
        if filetype and filetype != "cli":
            ctx.abort("template-command --> The choice of filetype is ['cli', 'nocli', 'pwn']!")
        generate_cli_exp(ctx, ".")