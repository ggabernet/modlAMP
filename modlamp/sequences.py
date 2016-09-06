# -*- coding: utf-8 -*-
"""
.. module:: modlamp.sequences

.. moduleauthor:: modlab Alex Mueller ETH Zurich <alex.mueller@pharma.ethz.ch>

This module incorporates different classes to generate peptide sequences with different characteristics from scratch.
The following classes are available:

============================        ===============================================================================
Class                               Characteristics
============================        ===============================================================================
:py:class:`Random`                  Generates random sequences with a specified amino acid distribution.
:py:class:`Helices`                 Generates presumed amphipathic helical sequences with a hydrophobic moment.
:py:class:`Kinked`                  Generates presumed amphipathic helices with a kink (Pro residue).
:py:class:`Oblique`                 Generates presumed oblique oriented sequences in presence of libid membranes.
:py:class:`Centrosymmetric`         Generates centrosymmetric sequences with a symmetry axis.
:py:class:`MixedLibrary`            Generates a mixed library of sequences of all other classes.
:py:class:`Hepahelices`             Generates presumed amphipathic helices with a heparin-binding-domain.
============================        ===============================================================================

.. note:: During the process of sequence generation, duplicates are only removed for the :py:class:`MixedLibrary` class.

"""

from numpy import random
from itertools import cycle

import numpy as np

from core import mutate_AA, aminoacids, clean, save_fasta, check_natural_aa, filter_unnatural, template, filter_aa, \
    filter_duplicates

__author__ = "modlab"
__docformat__ = "restructuredtext en"


class Random:
    """
    Class for random peptide sequences
    This class incorporates methods for generating peptide random peptide sequences of defined length.
    The amino acid probabilities can be chosen from different probabilities:

    - **rand**: equal probabilities for all amino acids
    - **AMP**: amino acid probabilities taken from the antimicrobial peptide database `APD3 <http://aps.unmc.edu/AP/statistic/statistic.php>`_, March 17, 2016, containing 2674 sequences.
    - **AMPnoCM**: same amino acid probabilities as **AMP** but lacking Cys and Met (for synthesizability)
    - **randnoCM**: equal probabilities for all amino acids, except 0.0 for both Cys and Met (for synthesizability)

    The probability values for all natural AA can be found in the following table:

    ===  ====    ======    =========    ==========
    AA   rand    AMP       AMPnoCM      randnoCM
    ===  ====    ======    =========    ==========
    A    0.05    0.0766    0.0812275    0.05555555
    C    0.05    0.071     0.0          0.0
    D    0.05    0.026     0.0306275    0.05555555
    E    0.05    0.0264    0.0310275    0.05555555
    F    0.05    0.0405    0.0451275    0.05555555
    G    0.05    0.1172    0.1218275    0.05555555
    H    0.05    0.021     0.0256275    0.05555555
    I    0.05    0.061     0.0656275    0.05555555
    K    0.05    0.0958    0.1004275    0.05555555
    L    0.05    0.0838    0.0884275    0.05555555
    M    0.05    0.0123    0.0          0.0
    N    0.05    0.0386    0.0432275    0.05555555
    P    0.05    0.0463    0.0509275    0.05555555
    Q    0.05    0.0251    0.0297275    0.05555555
    R    0.05    0.0545    0.0591275    0.05555555
    S    0.05    0.0613    0.0659275    0.05555555
    T    0.05    0.0455    0.0501275    0.05555555
    V    0.05    0.0572    0.0618275    0.05555555
    W    0.05    0.0155    0.0201275    0.05555555
    Y    0.05    0.0244    0.0290275    0.05555555
    ===  ====    ======    =========    ==========

    """

    def __init__(self, lenmin, lenmax, seqnum):
        """
        :param lenmin: minimal sequence length
        :param lenmax: maximal sequence length
        :param seqnum: number of sequences to generate
        :return: initialized class attributes for sequence number and length
        """
        aminoacids(self)
        template(self, lenmin, lenmax, seqnum)

    def generate_sequences(self, proba='rand'):
        """Method to actually generate the sequences.

        :param proba: AA probability to be used to generate sequences. Available: AMP, AMPnoCM, rand, randnoCM
        :return: A list of random AMP sequences with defined AA probabilities
        :Example:

        >>> r = Random(5,20,6)
        >>> r.generate_sequences(proba='AMP')
        >>> r.sequences
        ['CYGALWHIFV','NIVRHHAPSTVIK','LCPNPILGIV','TAVVRGKESLTP','GTGSVCKNSCRGRFGIIAF','VIIGPSYGDAEYA']
        """
        clean(self)
        self.prob = self.prob_rand  # default probability = rand
        if proba == 'AMPnoCM':
            self.prob = self.prob_AMPnoCM
        elif proba == 'AMP':
            self.prob = self.prob_AMP
        elif proba == 'randnoCM':
            self.prob = self.prob_randnoCM

        for s in range(self.seqnum):
            self.seq = []
            for l in range(random.choice(range(self.lenmin, self.lenmax + 1))):
                self.seq.append(np.random.choice(self.AAs,
                                                 p=self.prob))  # weighed random selection of amino acid, probabilities = prob
            self.sequences.append(''.join(self.seq))

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> H.sequences
        ['IAKAGRAIIK']
        >>> H.mutate_AA(3,1)
        >>> H.sequences
        ['NAKAGRAWIK']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)


class Helices:
    """Base class for peptide sequences probable to form helices.

    This class incorporates methods for generating presumed amphipathic alpha-helical peptide sequences.
    These sequences are generated by placing basic residues along the sequence with distance 3-4 AA to each other.
    The remaining empty spots are filled up by hydrophobic AAs.
    """

    def __init__(self, lenmin, lenmax, seqnum):
        """
        :param lenmin: minimal sequence length
        :param lenmax: maximal sequence length
        :param seqnum: number of sequences to generate
        :return: defined variables as instances
        """
        aminoacids(self)
        template(self, lenmin, lenmax, seqnum)

    def generate_helices(self):
        """Method to generate amphipathic helical sequences with class features defined in :class:`Helices()`

        :return: In the attribute :py:attr:`sequences`: a list of sequences with presumed amphipathic helical structure.
        :Example:

        >>> h = Helices(7,21,5)
        >>> h.generate_helices()
        >>> h.sequences
        ['KGIKVILKLAKAGVKAVRL','IILKVGKV','IAKAGRAIIK','LKILKVVGKGIRLIVRIIKAL','KAGKLVAKGAKVAAKAIKI']
        """
        clean(self)
        for s in range(self.seqnum):  # for the number of sequences to generate
            seq = ['X'] * random.choice(range(self.lenmin, self.lenmax + 1))
            basepos = random.choice(range(4))  # select spot for first basic residue from 0 to 3
            seq[basepos] = random.choice(self.AA_basic)  # place first basic residue
            gap = cycle([3, 4]).next  # gap cycle of 3 & 4 --> 3,4,3,4,3,4...
            g = gap()
            while g + basepos < len(
                    seq):  # place more basic residues 3-4 positions further (changing between distance 3 and 4)
                basepos += g
                seq[basepos] = random.choice(self.AA_basic)  # place more basic residues
                g = gap()  # next gap

            for p in range(len(seq)):
                while seq[p] == 'X':  # fill up remaining spots with hydrophobic AAs
                    seq[p] = random.choice(self.AA_hyd)

            self.sequences.append(''.join(seq))

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> H.sequences
        ['IAKAGRAIIK']
        >>> H.mutate_AA(3,1)
        >>> H.sequences
        ['NAKAGRAWIK']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)


class Kinked:
    """
    Base class for peptide sequences probable to form helices with a kink.
    This class incorporates methods for presumed kinked amphipathic alpha-helical peptide sequences:
    Sequences are generated by placing basic residues along the sequence with distance 3-4 AA to each other.
    The remaining spots are filled up by hydrophobic AAs. Then, a basic residue is replaced by proline, presumably
    leading to a kink in the hydrophobic face of the amphipathic helices.
    """

    def __init__(self, lenmin, lenmax, seqnum, ):
        """
        :param lenmin: minimal sequence length
        :param lenmax: maximal sequence length
        :param seqnum: number of sequences to generate
        :return: defined attributes :py:attr:`lenmin`, :py:attr:`lenmax` and :py:attr:`seqnum`
        """
        aminoacids(self)
        template(self, lenmin, lenmax, seqnum)

    def generate_kinked(self):
        """Method to actually generate the presumed kinked sequences with features defined in the class instances.

        :return: sequence list with strings stored in the attribute :py:attr:`sequences`
        :Example:

        >>> k = Kinked(7,28,8)
        >>> k.generate_kinked()
        >>> k.sequences
        ['IILRLHPIG','ARGAKVAIKAIRGIAPGGRVVAKVVKVG','GGKVGRGVAFLVRIILK','KAVKALAKGAPVILCVAKVI',
        'IGIRVWRAVIKVIPVAVRGLRL','RIGRVIVPVIRGL','AKAARIVAMLAR','LGAKGWRLALKGIPAAIKLGKV']
        """
        clean(self)
        for s in range(self.seqnum):  # for the number of sequences to generate
            poslist = []  # used to
            seq = ['X'] * random.choice(range(self.lenmin, self.lenmax + 1))
            basepos = random.choice(range(4))  # select spot for first basic residue from 0 to 3
            seq[basepos] = random.choice(self.AA_basic)  # place first basic residue
            poslist.append(basepos)
            gap = cycle([3, 4]).next  # gap cycle of 3 & 4 --> 3,4,3,4,3,4...
            g = gap()
            while g + basepos < len(
                    seq):  # place more basic residues 3-4 positions further (changing between distance 3 and 4)
                basepos += g
                seq[basepos] = random.choice(self.AA_basic)  # place more basic residues
                g = gap()  # next gap
                poslist.append(basepos)

            for p in range(len(seq)):
                while seq[p] == 'X':  # fill up remaining spots with hydrophobic AAs
                    seq[p] = random.choice(self.AA_hyd)

            # place proline around the middle of the sequence
            propos = poslist[len(poslist) / 2]
            seq[propos] = 'P'

            self.sequences.append(''.join(seq))

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> S.sequences
        ['IAKAGRAIIK']
        >>> S.mutate_AA(3,1)
        >>> S.sequences
        ['NAKAGRAWIK']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)


class Oblique(object):
    """Base class for oblique sequences with a so called linear hydrophobicity gradient.

    This class incorporates methods for generating peptide sequences with a linear hydrophobicity gradient, meaning that
    these sequences have a hydrophobic tail. This feature gives rise to the hypothesis that they orient themselves
    tilted/oblique in membrane environment.
    """

    def __init__(self, lenmin, lenmax, seqnum):
        """
        :param lenmin: minimal sequence length
        :param lenmax: maximal sequence length
        :param seqnum: number of sequences to generate
        :return: defined attributes :py:attr:`lenmin`, :py:attr:`lenmax` and :py:attr:`seqnum`
        """
        aminoacids(self)
        template(self, lenmin, lenmax, seqnum)

    def generate_oblique(self):
        """Method to generate the possible oblique sequences.

        :return: A list of sequences in the attribute :py:attr:`sequences`.
        :Example:

        >>> o = Oblique(10,30,4)
        >>> o.generate_oblique()
        >>> o.sequences
        ['GLLKVIRIAAKVLKVAVLVGIIAI','AIGKAGRLALKVIKVVIKVALILLAAVA','KILRAAARVIKGGIKAIVIL','VRLVKAIGKLLRIILRLARLAVGGILA']
        """
        clean(self)
        for s in range(self.seqnum):  # for the number of sequences to generate
            seq = ['X'] * random.choice(range(self.lenmin, self.lenmax + 1))
            basepos = random.choice(range(4))  # select spot for first basic residue from 0 to 3
            seq[basepos] = random.choice(self.AA_basic)  # place first basic residue
            gap = cycle([3, 4]).next  # gap cycle of 3 & 4 --> 3,4,3,4,3,4...
            g = gap()
            while g + basepos < len(
                    seq):  # place more basic residues 3-4 positions further (changing between distance 3 and 4)
                basepos += g
                seq[basepos] = random.choice(self.AA_basic)  # place more basic residues
                g = gap()  # next gap

            for p in range(len(seq)):
                while seq[p] == 'X':  # fill up remaining spots with hydrophobic AAs
                    seq[p] = random.choice(self.AA_hyd)

            for e in range(1, len(
                    seq) / 3):  # transform last 3rd of sequence into hydrophobic ones --> hydrophobicity gradient = oblique
                seq[-e] = random.choice(self.AA_hyd)

            self.sequences.append(''.join(seq))

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> H.sequences
        ['IAKAGRAIIK']
        >>> H.mutate_AA(3,1)
        >>> H.sequences
        ['NAKAGRAWIK']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)


class Centrosymmetric:
    """Base class for peptide sequences produced out of 7 AA centro-symmetric blocks yielding peptides of length
    14 or 21 AA (2*7 or 3*7).

    This class incorporates methods to generate special peptide sequences with an overall presumed
    hydrophobic moment. Sequences are generated by centro-symmetric blocks of seven amino acids. Two or three blocks
    are added to build a final sequence of length 14 or 21 amino acids length. If the method :func:`generate_symmetric()`
    is used, two or three identical blocks are concatenated. If the method :func:`generate_asymmetric()` is used,
    two or three different blocks are concatenated.
    """

    def __init__(self, seqnum=1):
        """
        :param seqnum: number of sequences to generate
        :return: defined number of sequences to generate, empty list to store produced sequences
        """
        aminoacids(self)
        self.seqnum = int(seqnum)

    def generate_symmetric(self):
        """The :func:`generate_symmetric()` method generates overall symmetric sequences out of two or three blocks of
        identical centro-symmetric sequence blocks of 7 amino acids. The resulting sequence presumably has a large
        hydrophobic moment.

        :return: In the attribute :py:attr:`sequences`: centro-symmetric peptide sequences of the form [h,+,h,a,h,+,h] with
            h = hydrophobic AA, + = basic AA, a = anchor AA (F,Y,W,(P)), sequence length is 14 or 21 AA
        :Example:

        >>> s = Centrosymmetric(5)
        >>> s.generate_symmetric()
        >>> s.sequences
        ['ARIFIRAARIFIRA','GRIYIRGGRIYIRGGRIYIRG','IRGFGRIIRGFGRIIRGFGRI','GKAYAKGGKAYAKG','AKGYGKAAKGYGKAAKGYGKA']
        """
        clean(self)
        for s in range(self.seqnum):  # iterate over number of sequences to generate
            n = random.choice(range(2, 4))  # number of sequence blocks to take (2 or 3)
            seq = ['X'] * 7  # template sequence AA list with length 7
            for a in range(7):  # generate symmetric sequence block of 7 AA with an anchor in the middle
                if a == 0:
                    seq[0] = random.choice(self.AA_hyd)
                    seq[6] = seq[0]
                elif a == 1:
                    seq[1] = random.choice(self.AA_basic)
                    seq[5] = seq[1]
                elif a == 2:
                    seq[2] = random.choice(self.AA_hyd)
                    seq[4] = seq[2]
                elif a == 3:
                    seq[3] = random.choice(self.AA_anchor)
                else:
                    continue
            self.sequences.append(''.join(seq) * n)

    def generate_asymmetric(self):
        """The :func:`generate_asymmetric()` method generates overall asymmetric sequences out of two or three blocks of
        different centro-symmetric sequence blocks of 7 amino acids. The resulting sequence presumably has a large
        hydrophobic    moment.

        :return: In the attribute :py:attr:`sequences`: a list of peptide sequences as strings of length 14 or 21
        :Example:

        >>> S = Centrosymmetric(5)
        >>> S.generate_asymmetric()
        >>> S.sequences
        ['GRLFLRGAKGFGKAVRVWVRV','IKGWGKILKLYLKL','LKAYAKLVKAWAKVLRLFLRL','IRLWLRIIKAFAKI','LRIFIRLVKLWLKVIRLWLRI']
        """
        clean(self)
        for s in range(self.seqnum):  # iterate over number of sequences to generate
            n = random.choice(range(2, 4))  # number of sequence blocks to take (2 or 3)
            seq = ['X'] * 7  # template sequence AA list with length 7
            self.blocks = list()
            for c in range(n):
                for a in range(7):  # generate symmetric sequence block of 7 AA with an anchor in the middle
                    if a == 0:
                        seq[0] = random.choice(self.AA_hyd)
                        seq[6] = seq[0]
                    elif a == 1:
                        seq[1] = random.choice(self.AA_basic)
                        seq[5] = seq[1]
                    elif a == 2:
                        seq[2] = random.choice(self.AA_hyd)
                        seq[4] = seq[2]
                    elif a == 3:
                        seq[3] = random.choice(self.AA_anchor)
                    else:
                        continue
                self.blocks.append(''.join(seq))
            self.sequences.append(''.join(self.blocks))

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> S.sequences
        ['IAKAGRAIIK']
        >>> S.mutate_AA(3,1)
        >>> S.sequences
        ['NAKAGRAWIK']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)


class MixedLibrary:
    """Base class for holding a virtual peptide library.

    This class :class:`MixedLibrary` incorporates methods to generate a virtual peptide library composed out of different
    sub-libraries. The available library subtypes are all from the classes :class:`Centrosymmetric`, :class:`Helices`,
    :class:`Kinked`, :class:`Oblique` or :class:`Random`.
    """

    def __init__(self, number, centrosymmetric=1, centroasymmetric=1, helix=1, kinked=1, oblique=1, rand=1, randAMP=1,
                 randAMPnoCM=1):
        """initializing method of the class :class:`MixedLibrary`. Except from **number**, all other parameters are
        ratios of sequences of the given sequence class.

        :param number: number of sequences to be generated
        :param centrosymmetric: ratio of symmetric centrosymmetric sequences in the library
        :param centroasymmetric: ratio of asymmetric centrosymmetric sequences in the library
        :param helix: ratio of amphipathic helical sequences in the library
        :param kinked: ratio of kinked amphipathic helical sequences in the library
        :param oblique: ratio of oblique oriented amphipathic helical sequences in the library
        :param rand: ratio of random sequneces in the library
        :param randAMP: ratio of random sequences with APD2 amino acid distribution in the library
        :param randAMPnoCM: ratio of random sequences with APD2 amino acid distribution without Cys and Met in the library

        .. warning::
            If duplicate sequences are created, these are removed during the creation process. It is therefore quite
            probable that you will not get the exact size of library that you entered as the parameter **number**. If you
            generate a small library, it can also happen that the size is bigger than expected, because ratios are rounded.
        """
        self.names = []
        self.sequences = []
        self.libsize = int(number)
        norm = float(sum((centrosymmetric, centroasymmetric, helix, kinked, oblique, rand, randAMP, randAMPnoCM)))
        self.ratios = {'sym': float(centrosymmetric) / norm, 'asy': float(centroasymmetric) / norm,
                       'hel': float(helix) / norm, 'knk': float(kinked) / norm, 'obl': float(oblique) / norm,
                       'ran': float(rand) / norm, 'AMP': float(randAMP) / norm, 'nCM': float(randAMPnoCM) / norm}
        self.nums = {'sym': int(round(float(self.libsize) * self.ratios['sym'], ndigits=0)),
                     'asy': int(round(float(self.libsize) * self.ratios['asy'], ndigits=0)),
                     'hel': int(round(float(self.libsize) * self.ratios['hel'], ndigits=0)),
                     'knk': int(round(float(self.libsize) * self.ratios['knk'], ndigits=0)),
                     'obl': int(round(float(self.libsize) * self.ratios['obl'], ndigits=0)),
                     'ran': int(round(float(self.libsize) * self.ratios['ran'], ndigits=0)),
                     'AMP': int(round(float(self.libsize) * self.ratios['AMP'], ndigits=0)),
                     'nCM': int(round(float(self.libsize) * self.ratios['nCM'], ndigits=0))}

    def generate_library(self):
        """This method generates a virtual sequence library with the subtype ratios initialized in class :class:`MixedLibrary()`.
        All sequences are between 7 and 28 amino acids in length.

        :return: a virtual library of sequences in the attribute :py:attr:`sequences`, the sub-library class names in
            :py:attr:`names`, the number of sequences generated for each class in :py:attr:`nums` and the library size in
            :py:attr:`libsize`.
        :Example:

        >>> lib = MixedLibrary(10000,centrosymmetric=5,centroasymmetric=5,helix=3,kinked=3,oblique=2,rand=10,
        randAMP=10,randAMPnoCM=5)
        >>> lib.generate_library()
        >>> lib.libsize  # as duplicates were present, the library does not have the size that was sepecified
        9126
        >>> lib.sequences
        ['RHTHVAGSWYGKMPPSPQTL','MRIKLRKIPCILAC','DGINKEVKDSYGVFLK','LRLYLRLGRVWVRG','GKLFLKGGKLFLKGGKLFLKG',...]
        >>> lib.nums
        {'AMP': 2326,
        'asy': 1163,
        'hel': 698,
        'knk': 698,
        'nCM': 1163,
        'obl': 465,
        'ran': 2326,
        'sym': 1163}
        """
        Cs = Centrosymmetric(self.nums['sym'])
        Cs.generate_symmetric()
        Ca = Centrosymmetric(self.nums['asy'])
        Ca.generate_asymmetric()
        H = Helices(7, 28, self.nums['hel'])
        H.generate_helices()
        K = Kinked(7, 28, self.nums['knk'])
        K.generate_kinked()
        O = Oblique(7, 28, self.nums['obl'])
        O.generate_oblique()
        R = Random(7, 28, self.nums['ran'])
        R.generate_sequences('rand')
        Ra = Random(7, 28, self.nums['AMP'])
        Ra.generate_sequences('AMP')
        Rc = Random(7, 28, self.nums['nCM'])
        Rc.generate_sequences('AMPnoCM')

        # TODO: update libnums according to real numbers

        sequences = Cs.sequences + Ca.sequences + H.sequences + K.sequences + O.sequences + R.sequences + Ra.sequences + Rc.sequences
        names = ['sym'] * self.nums['sym'] + ['asy'] * self.nums['asy'] + ['hel'] * self.nums['hel'] + \
                ['knk'] * self.nums['knk'] + ['obl'] * self.nums['obl'] + ['ran'] * self.nums['ran'] + \
                ['AMP'] * self.nums['AMP'] + ['nCM'] * self.nums['nCM']
        # combining sequence and name to remove duplicates
        comb = []
        for i, s in enumerate(sequences):
            comb.append(s + '_' + names[i])
        comb = set(comb)
        # remove duplicates
        for c in comb:
            self.sequences.append(c.split('_')[0])
            self.names.append(c.split('_')[1])
        # update libsize and nums
        self.libsize = len(self.sequences)
        self.nums = {k: self.names.count(k) for k in self.nums.keys()}  # update the number of sequences for every class

    def prune_library(self, newsize):
        """Method to cut down a library to the given new size.

        :param newsize: new desired size of the mixed library
        :return: adapted library with corresponding attributes (sequences, names, libsize, nums)
        """
        self.names = self.names[:newsize]
        self.sequences = self.sequences[:newsize]
        self.libsize = len(self.sequences)
        self.nums = {k: self.names.count(k) for k in self.nums.keys()}  # update the number of sequences for every class

    def save_fasta(self, filename, names=False):
        """Method to save generated sequences in a .fasta formatted file.

        :param filename: output filename in which the sequences from :py:attr:`sequences` are safed in fasta format.
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a fasta file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)


class Hepahelices:
    """Base class for peptide sequences probable to form helices and include a heparin-binding-domain.

    This class is used to construct presumed amphipathic helices that include a heparin-binding-domain (HBD)
    probable to bind heparin. The HBD sequence for alpha-helices usually has the following form: **XBBBXXBX**
    (B: basic AA; X: hydrophobic, uncharged AA, with mainly Ser & Gly).

    More on the HBD: Munoz, E. M. & Linhardt, R. J. Heparin-Binding Domains in Vascular Biology. *Arterioscler. Thromb.
    Vasc. Biol.* **24**, 1549–1557 (2004).

    .. versionadded:: v2.3.1
    """

    def __init__(self, lenmin, lenmax, seqnum):
        """
        :param lenmin: minimal sequence length, minimal 8!
        :param lenmax: maximal sequence length, maximal 50!
        :param seqnum: number of sequences to generate
        :return: defined variables as instances
        """
        aminoacids(self)
        if lenmin < 8 or lenmax > 50:
            print "Wrong sequence length.\nMinimum: 8\nMaximum: 50"
        else:
            template(self, lenmin, lenmax, seqnum)

    def generate_sequences(self):
        """Method to generate helical sequences with class features defined in :class:`Hepahelices()`

        :return: In the attribute :py:attr:`sequences`: a list of sequences including a heparin-binding-domain.
        :Example:

        >>> h = Hepahelices(8,21,10)  # minimal length: 8, maximal length: 50
        >>> h.generate_sequences()
        >>> h.sequences
        ['GRLARSLKRKLNRLVRGGGRLVRGGG', 'IRSIRRRLSKLARSLGRGARSLGRG', 'RAVKRKVNKLLKGAAKVLKGAAKVLKGAAK', ... ]
        """
        clean(self)
        for s in range(self.seqnum):  # for the number of sequences to generate
            # generate heparin binding domain with the from HBBBHPBH (H: hydrophobic, B: basic, P: polar)
            hbd = [random.choice(self.AA_hyd)] + [random.choice(self.AA_basic)] + [random.choice(self.AA_basic)] + \
                  [random.choice(self.AA_basic)] + [random.choice(self.AA_hyd)] + [random.choice(self.AA_polar)] + \
                  [random.choice(self.AA_basic)] + [random.choice(self.AA_hyd)]
            # generate amphipathic block to add in front of HBD
            bef = [random.choice(self.AA_hyd)] + [random.choice(['A', 'G'])] + [random.choice(self.AA_basic)] + \
                  [random.choice(self.AA_hyd)] + [random.choice(self.AA_hyd)] + [random.choice(self.AA_basic)] + \
                  [random.choice(['A', 'G', 'S', 'T'])]
            # generate amphipathic block to add after HBD
            aft = [random.choice(self.AA_hyd)] + [random.choice(self.AA_basic)] + \
                  [random.choice(['A', 'G', 'S', 'T'])] + [random.choice(self.AA_hyd)] + \
                  [random.choice(['A', 'G'])] + [random.choice(self.AA_basic)] + [random.choice(self.AA_hyd)]
            l = random.choice(range(self.lenmin, self.lenmax + 1))  # total sequence length
            try:
                r = l - 8  # remaining empty positions in sequence
                b = random.choice(r)  # positions before HBD
                a = r - b  # positions after HBD
                seq = 3 * bef + hbd + 3 * aft
                seq = seq[21 - b: 29 + a]
            except ValueError:  # if sequence length is 8, take HBD as whole sequence
                seq = hbd

            self.sequences.append(''.join(seq))

    def mutate_AA(self, nr, prob):
        """Method to mutate with **prob** probability a **nr** of positions per sequence randomly.

        :param nr: number of mutations to perform per sequence
        :param prob: probability of mutating a sequence
        :return: In the attribute :py:attr:`sequences`: mutated sequences
        :Example:

        >>> h.sequences
        ['IRSIRRRLSKLARSLGRGARSLGRG']
        >>> h.mutate_AA(3,1)
        >>> h.sequences
        ['IRSIRRRKSKLARQLGRGFRSLGRG']

        .. seealso:: :func:`modlamp.core.mutate_AA()`
        """
        mutate_AA(self, nr, prob)

    def save_fasta(self, filename, names=False):
        """Method for saving sequences in the instance :py:attr:`sequences` to a file in FASTA format.

        :param filename: output filename (ending .fasta)
        :param names: {bool} whether sequence names from :py:attr:`names` should be saved as sequence identifiers
        :return: a FASTA formatted file containing the generated sequences

        .. seealso:: :func:`modlamp.core.save_fasta()`
        """
        save_fasta(self, filename, names=names)

    def check_natural_aa(self):
        """Method to filter out sequences that do not contain natural amino acids. If the sequence contains a character
        that is not in ['A','C','D,'E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'].

        :return: filtered sequence list in the attribute :py:attr:`sequences`. The other attributes are also filtered
            accordingly.

        .. seealso:: :func:`modlamp.core.check_natural_aa()`

        .. versionadded:: v2.2.5
        """
        check_natural_aa(self)

    def filter_unnatural(self):
        """Method to filter out sequences with unnatural amino acids from :py:attr:`sequences`.

        :return: Filtered sequence list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_unnatural()`
        """
        filter_unnatural(self)

    def filter_duplicates(self):
        """Method to filter duplicates in the sequences from the class attribute :py:attr:`sequences`

        :return: filtered sequences list in the attribute :py:attr:`sequences`

        .. seealso:: :func:`modlamp.core.filter_sequences()`

        .. versionadded:: v2.2.5
        """
        filter_duplicates(self)

    def filter_aa(self, aminoacids):
        """Method to filter out sequences with given amino acids in the argument list *aminoacids*.
        **Dublicates** sequences are removed as well.

        :param aminoacids: list of amino acids to be filtered
        :return: filtered list of sequences in the attribute :py:attr:`sequences`.

        .. seealso:: :func:`modlamp.core.filter_aa()`
        """
        filter_aa(self, aminoacids=aminoacids)

