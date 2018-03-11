Minimal tool to generate random password
========================================

Install
-------

Run:

    > git clone https://github.com/phfaist/mkpw.git
    > cd mkpw
    > python setup.py sdist
    > pip install dist/mkpw-1.0.tar.gz

You will now have `mkpw` installed.


Run
---

Usage is pretty straightforward.

**Preset: website**

    > mkpw -w
    5bj8-nfZ3-dkvY-dn01-pCip-XJaW

**Preset: easy for mobile**

    > mkpw -m
    ocqa gquf avty wrrs

**Preset: paranoid**

    > mkpw -p
    x!Mu5%yZn$3%#z6[gNw&x#_>xG.=Q-.dY[CTAn]w!<sUPCJeSkJ0(:n,3R]XVpi%

**Further options:**

    > mkpw -l16 -aAds
    t1zy-XxAP-KTn3-MLty

    > mkpw -l16 -aAd -f -c'*!?'
    Wf0E?uDCt6VmxSPQ

    > mkpw -l24 -a -s' '
    xfjw tbgq rfaw ihij bazv nvpt
    
    > mkpw --help
    [...]

The main arguments are `-l,--length=<num-of-pw-chars>`, which char categories to
include `-a` lowercase letters, `-A` uppercase letters, `-d` digits and `-c`
special chars, and `-s` to split the output into a more readable form. Also use
option `-f` for sites which insist that you have at least one char of each
category. Run `mkpw --help` for more information.
