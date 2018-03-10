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

Pretty simple:

    > mkpw -l16 -aAds
    t1zy-XxAP-KTn3-MLty

    > mkpw -l16 -aAd -c'*!?' -s
    Wf0E-?uDC-t6Vm-xSPQ

    > mkpw -l24 -a -s' '
    xfjw tbgq rfaw ihij bazv nvpt

The main arguments are `-l,--length=<num-of-pw-chars>`, which char categories to
include `-a` lowercase letters, `-A` uppercase letters, `-d` digits and `-c`
special chars, and `-s` to split the output into a more readable form.
