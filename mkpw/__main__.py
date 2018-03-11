#!/usr/bin/env python

import sys
import re
import os
import os.path
import string
import argparse
import math

import logging


from .mkpw import SplitSpec, generate_password
from . import __version__


class PresetAction(argparse.Action):
    def __init__(self, option_strings, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(PresetAction, self).__init__(option_strings, nargs=0, **kwargs)
    def __call__(self, parser, namespace, values=None, option_string=None):
        assert(not values)
        # set defaults for mobile
        self.setPreset(namespace)

class MobilePresetAction(PresetAction):
    def setPreset(self, args):
        args.length = 16
        args.alpha_lower = True
        args.alpha_upper = False
        args.chars = False
        args.digits = False
        args.split = SplitSpec('4: ')

class WebsitePresetAction(PresetAction):
    def setPreset(self, args):
        args.length = 24
        args.alpha_lower = True
        args.alpha_upper = True
        args.chars = False
        args.digits = True
        args.split = SplitSpec('') # default split

class ParanoidPresetAction(PresetAction):
    def setPreset(self, args):
        args.length = 64
        args.alpha_lower = True
        args.alpha_upper = True
        args.chars = True
        args.digits = True
        args.split = SplitSpec(None)
        args.in_entropy_rate = 0.1
        args.concentrate_randomness = True
        args.force_each_category = True



def main():

    # args parser & open entropy file

    parser = argparse.ArgumentParser(
        description="Generate a good password",
        epilog="""\
If none of -a, -A, -d, -c are specified, all categories are used. Otherwise only
the specified character categories are used.

Examples:

> mkpw -l24 -aAd -s  # same as mkpw -w
t1zy-XxAP-KTn3-MLty-91Bn-vaP2

> mkpw -l16 -aAd -c'*!?' -s
Wf0E-?uDC-t6Vm-xSPQ

> mkpw -m
xfjw tbgq rfaw ihij

Your results may vary :)
 
""",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    legroup = parser.add_argument_group('password options')
    legroup.add_argument('-l', '--length', type=int, default=14,
                         help='Number of characters (14)')
    legroup.add_argument('-e', '--entropy_file', type=str, default='/dev/random',
                         help='Entropy file (/dev/random)')
    
    pgroup = parser.add_argument_group('convenient presets')
    pgroup.add_argument('-m', '--mobile', action=MobilePresetAction,
                        help="Sets some defaults so that password is easy to enter on a "
                        "mobile phone's keyboard (short for:  -l16 -a -s' ' )")
    pgroup.add_argument('-w', '--website', action=WebsitePresetAction,
                        help="Sets some defaults so that password is pretty secure and "
                        "suitable for a website (short for:  -l24 -aAd -s ).")
    pgroup.add_argument('-p', '--paranoid', action=ParanoidPresetAction,
                        help="Sets some defaults so that password is paranoidly difficult "
                        "to guess, with many different characters "
                        "(short for:  -l64 -aAdc -f -C -E0.1 -s ).")

    cgroup = parser.add_argument_group('char options')
    cgroup.add_argument('-a', '--alpha', dest='alpha_lower', action='store_true', default=False,
                        help='include lowercase ascii letters')
    cgroup.add_argument('-A', '--ALPHA', dest='alpha_upper', action='store_true', default=False,
                        help='include uppercase ascii letters')
    cgroup.add_argument('-d', '--digits', dest='digits', action='store_true', default=False,
                        help='include digits')
    cgroup.add_argument('-c', '--chars', dest='chars', nargs='?', action='store', const=True, default=None,
                        help='include special characters (optional: specify special char list, don\'t forget'
                        ' to escape from shell, or leave argument empty to use default list)')
    cgroup.add_argument('-s', '--split', dest='split', nargs='?', action='store', type=SplitSpec, const=SplitSpec(''),
                        default=SplitSpec(None),
                        help='split the password into groups of 4 characters separated by a hyphen.  The hyphen '
                        'does not count towards the password length.  Possible option values are "<CHAR>" or '
                        '"<NUMBER>" or "<NUMBER>:<CHAR>", which replaces the hyphen with CHAR and/or replaces the '
                        'grouping length.')
    cgroup.add_argument('-f', '--force-each-category', dest='force_each_category', action='store_true',
                        default=False, help="Force at least one character from each included category. "
                        "Note that this doesn't necessarily make your password more secure (on the contrary, "
                        "even, it could reduce its entropy). But some websites insist on this.")
    
    rgroup = parser.add_argument_group('randomness concentration options')
    rgroup.add_argument('-C', '--concentrate-randomness', dest="concentrate_randomness",
                        action='store_true', default=True)
    rgroup.add_argument('-N', '--no-concentrate-randomness', dest="concentrate_randomness", action='store_false',
                        help="Enable or disable the randomness concentration step (enabled by default)")
    rgroup.add_argument('-E', '--in-entropy-rate', dest="in_entropy_rate",
                        action='store', default=0.6, type=float,
                        help="The entropy per bit of the randomness file or device which you're willing to assume")

    ogroup = parser.add_argument_group('other options')
    ogroup.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Show verbose output on how the password was generated (for debugging)')
    ogroup.add_argument('--help', action='help', help="Show this help information and exit")
    ogroup.add_argument('--version', action='version', version='mkpw version %s'%(__version__))

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    logger.debug("args are : %r", args)

    pw = generate_password(args)

    print(pw)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
