#!/usr/bin/python

# Inspired by an example from Peter Norvig, see http://norvig.com/python-lisp.html

"""Module to generate random sentences from a grammar.  The grammar consists of
entries that can be written as S = 'NP VP | S and S', which gets translated to
{'S': [['NP', 'VP'], ['S', 'and', 'S']]}, and means that one of the top-level
lists will be chosen at random, and then each element of the second-level list
will be rewritten; if it is not in the grammar it rewrites as itself.  The
functions rewrite and rewrite_tree take as input a list of words and an
accumulator (empty list) to which the results are appended.  The function
generate and generate_tree are convenient interfaces to rewrite and rewrite_tree
that accept a string (which defaults to 'S') as input."""

import random
from pprint import pprint
import sys, resource
from collections import defaultdict
import argparse                   # argparse is standard in 2.7

# A drawback of this simple recursive program is that, since python
# doesn't recognize tail recursion, deeply recursive programs can run
# out of stack space. Increase max stack size from 8MB to 16MB and
# recursion limit to 1M!  You may have to comment out these lines if
# you are on a mac and have not reset the limts.

try:
  resource.setrlimit(resource.RLIMIT_STACK, (2**24,-1))
  sys.setrecursionlimit(10**6)
except:
  pass
  # print "Can't increase stack"


def load_grammar(file):
    """Load a grammar from file and return it as a dictionary where
     keys are non-terminals and values are lists of possible
     rewrites, where each rewrite is a (possibly empty) list of
     symbols. Example: {'S':[('S','and','S'),('NP','VP')],...}"""
    grammar = defaultdict(list)
    for line in open(file):
        line = line.strip()
        # skip blank lines and lines beginning with hash
        if line and line[0] != '#':
            # line is like:  NP -> Art NP | Art Adj NP
            lhs, rhs = line.split('->')
            lhs = lhs.strip()
            rhs = tuple([alt.split() for alt in rhs.strip().split('|')])
            # add new RHS to LHS entry
            grammar[lhs].append(rhs)
    return grammar


def rewrite(g, tokens, into):
  """Replace tokens in list with a random entry in grammar g
  (recursively)."""
  for token in tokens:
    if token in g:
        rewrite(g, random.choice(g[token]), into)
    else:
        into.append(token)
  return into


def rewrite_tree(g, tokens, into):
  """Replace list of tokens into a random tree, chosen from grammar g"""
  for token in tokens:
    if token in g:
      into.append({token: rewrite_tree(g, random.choice(g[token]), [])})
    else:
      into.append(token)
  return into


def generate(g, start='S'):
  """Replace each token in str with random entry in grammar g, recurse"""
  return ' '.join(rewrite(g, (start,) , []))


def generate_tree(g, start='S'):
  """Use grammar g to rewrite the category cat.  returns something
  like a parse tree."""
  return rewrite_tree(g, [start], [])


# what to do if called as a script
if __name__ == "__main__":
    # process command line arguments
    parser = argparse.ArgumentParser(description='Generate a random string from a grammar')
    parser.add_argument('-t', action="store_true", default=False,
                         help='return sentence as a tree rather than a string')
    parser.add_argument('-g', action="store", dest="gfile", required=True,
                        help='A file path specifying the grammar')
    parser.add_argument('-s', action="store", dest="start", default="S",
                        help="The grammar's start symbol for the grammar, defaults to S")
    args = parser.parse_args()

    if args.t:
        pprint(generate_tree(load_grammar(args.gfile), args.start))
    else:
        print generate(load_grammar(args.gfile), args.start)

