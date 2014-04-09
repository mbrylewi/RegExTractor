'''
Tree structure where every node is a common substring of either characters or
character classes. Leaves are lists of strings where no common substring can
be extracted anymore (e.g. ["AA", "A", ""]).
'''


import re
from utils import *


class Decisioner(object):
    '''Contains static methods that heuristically decide stuff'''

    @staticmethod
    def generalize_kleen(minim, maxim):
        '''Decides if it's ok to use +/* instead of the more strict {min,Max}'''
        if maxim - minim > 4:
            return True


def chars_to_classes(cs):
    '''Replaces characters with their class reference'''
    # Alphabetic
    cs = re.sub(r'[a-z]', 'a', cs)
    cs = re.sub(r'[A-Z]', 'A', cs)
    # Numerical
    cs = re.sub(r'[0-9]', 'N', cs)
    # Space has it's own class
    cs = re.sub(r' ', 'S', cs)
    # Special
    cs = re.sub(r'[^aANS]', 'O', cs)
    return cs

def gen_tree(strs, tp='chars'):
    '''Generates a tree with longest common substrings as nodes'''
    lcs = long_substr(strs)

    if not lcs:
        if tp == 'chars':
            strs = [chars_to_classes(s) for s in strs]
            return gen_tree(strs, tp='classes')
        else:
            return strs

    bgns = []
    ends = []
    for s in strs:
        i = s.find(lcs)
        bgn = s[:i]
        bgns.append(bgn)
        end = s[i+len(lcs):]
        ends.append(end)

    return {
                'root': lcs,
                'left': gen_tree(bgns, tp),
                'right': gen_tree(ends, tp),
                'type': tp
            }

def tree_to_regex(tree):
    '''
    [Based on tree generated by gen_tree()] Generates a regex with an inorder
    traversal.
    Uses Decisioner class to decide on when to generalize more or less.
    '''
    def strs_range(strs):
        '''Helper function: '''
        minim = 99999
        maxim = 0
        clss = []
        for s in strs:
            for sc in s:
                if sc not in clss:
                    clss.append(sc)
            l = len(s)
            if l > maxim:
                maxim = l
            if l < minim:
                minim = l
        return (clss, minim, maxim)

    clss = {
        'a': 'a-z',
        'A': 'A-Z',
        'N': '0-9',
        'S': ' ',
        'O': '!@#$%^&*()_+=-`~\'";:,<.>/?\\\]}\[{',
        # 'O': '!@#$%',
    }

    if type(tree) == dict:
        if tree['type'] == 'chars':
            return  tree_to_regex(tree['left']) + \
                    re.escape(tree['root']) + \
                    tree_to_regex(tree['right'])
        elif tree['type'] == 'classes':
            out = ''
            for c in tree['root']:
                out += '[%s]' % clss[c]
            return  tree_to_regex(tree['left']) + \
                    out + \
                    tree_to_regex(tree['right'])
    else:
        cs, m, M = strs_range(tree)
        if not M:
            return ''
        out = '['
        for c in cs:
            out += clss[c]
        out += ']'
        if M > 1:
            if Decisioner.generalize_kleen(m, M):
                if not m:
                    out += '*'
                else:
                    out += '+'
            else:
                out += '{%d,%d}' % (m, M)
        elif m == 0:
            out += '?'
        return out


def tree_to_HTML(tree):
    '''
    [Based on tree generated by gen_tree()] Generates an HTML block with a nice
    representation of the regex, using an inorder traversal.
    Similar to tree_to_regex(), but generates a visual thing, only for display.
    '''
    def strs_range(strs):
        '''Helper function: '''
        minim = 99999
        maxim = 0
        clss = []
        for s in strs:
            for sc in s:
                if sc not in clss:
                    clss.append(sc)
            l = len(s)
            if l > maxim:
                maxim = l
            if l < minim:
                minim = l
        return (clss, minim, maxim)

    clss = {
        'a': 'a-z',
        'A': 'A-Z',
        'N': '0-9',
        'S': '<span class="rgt-space-char rgt-tooltip" title="Space character"> </span>',
        'O': '!@#<i class="fa fa-ellipsis-h rgt-ellipsis"></i>',
    }

    if type(tree) == dict:
        if tree['type'] == 'chars':
            return  tree_to_HTML(tree['left']) + \
                    '<span class="rgt-exact-match rgt-tooltip">' + \
                    tree['root'].replace(' ', '<span class="rgt-space-char rgt-tooltip" title="Space character"> </span>') + \
                    '</span>' + \
                    tree_to_HTML(tree['right'])
        elif tree['type'] == 'classes':
            out = ''
            for c in tree['root']:
                out += '<span class="rgt-range rgt-tooltip">'
                out += '[%s]' % clss[c]
                out += '</span>'
            return  tree_to_HTML(tree['left']) + \
                    out + \
                    tree_to_HTML(tree['right'])
    else:
        cs, m, M = strs_range(tree)
        if not M:
            return ''
        out = '<span class="rgt-range rgt-tooltip">'
        out += '['
        for c in cs:
            out += clss[c]
        out += ']'
        out += '</span>'
        if M > 1:
            if Decisioner.generalize_kleen(m, M):
                if not m:
                    out += '<span class="rgt-quantifier">'
                    out += '*'
                    out += '</span>'
                else:
                    out += '<span class="rgt-quantifier">'
                    out += '+'
                    out += '</span>'
            else:
                out += '<span class="rgt-counts">'
                out += '{%d,%d}' % (m, M)
                out += '</span>'
        elif m == 0:
            out += '<span class="rgt-quantifier">'
            out += '?'
            out += '</span>'
        return out


if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter()

    s1 = 'abc$1250'
    s2 = 'xby#340'
    s3 = 'sbs@00000'
    # pp.pprint(gen_tree([s1, s2, s3]))
    print tree_to_HTML(gen_tree([s1, s2, s3]))

    s1 = 'skull'
    s2 = 'school'
    # pp.pprint(gen_tree([s1, s2]))
    print tree_to_HTML(gen_tree([s1, s2]))
