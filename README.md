Minimal tool to generate a random password
==========================================

Install
-------

Run:

```ShellSession
> git clone https://github.com/phfaist/mkpw.git
> cd mkpw
> python setup.py sdist
> pip install dist/mkpw-1.0.tar.gz
```

You will now have `mkpw` installed.


Run
---

Usage is pretty straightforward.

**Preset: for a website**

```ShellSession
> mkpw -w
5bj8-nfZ3-dkvY-dn01-pCip-XJaW
```

**Preset: easy for mobile input**

```ShellSession
> mkpw -m
ocqa gquf avty wrrs
```

**Preset: paranoid**

```ShellSession
> mkpw -p
+z<if0,BF_2&w,Bgg.K*!RW;0V.d@E,$43%LPR0-a$g#=em2b{t}<-(vDJ.@oeX_
```

**Further options:**

```ShellSession
> mkpw -aAd                   # -a, -A, -d: enable char categories
aEJlmCkZ442im9

> mkpw -aAd -s                # -s: split into chunks
e2VJ-nIGR-f5sk-yn

> mkpw -l16 -aAd -s           # -l: specify length
t1zy-XxAP-KTn3-MLty

> mkpw -l24 -a -s' '          # can specify separator char for -s
xfjw tbgq rfaw ihij bazv nvpt

> mkpw -c'*?+-_'              # -c: special chars category with given chars
+_+_--++*_*-??

> mkpw -l16 -aAd -c'*!?' -f   # -f: at least one char from each category
Wf0E?uDCt6VmxSPQ

> mkpw --help
[...]
```

The main arguments are `-l,--length=<num-of-pw-chars>`, which char categories to
include among `-a` lowercase letters, `-A` uppercase letters, `-d` digits and `-c`
special chars, and `-s` to split the output into a more readable form. Also use
option `-f` for sites which insist that you must have at least one char of each
category. Run `mkpw --help` for more information.
