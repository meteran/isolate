#!/usr/bin/env python
# coding: utf-8

import ctypes


_libc = ctypes.CDLL('libc.so.6', use_errno=True)
clone = _libc.clone
setns = _libc.setns
unshare = _libc.unshare