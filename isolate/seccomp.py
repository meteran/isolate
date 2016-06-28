#!/usr/bin/env python
# coding: utf-8
from isolate.libseccomp import KILL, seccomp_init, ALLOW, TRAP, seccomp_rule_add, seccomp_load, seccomp_release, \
    SCMP_CMP, seccomp_reset
from syscalls import *


arg_rule = SCMP_CMP


class SecureComputing(object):
    def __init__(self, default_action=KILL):
        self._ctx = seccomp_init(default_action)

    def reset(self):
        seccomp_reset(self._ctx)

    def allows_rule(self, syscall, *args):
        self._add_rule(syscall, ALLOW, args)

    def kills_rule(self, syscall, *args):
        self._add_rule(syscall, KILL, args)

    def traps_rule(self, syscall, *args):
        self._add_rule(syscall, TRAP, args)

    def _add_rule(self, syscall, action, args):
        r = seccomp_rule_add(self._ctx, action, syscall, len(args), *args)
        if r < 0:
            raise RuntimeError("error nr %d while adding seccomp rule." % -r)

    def load(self):
        seccomp_load(self._ctx)
        seccomp_release(self._ctx)

    def add_whitelist(self, w_list):
        for syscall in w_list:
            self.allows_rule(syscall)

    def add_blacklist(self, b_list, action=KILL):
        if action == KILL:
            for syscall in b_list:
                self.kills_rule(syscall)
        elif action == TRAP:
            for syscall in b_list:
                self.traps_rule(syscall)
        else:
            raise AttributeError("action can be only KILL or TRAP")
