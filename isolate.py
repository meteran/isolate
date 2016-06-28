#!/usr/bin/env python
# coding: utf-8
import argparse, os

from isolate import SUBSYSTEMS, NAMESPACES, Cgroup, run_in_namespaces


def enter_cgroup(target, name, subsystems):
    c = Cgroup(name, subsystems)
    c.enter()
    target()


def parse_cgroups(string):
    try:
        subsystems, path = string.split(":")
        subsystems = subsystems.split(',')
    except:
        raise argparse.ArgumentTypeError('wrong type of arguments: %s' % string)

    if any([subsystem not in SUBSYSTEMS for subsystem in subsystems]):
        raise argparse.ArgumentTypeError('subsystem must be one of {0}'.format(', '.join(SUBSYSTEMS)))

    return path, subsystems


def parse_args():
    parser = argparse.ArgumentParser(description="run your unsafe program")
    parser.add_argument('unsafe_program')
    parser.add_argument('arg', nargs='*')
    parser.add_argument("-cg", "--cgroups", nargs=1, type=parse_cgroups, metavar='SUBSYSTEMS:PATH')
    parser.add_argument("-ns", "--namespaces", nargs='+', choices=NAMESPACES)
    parser.add_argument("-nsc", "--no-seccomp", action='store_false')
    args = parser.parse_args()
    return args.unsafe_program, args.arg, args.cgroups, args.namespaces, args.no_seccomp


def main(program, args, cgroups, namespaces, seccomp):
    to_run = [program] + args
    cmd = ' '.join(to_run)
    if cgroups:
        c = Cgroup(cgroups[0], cgroups[1])
        if seccomp:
            f = lambda: c.execute_command('seccomp_isolate', *to_run)
        else:
            f = lambda: c.execute_command(program, *args)
    elif seccomp:
        f = lambda: os.system('seccomp_isolate ' + cmd)
    else:
        f = lambda: os.system(cmd)

    if namespaces:
        run_in_namespaces(f, namespaces)
    else:
        f()


if __name__ == '__main__':
    args = parse_args()
    print args
    main(*args)
