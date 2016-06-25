#!/usr/bin/env python
# coding: utf-8


import ctypes
import errno
import logging
from os import getpid

from isolate.clone import Clone
from isolate.common import CLONE_NEWNS, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWPID, CLONE_NEWUSER, CLONE_NEWUTS, CLONE_NEWCGROUP

from isolate.util import setns, unshare

logging.basicConfig()


class NameSpaceType(object):
    def __init__(self, flag, path='{proc}/{pid!s}/ns/{ns_type}'):
        self.flag = flag
        self.path = path


NAMESPACES = {'mnt': NameSpaceType(CLONE_NEWNS),
              'ipc': NameSpaceType(CLONE_NEWIPC),
              'net': NameSpaceType(CLONE_NEWNET),
              'pid': NameSpaceType(CLONE_NEWPID),
              'user': NameSpaceType(CLONE_NEWUSER),
              'uts': NameSpaceType(CLONE_NEWUTS),
              'cgroup': NameSpaceType(CLONE_NEWCGROUP, '{proc}/{pid!s}/{ns_type}')}


class Namespace(object):
    _log = logging.getLogger(__name__)

    def __init__(self, ns_types, proc='/proc'):
        self._log.setLevel(logging.DEBUG)
        if isinstance(ns_types, str):
            ns_types = [ns_types]

        if any([ns_type not in NAMESPACES.keys() for ns_type in ns_types]):
            raise AttributeError('ns_type must be one of {0}'.format(
                ', '.join(NAMESPACES)
            ))

        self.ns_types = ns_types
        self.proc = proc
        self.parent_paths = self._build_paths(getpid(), ns_types)
        self.parents = []

    def _open_files(self):
        self.parents = [open(p, 'r') for p in self.parent_paths]

    def _close_files(self):
        for fd in self.parents:
            try:
                fd.close()
            except:
                pass
        self.parents = []

    def __exit__(self, *_):
        self._log.debug('Leaving namespaces...')

        for namespace in self.parents:
            self._log.debug('Entering parent namespace %s', namespace.name)
            if setns(namespace.fileno(), 0) == -1:
                self._log.debug('Error while entering namespace %s', namespace.name)

        self._close_files()
        self._log.debug('Left namespaces...')

    def _build_paths(self, pid, ns_types):
        return [NAMESPACES[ns_type].path.format(proc=self.proc, pid=pid, ns_type=ns_type) for ns_type in ns_types]


class JoinNamespaces(Namespace):
    def __init__(self, ns_types, pid=None, paths=None, proc='/proc'):
        super(JoinNamespaces, self).__init__(ns_types, proc)
        if paths and pid:
            raise AttributeError('you can not specify both paths and pid.')

        if isinstance(paths, str):
            paths = [paths]

        if pid:
            paths = self._build_paths(pid, self.ns_types)

        if not paths:
            raise AttributeError('you mast specify at least one of paths or pid.')

        self.paths = paths
        self.children = []

    def __enter__(self):
        self._log.debug('Entering namespaces...')

        try:
            self._open_files()
        except IOError as e:
            self._close_files()
            raise e

        for namespace in self.children:
            self._log.debug('Entering namespace %s', namespace.name)
            if setns(namespace.fileno(), 0) == -1:
                e = ctypes.get_errno()
                self.__exit__()
                raise OSError(e, errno.errorcode[e])

        self._log.debug('Entered namespaces.')

    def _open_files(self):
        super(JoinNamespaces, self)._open_files()
        self.children = [open(p, 'r') for p in self.paths]

    def _close_files(self):
        super(JoinNamespaces, self)._close_files()
        for fd in self.children:
            try:
                fd.close()
            except:
                pass
        self.children = []


class NewNamespaces(Namespace):
    def __init__(self, ns_types):
        super(NewNamespaces, self).__init__(ns_types)
        self.child = None

    def __enter__(self):
        self._log.debug('Entering namespaces...')

        try:
            self._open_files()
        except IOError as e:
            self._close_files()
            raise e

        if unshare(sum(map(lambda x: NAMESPACES[x].flag, self.ns_types))) == -1:
            e = ctypes.get_errno()
            self.__exit__()
            raise OSError(e, errno.errorcode[e])

        self._log.debug('Entered namespaces.')


def in_namespace(target, ns_types, sync=True, *args):
    if any([ns_type not in NAMESPACES.keys() for ns_type in ns_types]):
        raise AttributeError('ns_type must be one of {0}'.format(
            ', '.join(NAMESPACES)
        ))

    cl = Clone(target, args, sum(map(lambda x: NAMESPACES[x].flag, ns_types)))
    if sync:
        cl.wait()
    return cl

