#!/usr/bin/env python
# coding: utf-8
import ctypes
import errno

import os
from signal import SIGCHLD
from time import sleep

CLONE_VM = 0x00000100
CLONE_FS = 0x00000200
CLONE_FILES = 0x00000400
CLONE_SIGHAND = 0x00000800
CLONE_PTRACE = 0x00002000
CLONE_VFORK = 0x00004000
CLONE_PARENT = 0x00008000
CLONE_THREAD = 0x00010000
CLONE_NEWNS = 0x00020000
CLONE_SYSVSEM = 0x00040000
CLONE_SETTLS = 0x00080000
CLONE_PARENT_SETTID = 0x00100000
CLONE_CHILD_CLEARTID = 0x00200000
CLONE_DETACHED = 0x00400000
CLONE_UNTRACED = 0x00800000
CLONE_CHILD_SETTID = 0x01000000
CLONE_NEWUTS = 0x04000000
CLONE_NEWIPC = 0x08000000
CLONE_NEWUSER = 0x10000000
CLONE_NEWPID = 0x20000000
CLONE_NEWNET = 0x40000000
CLONE_IO = 0x80000000

STACK_SIZE = 1024 * 1024

_libc = ctypes.CDLL('libc.so.6', use_errno=True)


class Clone(object):
    def __init__(self, target, args=None, flags=0):
        if not callable(target):
            raise ValueError('target must be callable')

        self.args = args or []

        self.target = target

        child = ctypes.CFUNCTYPE(ctypes.c_int)(self.child)
        child_stack = ctypes.create_string_buffer(STACK_SIZE)
        child_stack_pointer = ctypes.c_void_p(ctypes.cast(child_stack, ctypes.c_void_p).value + STACK_SIZE)

        self.pid = _libc.clone(child, child_stack_pointer, SIGCHLD | flags)

        if self.pid == -1:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e))

    def child(self):
        self.target(*self.args)
        return 54

    def join(self):
        return os.waitpid(self.pid, 0)[1]


a = Clone(lambda: sleep(5), flags=CLONE_NEWPID)
print(a.join())
