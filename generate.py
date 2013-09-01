#!/usr/bin/python

""" Generate random sentences from a grammar given in a file.  print
either the sentence string or the structure."""

from random import choice
from pprint import pprint
import sys, resource
from collections import defaultdict
from  argparse import ArgumentParser

# Since Python doesn't optimize tail recursion, deeply recursive
# programs can exhaust stack space or hit the recursion limit
try:
  # increase stack size to 16MB and recursion limit to 1M
  resource.setrlimit(resource.RLIMIT_STACK, (2**24,-1))
  sys.setrecursionlimit(10**6)
except:
  # you may have to tweak Mac setting to allow it :(
  pass


def load_grammar(file):
    """Load grammar from file and return as dictionary where keys are
    non-terminals and values are lists of possible rewrites, e.g.:
    {'S':[('S','or','S'),('NP','VP')],'NP':[('DET','N'),('N',)],...}"""
    grammar = defaultdict(list)
    for line in open(file):
        line = line.strip()
        if '#' in line:
            line, comment = line.split('#')
        if line:
            # line is like:  NP -> Art N | Art Adj N
            lhs, rhs = line.split('->')
            lhs = lhs.strip()
            rhs = [alt.split() for alt in rhs.strip().split('|')]
            # add new RHS to LHS entry
            grammar[lhs] += rhs
    return grammar

def generate(g, start='S', tree=False, n=1):
    """ Generate n sentences from grammar g starting with symbol
    start.  If tree is true, generate the parse trees and pprint, else
    generate simple strings and print."""
    while n>0:
        n = n-1
        try:
            if tree:
                pprint(rewrite_tree(g, start))
            else:
                print rewrite(g, start)
        except RuntimeError, e:
            print e

def rewrite(g, x='S'):
    """Replace tokens in list with a random entry in grammar g, recurse"""
    def rw(t):
        return rewrite(g, choice(g[t])) if t in g else t
    return ' '.join(filter(bool, map(rw, x))) if isinstance(x, list) else rw(x)


def rewrite_tree(g, x='S'):
    """Like rewrite, but returns a tuple representing the sentence structure"""
    def rw(t):
        return tuple([t] + rewrite_tree(g, choice(g[t]))) if t in g else t
    return map(rw, x) if isinstance(x, list) else rw(x)


# what to do if called as a script
if __name__ == "__main__":
    # process command line arguments
    p = ArgumentParser(description='Generate random sentences from a grammar')
    p.add_argument('-g', action="store", dest="gfile", required=True,
                   help='File path to grammar')
    p.add_argument('-t', action="store_true", default=False,
                   help='Print sentences as trees rather than strings')
    p.add_argument('-s', action="store", dest="start", default="S",
                   help="Start symbol, defaults to S")
    p.add_argument('-n', action="store", default=1,
                   help="Number of sentences to generate")
    args = p.parse_args()

    generate(load_grammar(args.gfile), args.start, args.t, int(args.n))

