#!/usr/bin/env python
# coding: utf-8
import ctypes
import os
from signal import SIGCHLD

from isolate.util import clone

STACK_SIZE = 1024 * 1024


class Clone(object):
    def __init__(self, target, args=None, flags=0):
        if not callable(target):
            raise ValueError('target must be callable')

        self.args = args or []

        self.target = target

        child = ctypes.CFUNCTYPE(ctypes.c_int)(self._child)
        child_stack = ctypes.create_string_buffer(STACK_SIZE)
        child_stack_pointer = ctypes.c_void_p(ctypes.cast(child_stack, ctypes.c_void_p).value + STACK_SIZE)

        self.pid = clone(child, child_stack_pointer, SIGCHLD | flags)

        if self.pid == -1:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e))

    def _child(self):
        try:
            return int(self.target(*self.args))
        except:
            return 0

    def wait(self):
        try:
            return os.waitpid(self.pid, 0)[1]/256
        except:
            return -1
