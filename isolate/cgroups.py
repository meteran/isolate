#!/usr/bin/env python
# coding: utf-8
import os
from datetime import timedelta
from signal import SIGKILL

from cgroupspy.trees import GroupedTree
from cgroupspy.nodes import Node
from datetime import datetime


class Cgroup(object):
    BYTES = 1
    KILOBYTES = 1024
    MEGABYTES = 1024**2
    GIGABYTES = 1024**3

    DEFAULT_CPU = 1024

    def __init__(self, path, subsystems):
        if any([subsystem not in Node.CONTROLLERS.keys() for subsystem in subsystems]):
            raise AttributeError('subsystem must be one of {0}'.format(
                ', '.join(Node.CONTROLLERS.keys())
            ))

        if not path.startswith(os.sep):
            path = os.sep + path

        self._tree = GroupedTree()
        self.subsystems = set(subsystems)

        self.path = path
        splitted_path = path.split(os.sep)
        self.parent = os.sep.join(splitted_path[:-1])
        if not self.parent:
            self.parent = os.sep
        self.name = splitted_path[-1]

        self.nodes = []
        self._init_nodes()
        self._tree = GroupedTree()

    def _init_nodes(self):
        parent_node = self._tree.get_node_by_path(self.parent)
        if not parent_node:
            raise OSError('there is no subsystem on path {}.'.format(self.parent))
        node = self._tree.get_node_by_path(self.path)
        for subsystem in self.subsystems:
            if node and subsystem in node.controllers.keys():
                n = self._get_node(subsystem, node)
            else:
                n = self._create_node(subsystem, parent_node)
            self._add_node(n)

    def _add_node(self, node):
        self.nodes.append(node)
        if node.controller:
            setattr(self, node.controller_type, node.controller)

    def _create_node(self, subsystem, parent_node):
        for node in parent_node.nodes:
            if node.controller_type == subsystem:
                return node.create_cgroup(self.name)
        raise AttributeError('there is no subsystem {} on cgroup {}.'.format(subsystem, parent_node.path))

    @staticmethod
    def _get_node(subsystem, node):
        for n in node.nodes:
            if n.controller_type == subsystem:
                return n

    def delete(self, kill_tasks=False, timeout=5):
        if kill_tasks:
            for pid in self.tasks:
                os.kill(pid, SIGKILL)
            dt = datetime.now() + timedelta(seconds=timeout)
            while self.tasks and dt > datetime.now():
                pass
        for node in self.nodes:
            node.parent.delete_cgroup(node.name)
        self._tree = GroupedTree()
        self.nodes = []

    def create(self):
        if self.nodes:
            raise RuntimeError('cgroups {} already exists.'.format(self.path))
        self._init_nodes()
        self._tree = GroupedTree()

    def enter(self):
        self.add_pid(os.getpid())

    def add_pid(self, pid):
        os.system('cgclassify -g {}:{} {}'.format(','.join(self.subsystems), self.path, pid))

    def execute_command(self, cmd, *args):
        if args:
            os.system('cgexec -g {}:{} {} {}'.format(','.join(self.subsystems), self.path, cmd, ' '.join(args)))
        else:
            os.system('cgexec -g {}:{} {}'.format(','.join(self.subsystems), self.path, cmd))

    def _check_subsystem(self, subsystem):
        if subsystem not in self.subsystems:
            raise AttributeError('subsystem {} not belongs to cgroup {}.'.format(subsystem, self.path))

    def set_memory_limit(self, limit, unit=BYTES):
        self._check_subsystem('memory')
        self.memory.limit_in_bytes = limit*unit

    def set_cpu_limit(self, limit=100):
        self._check_subsystem('cpu')
        if limit < 1:
            raise AttributeError('cpu limit must be 1 or greater.')
        self.cpu.shares = int(self.DEFAULT_CPU * limit / 100)

    def set_cpus(self, *args):
        self._check_subsystem('cpuset')
        self.cpuset.cpus = ','.join(map(str, args))

    def set_memory_nodes(self, *args):
        self._check_subsystem('cpuset')
        self.cpuset.mems = ','.join(map(str, args))

    @property
    def tasks(self):
        node = self._tree.get_node_by_path(self.path)
        if node:
            return node.tasks
        return set()

    def create_child(self, name):
        return Cgroup(os.path.join(self.path, name), self.subsystems)
