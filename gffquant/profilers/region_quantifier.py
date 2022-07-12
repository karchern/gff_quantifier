# pylint: disable=C0103

""" module docstring """

import logging

from gffquant.db.annotation_db import AnnotationDatabaseManager
from .feature_quantifier import FeatureQuantifier


logger = logging.getLogger(__name__)


class RegionQuantifier(FeatureQuantifier):
    # pylint: disable=R0913,R0801
    def __init__(
        self,
        db=None,
        out_prefix="gffquant",
        ambig_mode="uniq_only",
        strand_specific=False,
        calc_coverage=False,
        paired_end_count=1,
        unmarked_orphans=False,
    ):
        FeatureQuantifier.__init__(
            self,
            db=db,
            out_prefix=out_prefix,
            ambig_mode=ambig_mode,
            strand_specific=strand_specific,
            reference_type="genome",
            calc_coverage=calc_coverage,
            paired_end_count=paired_end_count,
            unmarked_orphans=unmarked_orphans,
        )
        self.adm = AnnotationDatabaseManager(self.db)

    def process_alignment_group(self, aln_group):
        logging.info("Processing new alignment group %s (%s)", aln_group.qname, aln_group.n_align())
        ambig_counts = list(aln_group.get_ambig_align_counts())
        if any(ambig_counts) and self.require_ambig_bookkeeping:
            all_hits = []
            for aln in aln_group.get_alignments():
                current_ref = self.alp.get_reference(aln.rid)[0]
                # how many other positons does this read align to?
                # this is needed in 1overN to scale down counts of multiple alignments
                ambig_count = ambig_counts[aln.is_second()]
                # if no overlaps: aln_count = 0
                # yield ({rid: hits}, aln_count, 0 if aln_count else 1)
                hit, _, unaligned = next(self.process_alignments_sameref(
                    current_ref, (aln.shorten(),), aln_count=ambig_count
                ))

                all_hits.append((aln, hit, unaligned))
                # correct for alignments in unannotated regions
                if unaligned:
                    ambig_counts[aln.is_second()] -= 1

            self.count_manager.update_counts(
                (
                    (hit, 0 if unaligned else ambig_counts[aln.is_second()], unaligned)
                    for aln, hit, unaligned in all_hits
                ),
                ambiguous_counts=True,
                pair=aln_group.is_paired()
            )
        elif aln_group.is_aligned_pair():
            current_ref = self.alp.get_reference(aln_group.primaries[0].rid)[0]
            hits = self.process_alignments_sameref(
                current_ref,
                (
                    aln_group.primaries[0].shorten(),
                    aln_group.primaries[1].shorten(),
                )
            )
            self.count_manager.update_counts(
                hits, ambiguous_counts=False, pair=True
            )
        else:
            for aln in aln_group.get_alignments():
                current_ref = self.alp.get_reference(aln.rid)[0]
                hits = self.process_alignments_sameref(
                    current_ref, (aln.shorten(),)
                )
                self.count_manager.update_counts(
                    hits, ambiguous_counts=not aln.is_unique(),
                    pair=aln_group.is_paired()
                )
