# pylint: disable=W0223
# pylint: disable=C0103
# pylint: disable=W1514

"""module docstring"""

from collections import Counter


class AlignmentCounter(Counter):
    COUNT_HEADER_ELEMENTS = ["raw", "lnorm", "scaled"]

    @staticmethod
    def normalise_counts(counts, feature_len, scaling_factor):
        """Returns raw, length-normalised, and scaled feature counts."""
        normalised = counts / feature_len
        scaled = normalised * scaling_factor
        return counts, normalised, scaled

    def __init__(self, distribution_mode="uniq_only", strand_specific=False):
        Counter.__init__(self)
        self.distribution_mode = distribution_mode
        self.strand_specific = strand_specific
        self.unannotated_reads = 0

    def dump(self, prefix, bam):
        with open(f"{prefix}.{self.__class__.__name__}.tsv", "wt") as _out:
            for k, v in self.items():
                print(k, bam.get_reference(k)[0], v, sep="\t", file=_out)
