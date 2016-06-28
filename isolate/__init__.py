#!/usr/bin/env python
# coding: utf-8
from cgroupspy.nodes import Node

from isolate.namespaces import NewNamespaces, JoinNamespaces, in_namespaces as run_in_namespaces, NAMESPACES
from cgroups import Cgroup
from syscalls import *
from seccomp import SecureComputing, arg_rule
from libseccomp import SCMP_CMP_EQ, SCMP_CMP_GE, SCMP_CMP_GT, SCMP_CMP_LE, SCMP_CMP_LT, SCMP_CMP_MASKED_EQ, SCMP_CMP_NE, ALLOW, KILL, TRAP

BYTES = Cgroup.BYTES
KILOBYTES = Cgroup.KILOBYTES
MEGABYTES = Cgroup.MEGABYTES
GIGABYTES = Cgroup.GIGABYTES

SUBSYSTEMS = Node.CONTROLLERS.keys()
NAMESPACES = NAMESPACES.keys()
