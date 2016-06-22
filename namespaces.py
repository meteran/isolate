#!/usr/bin/env python
# coding: utf-8


import ctypes
import errno
import logging
from pathlib import Path

NAMESPACES = {'mnt', 'ipc', 'net', 'pid', 'user', 'uts', 'cgroup'}


class Namespace(object):
    _log = logging.getLogger(__name__)
    _libc = ctypes.CDLL('libc.so.6', use_errno=True)


class JoinNamespace(Namespace):
    """A context manager for entering namespaces
    Args:
        pid: The PID for the owner of the namespace to enter, or an absolute
             path to a file which represents a namespace handle.
        ns_type: The type of namespace to enter must be one of
                 mnt ipc net pid user uts.  If pid is an absolute path, this
                 much match the type of namespace it represents
        proc: The path to the /proc file system.  If running in a container
              the host proc file system may be binded mounted in a different
              location
    Raises:
        IOError: A non existent PID was provided
        ValueError: An improper ns_type was provided
        OSError: Unable to enter or exit the namespace
    Example:
        with Namespace(916, 'net'):
            #do something in the namespace
            pass
        with Namespace('/var/run/netns/foo', 'net'):
            #do something in the namespace
            pass
    """

    def __init__(self, pid, ns_type=None, ns_types=None, proc='/proc'):
        ns_types = ns_types or {}
        self.ns_types = set(ns_types)
        if ns_type:
            self.ns_types.add(ns_type)

        if not all([x in NAMESPACES for x in self.ns_types]):
            raise ValueError('ns_type must be one of {0}'.format(
                ', '.join(NAMESPACES)
            ))

        self.pid = pid
        self.proc = proc

        # if it's numeric, then it's a pid, else assume it's a path
        try:
            pid = int(pid)
            self.target_fd = self._nsfd(pid, ns_type).open()
        except ValueError:
            self.target_fd = Path(pid).open()

        self.target_fileno = self.target_fd.fileno()

        self.parent_fd = self._nsfd('self', ns_type).open()
        self.parent_fileno = self.parent_fd.fileno()

    __init__.__annotations__ = {'pid': str, 'ns_type': str}


class JoinNamespaces(Namespace):
    def __init__(self, pid, ns_type=None, ns_types=None, proc='/proc'):
        ns_types = ns_types or {}
        self.ns_types = set(ns_types)
        if ns_type:
            self.ns_types.add(ns_type)

        if not all([x in NAMESPACES for x in self.ns_types]):
            raise ValueError('ns_type must be one of {0}'.format(
                ', '.join(NAMESPACES)
            ))

        self.pid = pid
        self.proc = proc

        # if it's numeric, then it's a pid, else assume it's a path
        try:
            pid = int(pid)
            self.target_fd = self._nsfd(pid, ns_type).open()
        except ValueError:
            self.target_fd = Path(pid).open()

        self.target_fileno = self.target_fd.fileno()

        self.parent_fd = self._nsfd('self', ns_type).open()
        self.parent_fileno = self.parent_fd.fileno()

    __init__.__annotations__ = {'pid': str, 'ns_type': str}

    def _nsfd(self, pid, ns_type):
        """Utility method to build a pathlib.Path instance pointing at the
        requested namespace entry
        Args:
            pid: The PID
            ns_type: The namespace type to enter
        Returns:
             pathlib.Path pointing to the /proc namespace entry
        """
        return Path(self.proc) / str(pid) / 'ns' / ns_type

    _nsfd.__annotations__ = {'process': str, 'ns_type': str, 'return': Path}

    def _close_files(self):
        """Utility method to close our open file handles"""
        try:
            self.target_fd.close()
        except:
            pass

        if self.parent_fd is not None:
            self.parent_fd.close()

    def __enter__(self):
        self._log.debug('Entering %s namespace %s', self.ns_type, self.pid)

        if self._libc.setns(self.target_fileno, 0) == -1:
            e = ctypes.get_errno()
            self._close_files()
            raise OSError(e, errno.errorcode[e])

    def __exit__(self, *_):
        self._log.debug('Leaving %s namespace %s', self.ns_type, self.pid)

        if self._libc.setns(self.parent_fileno, 0) == -1:
            e = ctypes.get_errno()
            self._close_files()
            raise OSError(e, errno.errorcode[e])

        self._close_files()


class NewNamespaces(Namespace):
    pass
