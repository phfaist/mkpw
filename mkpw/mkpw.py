#!/usr/bin/env python

import sys
import re
import os
import os.path
import string
import math
import hashlib
import collections

import logging



class RandomSourceConcentrator(object):
    def __init__(self, f, entropyrate=0.6):
        """
        Arguments:

          - `f`: a binary opened file-like object.  Needs to implement the method
            `f.read(nbytes)` which should return `bytes()`.

          - `entropyrate`: the amount of min-entropy per bit of the data read
            from the source `f` we are ready to assume.
        """
        self.f = f
        self.entropyrate = entropyrate
        self.buf = bytes()

    def read(self, n):
        """
        Return `n` bytes of concentrated randomness from the source given in the
        constructor.
        """

        logger = logging.getLogger(__name__ + "." + self.__class__.__name__ + ".read()")

        logger.debug("n = %d, current buf len = %d", n, len(self.buf))

        m = hashlib.sha512()

        while len(self.buf) < n:
            # collect some concentrated randomness into our buffer.
            #
            # need 2*bits/entropyrate bytes to ensure that at input to
            # concentrator has at least 2*bits entropy rate.  (See NIST SP
            # 800-90B, section 3.1.5; we use hash function sha512; I'm not sure
            # I read all of this correctly but sounds not too wrong)

            # increase the amount of concentrated randomness by m.digest_size:
            
            needbytes = math.ceil( 2 * m.digest_size / self.entropyrate )
            
            # read exactly needbytes from the entropy source
            inbytes = b''
            while len(inbytes) < needbytes:
                inbytes = self.f.read(needbytes-len(inbytes))

            m.update(inbytes)

            outbytes = m.digest()
            self.buf += outbytes

            logger.debug("Concentrated another %d -> %d bytes: %r -> %r",
                         needbytes, m.digest_size, inbytes, outbytes)
            
        readbytes = self.buf[:n]

        self.buf = self.buf[n:]

        logger.debug("read bytes: %r", readbytes)
        return readbytes
        


class RandomStreamIntRecoder(object):
    """
    Given a source of random data `f` (provided as a file stream), extract
    random integers in a given range.

    The object `f` only has to implement the call ``f.read(m)`` to read `m`
    bytes of random data.  Note that the buffer must be open in binary mode,
    i.e., the `f.read()` call must return bytes, not a (unicode) string.
    """
    def __init__(self, f):
        self.f = f
        self.bitsbuffer = 0
        self.bitsbufferlen = 0
        self.waste = 0
        self.wastesize = 0

    def getInt(self, n):
        """
        Return a random integer between `0` and `n-1`, included.

        This function works the following way:
    
        - ensure enough random bits in the long integer `bitsbuffer`. There are exactly
         `bitsbufferlen` random bits in there `(0-2**bitsbufferlen)`
    
        - to generate a random char, take `n_bits` from the bitsbuffer. Then:
          (a) If the number is inside `{0, ..., n-1}`, this defines a new password character.
          (b) Otherwise, we add this value minus `n` to the `waste`, and increase
              `wastesize` by exactly `2**n_bits-n`.

        - `waste` is used to collect the randomness that wasn't used because the charstr isn't
          necessarily a power of two of length. Because the "waste numbers" (b) are uniformly
          distributed, we can still use them. We make sure that at all times `waste` contains a
          uniformly random number `{0, ..., wastesize-1}`.
        """

        logger = logging.getLogger(__name__ + "." + self.__class__.__name__ + ".getInt()")

        if not n > 0:
            raise ValueError("getInt(): Expected n > 0")

        # random number to be generated
        x = 0

        # The number of random bits we need to have in order to be sure to be
        # able to generate a uniformly random number in {0, ..., n-1}
        #
        # This is ceiling(math.log(len(charstr))/math.log(2))
        #
        n_bits = int(math.ceil(math.log(n)/math.log(2)))

        # mask to get the weakest n_bits out of a number
        n_bits_mask = ((1 << n_bits) - 1)

        logger.debug('n=%d, n_bits=%d', n, n_bits)

        # attempt until we get out a random integer.
        while True:
            logger.debug('need more bits.')
            # first, see if we can recycle some bits from the waste:
            if (self.wastesize > 2):
                logger.debug('recycling waste: waste=%#x, wastesize=%#x=%d',
                             self.waste, self.wastesize, self.wastesize)
                minwastebits = int(math.floor(math.log(self.wastesize)/math.log(2)))
                twominwastebits = 2**minwastebits;
                # now, do the same thing as when getting a random char. See if the number is
                # in [0,2**minwastebits[: if the case, then those bits are added to the
                # bitsbuffer; otherwise, the waste is updated to the new waste :)
                if self.waste < twominwastebits:
                    self.bitsbuffer |= ( self.waste << self.bitsbufferlen )
                    self.bitsbufferlen += minwastebits
                    self.waste = 0
                    self.wastesize = 0
                    logger.debug('got more bits: bitsbuffer=%#x, bitsbufferlen=%d',
                                 self.bitsbuffer, self.bitsbufferlen)
                else:
                    # nothing new for the bitsbuffer, but we can further recycle the surplus waste:
                    self.waste -= twominwastebits
                    self.wastesize -= twominwastebits
                    logger.debug('out of luck; new waste=%#x, wastesize=%#x=%d',
                                 self.waste, self.wastesize, self.wastesize)

                # if we did anything with the waste, retry from the beginning of the while loop
                continue

            if (self.bitsbufferlen < n_bits):
                # if we don't have enough randomness to generate the random
                # number, get more randomness first.
                logger.debug('getting random bits from entropy file')

                # read 8 very random bytes
                dat = self.f.read(8)
                # dat is an array of 8 integers (bytes)
                logger.debug('dat=%s', ",".join(['%#x'%(c) for c in dat]))

                # add to bit buffer, in the high weight bits
                for c in dat:
                    self.bitsbuffer |=  (c << self.bitsbufferlen)
                    self.bitsbufferlen += 8
                    logger.debug('adding %#x: bitsbuffer=%#x, bitsbufferlen=%d',
                                 c, self.bitsbuffer, self.bitsbufferlen)

            if (self.bitsbufferlen < n_bits):
                # if we still don't have enough randomness to even attempt to
                # generate the random number, get more randomness first.
                continue
            
            # we now have enough randomness in bitsbuffer to attempt to generate the
            # requested random integer x

            # take the last n_bits and, if we hit inside {0, ..., n-1}, that's
            # the random number
            rn = self.bitsbuffer & n_bits_mask
            self.bitsbuffer >>= n_bits
            self.bitsbufferlen -= n_bits

            logger.debug('got rn=%#x=%d, now bitsbuffer=%#x, bitsbufferlen=%d',
                         rn, rn, self.bitsbuffer, self.bitsbufferlen)

            if rn < n:
                # indeed got a random integer
                x = rn
                logger.debug('got random integer: x=%s', x)
                return x

            # got waste.
            self.waste += (rn - n)
            self.wastesize += (2**n_bits - n)
            logger.debug('now waste=%#x=%d, wastesize=%d', self.waste, self.waste, self.wastesize)

            # repeat until we manage to extract an integer....

        raise RuntimeError("Congrats! You've just miraculously broke out of an infinite loop")




class SplitSpec(object):
    DEFAULT_NUM = 4
    DEFAULT_CHAR = '-'

    def __init__(self, s=None):
        if s is None:
            # no splitting
            self.num = 0
            self.char = ''
            return

        # parse specification

        items = s.split(':',1)
        if len(items) == 2:
            if len(items[0]):
                if not re.match(r'^\d+$', items[0]):
                    raise ValueError("Expected \"<NUMBER>:<CHAR>\", got \"%s\""%(s))
                self.num = int(items[0])
            else:
                self.num = SplitSpec.DEFAULT_NUM
            self.char = items[1]
            return

        if len(s) == 0:  # empty string
            # defaults
            self.num = SplitSpec.DEFAULT_NUM
            self.char = SplitSpec.DEFAULT_CHAR
            return

        # else, either a number or a char
        if re.match(r'^\d+$', s):
            self.num = int(s)
            self.char = SplitSpec.DEFAULT_CHAR
            return

        # else, it's a char:
        self.num = SplitSpec.DEFAULT_NUM
        self.char = s
        

default_special_chars = '!@#$%^&*()_+/-=[]{};:,.<>'

GeneratePasswordArgs = collections.namedtuple('GeneratePasswordArgs', [
    'length',
    'alpha_lower',
    'alpha_upper',
    'digits',
    'chars',
    'split',
    'force_each_category',
    'entropy_file',
    'concentrate_randomness',
    'in_entropy_rate'
    ])
    

def generate_password(args):

    logger = logging.getLogger(__name__ + ".generate_password()")

    f = None
    if args.entropy_file == '-':
        f = sys.stdin.buffer
    else:
        f = open(args.entropy_file, 'rb')

    if args.concentrate_randomness:
        fin = RandomSourceConcentrator(f, args.in_entropy_rate)
    else:
        fin = f

    rndgen = RandomStreamIntRecoder(fin)

    allchars = False
    if not (args.alpha_lower or args.alpha_upper or args.digits or args.chars):
        allchars = True

    pwcharcategories = {}
        
    if allchars or args.alpha_lower:
        pwcharcategories['ascii_lowercase'] = string.ascii_lowercase
    if allchars or args.alpha_upper:
        pwcharcategories['ascii_uppercase'] = string.ascii_uppercase
    if allchars or args.digits:
        pwcharcategories['digits'] = string.digits
    if allchars or args.chars:
        pwcharcategories['chars'] = args.chars if isinstance(args.chars, str) else default_special_chars

    logger.debug('pwcharcategories=%r', pwcharcategories)

    charlist = "".join(pwcharcategories.values())

    logger.debug('charlist=%s', charlist)

    # if we need at least one character per category (say m categories), then 1)
    # choose m distinct positions 2) at each of those positions, the random
    # choice will be restricted to that category
    force_categories = {} # { position-in-pw: category-name }
    if args.force_each_category:
        if len(pwcharcategories) > args.length:
            logger.error("Can't force one char per category, password too short (%d)!", args.length)
            raise ValueError("Can't force one char per category, password too short")
        else:
            avail_catpos_list = list(range(args.length))
            for cat in pwcharcategories.keys():
                # choose from available positions
                i = rndgen.getInt(len(avail_catpos_list))
                catpos = avail_catpos_list[i]
                del avail_catpos_list[i]
                force_categories[catpos] = cat
            # force_categories is now properly initialized

    pw = ''
    l = 0 # saved value of len(pw)
    while (l < args.length):
        if l in force_categories:
            # only choose from fixed category
            thischarlist = pwcharcategories[force_categories[l]]
        else:
            # use our charlist
            thischarlist = charlist

        x = rndgen.getInt(len(thischarlist))
        ch = thischarlist[x]
        logger.debug("got pw char: %r (x=%d from thischarlist=%r)", ch, x, thischarlist)

        pw += ch
        l += 1

            

    # potentially split the password into groups
    spl = args.split
    if spl.num > 0:
        pw = spl.char.join([pw[i:i+spl.num] for i in range(0, len(pw), spl.num)])

    return pw

