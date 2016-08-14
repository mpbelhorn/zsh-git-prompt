#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

from __future__ import print_function
from subprocess import Popen, PIPE
import sys

# change those symbols to whatever you prefer
symbols = {'ahead of': '^', 'behind': 'v', 'prehash':':'}

def git(args):
    return [byte_array.decode('utf-8') for byte_array in Popen(
            ['git'] + args, stdout=PIPE, stderr=PIPE).communicate()]

branch, error = git(['symbolic-ref', 'HEAD'])
if error.find('fatal: Not a git repository') != -1:
    sys.exit(0)

branch = branch.strip()[11:]
res, err = git(['diff', '--name-status'])

if err.find('fatal') != -1:
    sys.exit(0)

changed_files = [namestat[0] for namestat in res.splitlines()]
staged_files = [namestat[0] for namestat in git(
    ['diff', '--staged','--name-status'])[0].splitlines()]
nb_changed = len(changed_files) - changed_files.count('U')
nb_U = staged_files.count('U')
nb_staged = len(staged_files) - nb_U
staged = str(nb_staged)
conflicts = str(nb_U)
changed = str(nb_changed)
nb_untracked = len(git(
    ['ls-files', '--others', '--exclude-standard'])[0].splitlines())
untracked = str(nb_untracked)

if not nb_changed and not nb_staged and not nb_U and not nb_untracked:
    clean = u'1'
else:
    clean = u'0'

remote = ''
if not branch: # not on any branch
    branch = (symbols['prehash'] +
            git(['rev-parse', '--short', 'HEAD'])[0][:-1])
else:
    remote_name = git(
            ['config',
             'branch.{0}.remote'.format(branch)
            ])[0].strip()
    if remote_name:
        merge_name = git(
                ['config',
                 'branch.{0}.merge'.format(branch)
                ])[0].strip()
        if remote_name == '.': # local
            remote_ref = merge_name
        else:
            remote_ref = 'refs/remotes/{0}/{1}'.format(
                    remote_name, merge_name[11:])
        revgit = Popen(
                ['git',
                 'rev-list',
                 '--left-right',
                 '{0}...HEAD'.format(remote_ref)
                ], stdout=PIPE)
        revlist = revgit.communicate()[0].decode('utf-8')
        if revgit.poll(): # fallback to local
            revlist = git(
                    ['rev-list',
                     '--left-right',
                     '{0}...HEAD'.format(merge_name)
                    ])[0]
        behead = revlist.splitlines()
        ahead = len([x for x in behead if x[0]=='>'])
        behind = len(behead) - ahead
        if behind:
            remote += '{0}{1}'.format(symbols['behind'], behind)
        if ahead:
            remote += '{0}{1}'.format(symbols['ahead of'], ahead)

out = '\n'.join([
	branch,
	remote,
	staged,
	conflicts,
	changed,
	untracked,
	clean])
print(out)

