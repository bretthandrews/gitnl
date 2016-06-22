#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

import os
import sys
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE, STDOUT, check_output


def parse_to_git(args):
    """
    returns a string with what should be passed to git.  E.g.,
    "push remotename branchname"
    """
    ind_prep = np.atleast_1d(np.array(args[args['pos'] == 'PRT']['level']))
    if len(ind_prep) == 0:
        print('No preposition found')
    elif len(ind_prep) > 1:
        print('Multiple prepositions found')
    action = args[args['group'] == 'ROOT']['word'].ix[0]
    others = args[args['pos'] == 'NOUN']
    others1 = others[others['parent'] < ind_prep[0]]
    others2 = others[others['parent'] > ind_prep[0]]

    kwargs = dict(action=action, args1=others1['word'].tolist(), args2=others2['word'].tolist())
    cmds = []
    for a2 in kwargs['args2']:
        for a1 in kwargs['args1']:
            cmds.append('{0} {1} {2}'.format(action, a1, a2))
    print('kwargs', kwargs)
    return cmds


cwd = os.getcwd()
os.chdir('/Users/andrews/software/python/models/syntaxnet/')

demo_file = '/Users/andrews/software/python/models/syntaxnet/syntaxnet/demo.sh'
phrase = 'push branch test_branch to remote github_repo.'
bash_cmd = 'echo {0} | {1}'.format(phrase, demo_file)
pp = Popen(bash_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
out = pp.communicate()[0]
out_split = out.split('\n')
for i, it in enumerate(out_split):
    if it[0] == '1':
        ind = i
        break

os.chdir(cwd)

colln_tabbed = out_split[ind:-3]  # need better way to cut off trailing useless rows
colln = [it.split('\t') for it in colln_tabbed]
columns = ['level', 'word', 'ig1', 'pos', 'fine', 'ig2', 'parent', 'group', 'ig3', 'ig4']

raw = pd.DataFrame(colln, columns=columns)
useful_cols = ['level', 'word', 'pos', 'fine', 'parent', 'group']
hier = raw[useful_cols]
hier['level'] = pd.to_numeric(hier['level'])
hier['parent'] = pd.to_numeric(hier['parent'])


#  level         word   pos fine parent  group
#      1         push  VERB   VB      0   ROOT
#      2       branch  NOUN   NN      3     nn
#      3  test_branch  NOUN   NN      1   dobj
#      4           to   PRT   TO      5    aux
#      5       remote  VERB   VB      1  xcomp
#      6  github_repo  NOUN   NN      5   dobj

# ['push VB ROOT',
#  ' +-- test_branch NN dobj',
#  ' |   +-- branch NN nn',
#  ' +-- remote VB xcomp',
#  ' |   +-- to TO aux',
#  ' |   +-- github_repo NN dobj']

if __name__ == '__main__':
    
    # allargs = ' '.join(sys.argv[1:])
    gitcmds = parse_to_git(hier)

    print(gitcmds)

    prompt = 'Options:\n'
    for i, cmd in enumerate(gitcmds):
        prompt += '( {0} ) git {1}\n'.format(i, cmd)

    prompt += 'or type "q" to quit.\n\n'

    res = input(prompt)
    if res in ['q', 'Q', 'quit', 'Quit']:
        sys.exit(1)

    # gitpath = check_output(['which', 'git']).decode()
    # command = gitpath.strip() + ' ' + gitcmds.strip()
    print('Doing this command: "git {}"'.format(gitcmds[res]))
    # sys.exit(os.system(command))
