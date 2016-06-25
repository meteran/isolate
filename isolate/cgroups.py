#!/usr/bin/env python
# coding: utf-8
import os

from cgroupspy.trees import GroupedTree
from cgroupspy.nodes import Node


class Cgroup(object):
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
        self.name = splitted_path[-1]

        self.nodes = []
        self._init_nodes()
        self._tree = GroupedTree()

        self.processes = []

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
            self.nodes.append(n)

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

    def delete(self):
        for node in self.nodes:
            node.parent.delete_cgroup(node.name)
        self._tree = GroupedTree()
        self.nodes = []

    def create(self):
        if self.nodes:
            raise RuntimeError('cgroups {} already exists.'.format(self.path))

    def enter(self):
        os.system('cgclassify -g {}:{} {}'.format(','.join(self.subsystems), self.path, os.getpid()))

if __name__ == '__main__':
    c = Cgroup('group2/group3', ['memory', 'cpu'])
    print c.nodes
    raw_input()
    c.delete()

