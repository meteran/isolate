#!/usr/bin/env python
# coding: utf-8

from isolate.namespaces import NewNamespaces, JoinNamespaces, in_namespace as run_in_namespace
from cgroups import Cgroup

BYTES = Cgroup.BYTES
KILOBYTES = Cgroup.KILOBYTES
MEGABYTES = Cgroup.MEGABYTES
GIGABYTES = Cgroup.GIGABYTES