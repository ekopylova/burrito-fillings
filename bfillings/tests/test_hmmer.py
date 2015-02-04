#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2015--, biocore development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
Unit tests for HMMER v. 3.1b1 Application controller
====================================================
"""


from unittest import TestCase, main
from os import close
from os.path import exists, join
from tempfile import mkstemp, mkdtemp
from shutil import rmtree
from itertools import islice

from skbio.util import remove_files

from bfillings.hmmer import (run_nhmmer)


# Test class and cases
class hmmerTests(TestCase):
    """ Tests for HMMER v. 3.1b1 functionality """

    def setUp(self):
        self.output_dir = mkdtemp()
        self.bac_ssu_hmm = bac_ssu_hmm
        self.fasta_with_count_info = fasta_with_count_info

        # create a temporary bac SSU HMM profile
        f, self.file_bac_ssu_hmm_fp = mkstemp(prefix='temp_bac_ssu_',
                                              suffix='.hmm')
        close(f)

        # write HMM profile to file
        with open(self.file_bac_ssu_hmm_fp, 'w') as tmp:
            tmp.write(self.bac_ssu_hmm)
        tmp.close()

        # create a temporary reads file
        f, self.file_fasta_with_count_info_fp = mkstemp(prefix='temp_reads_',
                                                        suffix='.fasta')
        close(f)

        # write reads to file
        with open(self.file_fasta_with_count_info_fp, 'w') as tmp:
            tmp.write(self.fasta_with_count_info)
        tmp.close()

        # list of files to remove
        self.files_to_remove = [self.file_bac_ssu_hmm_fp,
                                self.file_fasta_with_count_info_fp]

    def tearDown(self):
        remove_files(self.files_to_remove)
        rmtree(self.output_dir)

    def test_run_nhmmer_default(self):
        """ Test functionality of run_nhmmer method
            using default settings
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")

        app_result = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath)

        self.assertTrue(exists(output_filepath))

        # Check the statistics summary in the output file
        with open(output_filepath, 'U') as output_f:
            num_seqs = 0
            num_hits = 0
            for line in output_f:
                if line.startswith("Target sequences:"):
                    num_seqs = int(line.split()[2])
                elif line.startswith("Total number of hits:"):
                    num_hits = int(line.split()[4])

            # check correct number of input sequences
            self.assertEquals(num_seqs, 40)
            # check correct number of valid 16S sequences
            self.assertEquals(num_hits, 34)

    def test_run_nhmmer_acc_off(self):
        """ Test functionality of run_nhmmer method
            without preferring accessions over names in output
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")

        app_result = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath,
            acc=False)

        # Check the statistics summary in the output file
        with open(output_filepath, 'U') as output_f:
            num_seqs = 0
            num_hits = 0
            for line in output_f:
                if line.startswith("Target sequences:"):
                    num_seqs = int(line.split()[2])
                elif line.startswith("Total number of hits:"):
                    num_hits = int(line.split()[4])

            # check correct number of input sequences
            self.assertEquals(num_seqs, 40)
            # check correct number of valid 16S sequences
            self.assertEquals(num_hits, 34)

    def test_run_nhmmer_noali_off(self):
        """ Test functionality of run_nhmmer method
            with output alignments
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")

        app_result = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath,
            noali=False)

        expected_alignment =\
            ['    score  bias    Evalue   hmmfrom    hmm to     alifrom    ali to      envfrom    env to    sq len      acc\n',
             '   ------ ----- ---------   -------   -------    --------- ---------    --------- --------- ---------    ----\n',
             ' !  115.2   5.8     2e-37       627       773 ..         1       147 [.         1       149 [.       150    0.99\n',
             '\n', '  Alignment:\n', '  score: 115.2 bits\n',
             '               bac_ssu 627 tacgtagggtgcaagcgttatccggaattactgggcgtaaagggcgcgtaggcggtttgttaagtcagatgtgaaagccccgggctcaa 715\n',
             '                           tacgtagggtgcaagcgtta +cggaattactgggcgtaaag g+gcg+aggcggttt+ +aag c gatgtgaaa+ccccgggct+aa\n',
             '  19896_65019;size=36;   1 TACGTAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGAGTGCGCAGGCGGTTTTGCAAGACCGATGTGAAATCCCCGGGCTTAA 89 \n',
             '                           69*************************************************************************************** PP\n',
             '\n', '               bac_ssu 716 cctgggaactgcatttgaaactggcagactagagtgcgggagaggaaagtggaattcc 773\n',
             '                           cctgggaactgcatt g  actg  ag ctagagtg+g  agagg a gtggaattcc\n',
             '  19896_65019;size=36;  90 CCTGGGAACTGCATTGGTGACTGCAAGGCTAGAGTGTGTCAGAGGGAGGTGGAATTCC 147\n',
             '                           ********************************************************98 PP\n']

        # Check the statistics summary in the output file
        with open(output_filepath, 'U') as output_f:
            num_seqs = 0
            num_hits = 0
            for line in output_f:
                if line.startswith("Target sequences:"):
                    num_seqs = int(line.split()[2])
                elif line.startswith("Total number of hits:"):
                    num_hits = int(line.split()[4])
                elif line.startswith(">> 19896_65019;size=36;"):
                    next_alignment = list(islice(output_f, 15))
                    next_alignment.sort()
                    expected_alignment.sort()
                    self.assertEquals(next_alignment, expected_alignment)

            # check correct number of input sequences
            self.assertEquals(num_seqs, 40)
            # check correct number of valid 16S sequences
            self.assertEquals(num_hits, 34)

    def test_run_nhmmer_evalue_set(self):
        """ Test functionality of run_nhmmer method
            with different E-value than default (1e-5)
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")

        app_result = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath,
            evalue=1e-35)

        # Check the statistics summary in the output file
        with open(output_filepath, 'U') as output_f:
            num_seqs = 0
            num_hits = 0
            for line in output_f:
                if line.startswith("Target sequences:"):
                    num_seqs = int(line.split()[2])
                elif line.startswith("Total number of hits:"):
                    num_hits = int(line.split()[4])

            # check correct number of input sequences
            self.assertEquals(num_seqs, 40)
            # check correct number of sequences passing E-value
            self.assertEquals(num_hits, 3)

    def test_run_nhmmer_tblout(self):
        """ Test functionality of run_nhmmer method
            with the output of a parseable table of hits
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")
        tblout_filepath = join(self.output_dir, "nhmmer_tblout.txt")

        app_result = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath,
            tblout_filepath=tblout_filepath)

        # Some of the expected alignments
        expected_alignments = {'19896_65019;size=36;':
            ['-', 'bac_ssu', '-', '627', '773', '1', '147', '1', '149', '150', '+', '2e-37', '115.2', '5.8', '-'],
            '19896_435217;size=12;':
            ['-', 'bac_ssu', '-', '627', '776', '1', '149', '1', '150', '150', '+', '4.7e-32', '97.4', '4.7', '-'],
            '19896_629329;size=48;':
            ['-', 'bac_ssu', '-', '627', '773', '1', '147', '1', '150', '150', '+', '7.3e-24', '70.2', '5.9', '-']}

        # All expected failures (phiX reads and other non-16S rRNA)
        expected_failures = ['19896_4809454;size=2;', '19896_3785700;size=2;',
                             '19896_1979752;size=2;', '19896_824354;size=17;',
                             '19896_1305222;size=2;', '19896_11113011;size=2;']

        actual_alignments = {}

        # Load actual alignments into dict
        with open(tblout_filepath, 'U') as table_out_f:
            for line in table_out_f:
                if line.startswith('#'):
                    continue
                alignment = line.strip().split()
                self.assertTrue(alignment[0] not in actual_alignments)
                actual_alignments[alignment[0]] = alignment[1:]

        self.assertEquals(len(actual_alignments), 34)

        # Check expected alignments have been found
        for expected_alignment in expected_alignments:
            self.assertTrue(expected_alignment in actual_alignments)

        # Check none of the failures are in the
        # actual alignments
        for expected_failure in expected_failures:
            self.assertFalse(expected_failure in actual_alignments)

        # Check the statistics summary in the output file
        with open(output_filepath, 'U') as output_f:
            num_seqs = 0
            num_hits = 0
            for line in output_f:
                if line.startswith("Target sequences:"):
                    num_seqs = int(line.split()[2])
                elif line.startswith("Total number of hits:"):
                    num_hits = int(line.split()[4])

            # check correct number of input sequences
            self.assertEquals(num_seqs, 40)
            # check correct number of valid 16S sequences
            self.assertEquals(num_hits, 34)

    def test_run_nhmmer_report_artifacts(self):
        """ Test functionality of run_nhmmer method
            when reporting artifacts
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")
        tblout_filepath = join(self.output_dir, "nhmmer_tblout.txt")

        app_result, actual_artifacts = run_nhmmer(
            fasta_filepath=self.file_fasta_with_count_info_fp,
            profile_hmm=self.file_bac_ssu_hmm_fp,
            output_filepath=output_filepath,
            tblout_filepath=tblout_filepath,
            report_artifacts=True)

        self.assertEquals(len(actual_artifacts), 6)

        expected_artifacts = ['19896_4809454;size=2;', '19896_3785700;size=2;',
                              '19896_1979752;size=2;', '19896_824354;size=17;',
                              '19896_1305222;size=2;',
                              '19896_11113011;size=2;']

        expected_artifacts.sort()
        actual_artifacts.sort()

        self.assertEquals(expected_artifacts, actual_artifacts)

    def test_negative_threads(self):
        """ run_nhmmer should fail with a negative value
            for threads
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")
        self.assertRaises(ValueError,
                          run_nhmmer,
                          fasta_filepath=self.file_fasta_with_count_info_fp,
                          profile_hmm=self.file_bac_ssu_hmm_fp,
                          output_filepath=output_filepath,
                          threads=-1)

    def test_output_artifacts(self):
        """ run_nhmmer should fail if report_artifacts is set but a path for
            a parseable table output is not provided
        """
        output_filepath = join(self.output_dir, "nhmmer_results.txt")
        self.assertRaises(ValueError,
                          run_nhmmer,
                          fasta_filepath=self.file_fasta_with_count_info_fp,
                          profile_hmm=self.file_bac_ssu_hmm_fp,
                          output_filepath=output_filepath,
                          tblout_filepath=None,
                          report_artifacts=True)


# Demultiplexed, quality filtered, split on sample ids, trimmed and
# dereplicated + singleton removed reads which are passed to the
# deblurring artifact removal step.
# Total reads: 40
# PhiX reads: 3
#    19896_4809454;size=2; 19896_3785700;size=2; 19896_1979752;size=2;
# other non-16S rRNA reads: 3 human DNA related
#    19896_4809454;size=2; 19896_3785700;size=2; 19896_1979752;size=2;
#    19896_11113011;size=2; 19896_1305222;size=2; 19896_824354;size=17;
fasta_with_count_info = """>19896_691;size=2674;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCTTTGGAAACTGTTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_15821;size=1224;
TACGGAGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGTGACTTAAGTGAGGTGTGAAAGCCC
CGGGCTTAACCTGGGAATTGCATTTCATACTGGGTCGCTAGAGTACTTTAGGGAGGGGTAGAATTCCACG
>19896_27435;size=1009;
TACGTAGGGTGCGAGCGTTAATCGGAATTACTGGGCGTAAAGCGAGCGCAGACGGTTACTTAAGCAGGATGTGAAATCCC
CGGGCTCAACCTGGGAACTGCGTTCTGAACTGGGTGACTAGAGTGTGTCAGAGGGAGGTAGAATTCCACG
>19896_12254;size=533;
TACGTATGTCACAAGCGTTATCCGGATTTATTGGGCGTAAAGCGCGTCTAGGTGGTTATGTAAGTCTGATGTGAAAATGC
AGGGCTCAACTCTGTATTGCGTTGGAAACTGCATGACTAGAGTACTGGAGAGGTAAGCGGAACTACAAGT
>19896_315414;size=83;
TACGTAGGTGGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGCGCGCGCAGGTGGTTTAATAAGTCTGATGTGAAAGCCC
ACGGCTCAACCGTGGAGGGTCATTGGAAACTGTTAAACTTGAGTGCAGGAGAGAAAAGTGGAATTCCTAG
>19896_253137;size=63;
TACGTAGGTGGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGCGCGCGCAGGCGGATCAGTTAGTCTGTCTTAAAAGTTC
GGGGCTTAACCCCGTGATGGGATGGAAACTGCTGATCTAGAGTATCGGAGAGGAAAGTGGAATTCCTAGT
>19896_351297;size=60;
TACGGAGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGTGACTTAAGTGAGATGTGAAAGCCC
CGGGCTTAACCTGGGAATTGCATTTCATACTGGGTCGCTAGAGTACTTTAGGGAGGGGTAGAATTCCACG
>19896_121543;size=57;
TACGTAGGTGGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGCGCGCGCAGGCGGATAGGTCAGTCTGTCTTAAAAGTTC
GGGGCTTAACCCCGTGATGGGATGGAAACTGCCAATCTAGAGTATCGGAGAGGAAAGTGGAATTCCTAGT
>19896_99223;size=56;
TACGTAGGTCCCGAGCGTTATCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCTTTGGAAACTGTTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_12252;size=51;
TACGTATGTCACAAGCGTTATCCGGATTTATTGGGCGTAAAGCGCGTCTAGGTGGTTATGTAAGTCTGATGTGAAAATGC
AGGGCTCAACTCTGTATTGCGTTGGAAACTGTGTAACTAGAGTACTGGAGAGGTAAGCGGAACTACAAGT
>19896_629329;size=48;
TACGGAAGGTCCAGGCGTTATCCGGATTTATTGGGTTTAAAGGGTGCGTAGGCCGTTTGATAAGCGTGCTGTGAAATATA
GTGGCTCAACCTCTATCGTGCAGCGCGAACTGTTGAACTTGAGTGCGTAGTAGGTAGGCGGAATTCGTGG
>19896_205485;size=41;
TACGGGGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGTGACTTAAGTGAGGTGTGAAAGCCC
CGGGCTTAACCTGGGAATTGCATTTCATACTGGGTCGCTAGAGTACTTTAGGGAGGGGTAGAATTCCACG
>19896_65019;size=36;
TACGTAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGAGTGCGCAGGCGGTTTTGCAAGACCGATGTGAAATCCC
CGGGCTTAACCTGGGAACTGCATTGGTGACTGCAAGGCTAGAGTGTGTCAGAGGGAGGTGGAATTCCGCA
>19896_984939;size=18;
TACGGAAGGTCCAGGCGTTATCCGGATTTATTGGGTTTAAAGGGTGCGTAGGCCGTTTGATAAGCGTGCTGTGAAATATA
GTGGCTCAACCTCTATCGTGCAGCGCGAACTGTCGAACTTGAGTGCGTAGTAGGTAGGCGGAATTCGTGG
>19896_824354;size=17;
CACGATTAACCCAAGTCAATAGAAGCCGGCGTAAAGAGTGTTTTAGATCACCCCCTCCCCAATAAAGCTAAAACTCACCT
GAGTTGTAAAAAACTCCAGTTGACACAAAATAGACTACGAAAGTGGCTTTAACATATCTGAACACACAAT
>19896_261786;size=16;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTATGCTTTGGAAACTGTTTAACTTGAGTGCAGAAGGGGAGAGTGGAATTCCATGT
>19896_51178;size=15;
TACGGAGGGTGCAAGCGTTACTCGGAATCACTGGGCGTAAAGGACGCGTAGGCGGATTATCAAGTCTCTTGTGAAATCTA
ACGGCTTAACCGTTAAACTGCTTGAGAAACTGATAATCTAGAGTAAGGGAGAGGCAGATGGAATTCTTGG
>19896_468624;size=15;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCTTTGGAGACTGTTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_1824356;size=15;
TACGTATGTCACGAGCGTTATCCGGATTTATTGGGCGTAAAGCGCGTCTAGGTGGTTATATAAGTCTGATGTGAAAATGC
AGGGCTCAACTCTGTATTGCGTTGGAAACTGTATAACTAGAGTACTGGAGAGGTAAGCGGAACTACAAGT
>19896_191076;size=15;
TACGTAGGTGGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGCGCGCGCAGGCGGATCAGTCAGTCTGTCTTAAAAGTTC
GGGGCTTAACCCCGTGATGGGATGGAAACTGTTGATCTAGAGTATCGGAGAGGAAAGTGGAATTCCTAGT
>19896_62553;size=15;
TACGGAGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGACTTTTAAGTGAGGTGTGAAATCCC
CGGGCTTAACCTGGGAATTGCATTTCAGACTGGGAGTCTAGAGTACTTTAGGGAGGGGTAGAATTCCACG
>19896_674151;size=15;
TACGTAGGGAGCGAGCGTTATCCGGATTTATTGGGTGTAAAGGGTGCGTAGACGGAAATGCAAGTTAGTTGTGAAATACC
TCGGCTTAACTGAGGAACTGCAACTAAAACTATATTTCTTGAGTATCGGAGGGGTTTGTGGAATTCCTAG
>19896_2273161;size=12;
TACGTATGTCACGAGCGTTATCCGGATTTATTGGGCGTAAAGCGCGTCTAGGTGGTTATGTAAGTCTGATGTGAAAATGC
AGGGCTCAACTCTGTATTGCGTTGGAAACTGCATGACTAGAGTACTGGAGAGGTAAGCGGAACTACAAGT
>19896_516577;size=12;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCCTTGGAAACTGTTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_435217;size=12;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGCGTCTAGGTGGTTATGTAAGTCTGATGTGAAAATGC
AGGGCTCAACTCTGTATTGCGTTGGAAACTGCATGACTAGAGTACTGGAGAGGTAAGCGGAACTACAAGT
>19896_820001;size=12;
TACGGAGGATGCGAGCGTTATCCGGAATCATTGGGTTTAAAGGGTCCGTAGGCGGGCTAATAAGTCAGAGGTGAAAGCGC
TCAGCTCAACTGAGCAACTGCCTTTGAAACTGTTAGTCTTGAATGGTTGTGAAGTAGTTGGAATGTGTAG
>19896_1019112;size=11;
TACGGAGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGTGACTTAAGTGAGGTGTGAAAGCCC
CGGGCTTAACCTGGGGATTGCATTTCATACTGGGTCGCTAGAGTACTTTAGGGAGGGGTAGAATTCCACG
>19896_1245913;size=11;
TACGTATGTCGCGAGCGTTATCCGGAATTATTGGGCATAAAGGGCATCTAGGCGGCCTTTCAAGTCAGGGGTGAAAACCT
GCGGCTCAACCGCAGGCCTGCCTTTGAAACTGATAGGCTGGAGTACCGGAGAGGTGGACGGAACTGCACG
>19896_1896249;size=11;
TACGTAGGGCGCGAGCGTTGTCCGGAATTATTGGGCGTAAAGAGCTCGTAGGCGGCTGGTCGCGTCTGTCGTGAAATCCT
CTGGCTTAACTGGGGGCTTGCGGTGGGTACGGGCCGGCTTGAGTGCGGTAGGGGAGACTGGAACTCCTGG
>19896_1080052;size=11;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAGGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCTTTGGAAACTGTTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_1008972;size=10;
TACGGAGGGTGCGAGCGTTAATCGGAATAACTGGGCGTAAAGGGCACGCAGGCGGTTATTTAAGTGAGGTGTGAAAGCCC
CGGGCTTAACCTGGGAATTGCATTTCAGACTGGGTAACTAGAGTACTTTAGGGAGGGGGAGAATTCCACG
>19896_5750778;size=9;
TACGTAGGGTGCGAGCGTTAATCGGAATTACTGGGCGTAAAGCGGGCGCAGACGGTTACTTAAGCAGGATGTGAAATCCC
CGGGCTCAACCTGGGAACTGCGTTCTGAACTGGGTGACTAGAGTGTGTCAGAGGGAGGTAGGATTCCACG
>19896_3226853;size=9;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTTAGATAAGTCTGAAGTTAAAGGCT
GTGGCTTAACCATAGTACGCTTTGGAAACTGCTTAACTTGAGTGCAAGAGGGGAGAGTGGAATTCCATGT
>19896_2607532;size=9;
TACGGAGGGTGCAAGCGTTACTCGGAATCACTGGGCGTAAAGGACGCGTAGGCGGATTATCAAGTCTCTTGTGAAATCCT
ATGGCTTAACCATAGAACTGCTTGGGAAACTGATAATCTAGAGTGAGGGAGAGGCAGATGGAATTGGTGG
>19896_2797701;size=9;
TACGTAGGTCCCGAGCGTTGTCCGGATTTATTGGGCGTAAAGCGAGCGCAGGCGGTCAATTAAGTCTGATGTGAAAGCCC
CCGGCTCAACCGGGGAGGGTCATTGGAAACTGGTTGACTTGAGTGCAGAAGAGGAGAGTGGAATTCCATG
>19896_11113011;size=2;
CACGATTAACCCAAGTCAATAGAAACCGGCATAAAGAGTGTTTTAGATCAATTCCCCTCAATAAAGCTAAAATTCACGTG
AGTTGTAAAAAACTCCAGTTGATACAAAATAAACTACGAAAGTGGCTTTAATGCATCTGAACACAGAATA
>19896_4809454;size=2;
GCAGTAGTAATTCCTGCTTTATCAAGATAATTTTTCGACTCATCAGAAATATCCGAAAGTGTTAACTTCTGCGTCATGGA
AGCGATAAAACTCTGCAGGTTGGATACGCCAATCATTTTTATCGAAGCGCGCATAAATTTGAGCAGATTT
>19896_3785700;size=2;
TCCAGCTTCTTCGGCACCTGTTTTACAGACACCTAAAGCTACATCGTCAACGTTATATTTTGATAGTTTGACGGTTAATG
CTGGTAATGGTGGTTTTCTTCATTGCATTCAGATGGATACATCTGTCAACGCCGCTAATCAGGTTGTTTC
>19896_1305222;size=2;
GTTTTAATTTTTGTAGAGAAGGAGTCTTGCTATGTTGCCCAGGCTGGTCTCAAACTCCTGGGCTCAAGCAATCTGCCTGC
CTTGGCCTCATAAAGTGCTAGGATTACAGGCGTAAGCCACCATGCCAAGCCACCTTCTTTTGATTTTTAC
>19896_1979752;size=2;
TACTAAATGCCGCGGATTGGTTTCGCTGAATCAGGTTATTAAAGAGATTATTTGTCTCCAGCCACTTAAGTGAGGTGATT
TATGTTTGGTGCTATTGCTGGCGGTATTGCTTCTGCTCTTGCTGGTGGCGCCATGTCTAAATTGTTTGGA
"""

# HMM profile for 16S bacterial SSU taken from Meta_RNA
# (http://weizhong-lab.ucsd.edu/meta_rna/)
# See paper:
# Ying Huang, Paul Gilna and Weizhong Li. "Identification of ribosomal RNA
# genes in metagenomic fragments". Bioinformatics (2009) 25:1338-1340
bac_ssu_hmm = """HMMER3/b [3.0 | March 2010]
NAME  bac_ssu
LENG  1739
ALPH  DNA
RF    no
CS    no
MAP   yes
DATE  Wed Aug 11 12:06:51 2010
NSEQ  636
EFFN  2.625092
CKSUM 2382231757
STATS LOCAL MSV      -13.2346  0.69455
STATS LOCAL VITERBI  -14.2839  0.69455
STATS LOCAL FORWARD   -7.3871  0.69455
HMM          A        C        G        T   
            m->m     m->i     m->d     i->m     i->i     d->m     d->d
  COMPO   1.36705  1.47195  1.23543  1.49188
          1.38629  1.38629  1.38629  1.38629
          0.09531  3.09104  3.09104  1.46634  0.26236  0.00000        *
      1   1.26637  1.51815  1.33161  1.44827      4 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      2   1.35871  1.52193  1.23560  1.45219      5 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      3   1.35871  1.52193  1.23560  1.45219      6 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      4   1.40618  1.44840  1.38773  1.30810      7 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      5   1.40618  1.44840  1.38773  1.30810      8 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      6   1.35871  1.52193  1.23560  1.45219      9 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      7   1.40618  1.44840  1.38773  1.30810     10 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      8   1.40618  1.44840  1.38773  1.30810     11 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
      9   1.40618  1.44840  1.38773  1.30810     12 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     10   1.40618  1.44840  1.38773  1.30810     13 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     11   1.35871  1.52193  1.23560  1.45219     14 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     12   1.26637  1.51815  1.33161  1.44827     15 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     13   1.26637  1.51815  1.33161  1.44827     16 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     14   1.26637  1.51815  1.33161  1.44827     17 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     15   1.40878  1.35999  1.38997  1.38705     18 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     16   1.26637  1.51815  1.33161  1.44827     19 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     17   1.26637  1.51815  1.33161  1.44827     20 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     18   1.40878  1.35999  1.38997  1.38705     21 - -
          1.38629  1.38629  1.38629  1.38629
          0.09364  3.10786  3.10786  1.46634  0.26236  1.09861  0.40547
     19   1.38461  1.51094  1.27133  1.39264     22 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     20   1.26840  1.55294  1.27943  1.47448     23 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     21   1.38567  1.46105  1.27212  1.43710     24 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     22   1.29498  1.50758  1.36503  1.38919     25 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     23   1.43132  1.44686  1.41937  1.25937     26 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     24   1.29498  1.50758  1.36503  1.38919     27 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     25   1.36310  1.55461  1.18909  1.47682     28 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     26   1.43132  1.44686  1.41937  1.25937     29 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     27   1.40251  1.48266  1.33208  1.33538     30 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     28   1.43618  1.35625  1.42450  1.33214     31 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     29   1.43132  1.44686  1.41937  1.25937     32 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     30   1.40251  1.48266  1.33208  1.33538     33 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     31   1.43132  1.44686  1.41937  1.25937     34 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     32   1.38461  1.51094  1.27133  1.39264     35 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     33   1.29498  1.50758  1.36503  1.38919     36 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     34   1.21983  1.54855  1.33801  1.47056     37 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     35   1.21983  1.54855  1.33801  1.47056     38 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     36   1.26840  1.55294  1.27943  1.47448     39 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     37   1.40467  1.39653  1.33382  1.41211     40 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     38   1.43505  1.39255  1.42352  1.29979     41 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     39   1.30634  1.55455  1.23998  1.47615     42 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     40   1.30634  1.55455  1.23998  1.47615     43 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     41   1.29498  1.50758  1.36503  1.38919     44 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     42   1.43132  1.44686  1.41937  1.25937     45 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     43   1.21983  1.54855  1.33801  1.47056     46 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     44   1.35283  1.39480  1.38819  1.41024     47 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     45   1.38461  1.51094  1.27133  1.39264     48 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     46   1.29498  1.50758  1.36503  1.38919     49 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     47   1.21983  1.54855  1.33801  1.47056     50 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     48   1.40251  1.48266  1.33208  1.33538     51 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     49   1.29498  1.50758  1.36503  1.38919     52 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     50   1.40467  1.39653  1.33382  1.41211     53 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     51   1.35283  1.39480  1.38819  1.41024     54 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     52   1.26840  1.55294  1.27943  1.47448     55 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     53   1.43132  1.44686  1.41937  1.25937     56 - -
          1.38629  1.38629  1.38629  1.38629
          0.09270  3.11749  3.11749  1.46634  0.26236  1.09861  0.40547
     54   1.45978  1.39216  1.45464  1.25285     57 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     55   1.29631  1.49272  1.31248  1.45866     58 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     56   1.32187  1.50107  1.39639  1.33567     59 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     57   1.46254  1.30806  1.45707  1.32769     60 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     58   1.36977  1.58566  1.14575  1.50042     61 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     59   1.45525  1.44795  1.44939  1.21438     62 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     60   1.37839  1.34501  1.41960  1.40377     63 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     61   1.22249  1.58224  1.28741  1.49608     64 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     62   1.17651  1.57724  1.34660  1.49174     65 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     63   1.37496  1.47835  1.41660  1.28519     66 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     64   1.45978  1.39216  1.45464  1.25285     67 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     65   1.42953  1.42695  1.36658  1.32591     68 - -
          1.38629  1.38629  1.38629  1.38629
          0.09177  3.12720  3.12720  1.46634  0.26236  1.09861  0.40547
     66   1.18394  1.56155  1.35448  1.48705     69 - -
          1.38629  1.38629  1.38629  1.38629
          0.09154  3.12955  3.12955  1.46634  0.26236  1.09861  0.40547
     67   1.41579  1.43384  1.36795  1.33088     70 - -
          1.38629  1.38629  1.38629  1.38629
          0.09136  3.13142  3.13142  1.46634  0.26236  1.09861  0.40547
     68   1.34924  1.52164  1.32044  1.36574     71 - -
          1.38629  1.38629  1.38629  1.38629
          0.09136  3.13142  3.13142  1.46634  0.26236  1.09861  0.40547
     69   1.35388  1.52070  1.32559  1.35651     72 - -
          1.38629  1.38629  1.38629  1.38629
          0.09136  3.13142  3.13142  1.46634  0.26236  1.09861  0.40547
     70   1.47333  1.32063  1.47085  1.29411     73 - -
          1.38629  1.38629  1.38629  1.38629
          0.09136  3.13142  3.13142  1.46634  0.26236  1.09861  0.40547
     71   1.39052  1.42370  1.43431  1.30213     74 - -
          1.38629  1.38629  1.38629  1.38629
          0.09119  3.13320  3.13320  1.46634  0.26236  1.09861  0.40547
     72   1.41908  1.64411  1.12008  1.43286     75 - -
          1.38629  1.38629  1.38629  1.38629
          0.08470  3.20387  3.20387  1.46634  0.26236  1.09861  0.40547
     73   1.52799  1.19488  1.54586  1.31991     76 - -
          1.38629  1.38629  1.38629  1.38629
          0.08451  3.20597  3.20597  1.46634  0.26236  1.09861  0.40547
     74   1.49939  1.13329  1.60774  1.36876     77 - -
          1.38629  1.38629  1.38629  1.38629
          0.08440  3.20722  3.20722  1.46634  0.26236  1.09861  0.40547
     75   1.39736  1.70003  1.06594  1.48869     78 - -
          1.38629  1.38629  1.38629  1.38629
          0.08417  3.20987  3.20987  1.46634  0.26236  1.09861  0.40547
     76   1.53744  1.19673  1.56913  1.29221     79 - -
          1.38629  1.38629  1.38629  1.38629
          0.08328  3.22010  3.22010  1.46634  0.26236  1.09861  0.40547
     77   1.52455  1.19396  1.57565  1.30052     80 - -
          1.38629  1.38629  1.38629  1.38629
          0.08311  3.22204  3.22204  1.46634  0.26236  1.09861  0.40547
     78   1.06425  1.65030  1.41292  1.51601     81 - -
          1.38629  1.38629  1.38629  1.38629
          0.08300  3.22322  3.22322  1.46634  0.26236  1.09861  0.40547
     79   1.44557  1.64065  1.14499  1.37710     82 - -
          1.38629  1.38629  1.38629  1.38629
          0.08266  3.22718  3.22718  1.46634  0.26236  1.09861  0.40547
     80   1.46173  1.49785  1.51230  1.12654     83 - -
          1.38629  1.38629  1.38629  1.38629
          0.08266  3.22718  3.22718  1.46634  0.26236  1.09861  0.40547
     81   1.38622  1.70324  1.02742  1.56084     84 - -
          1.38629  1.38629  1.38629  1.38629
          0.08255  3.22849  3.22849  1.46634  0.26236  1.09861  0.40547
     82   1.42122  1.53327  1.60266  1.07472     85 - -
          1.38629  1.38629  1.38629  1.38629
          0.08255  3.22849  3.22849  1.46634  0.26236  1.09861  0.40547
     83   1.40005  1.66380  1.03959  1.55876     86 - -
          1.38629  1.38629  1.38629  1.38629
          0.08255  3.22849  3.22849  1.46634  0.26236  1.09861  0.40547
     84   1.52088  1.17125  1.58937  1.31884     87 - -
          1.38629  1.38629  1.38629  1.38629
          0.08246  3.22956  3.22956  1.46634  0.26236  1.09861  0.40547
     85   1.51491  1.46577  1.59140  1.06238     88 - -
          1.38629  1.38629  1.38629  1.38629
          0.08234  3.23094  3.23094  1.46634  0.26236  1.09861  0.40547
     86   1.44931  1.49860  1.15553  1.48308     89 - -
          1.38629  1.38629  1.38629  1.38629
          0.08214  3.23330  3.23330  1.46634  0.26236  1.09861  0.40547
     87   1.43010  1.67134  0.99453  1.59542     90 - -
          1.38629  1.38629  1.38629  1.38629
          0.08214  3.23330  3.23330  1.46634  0.26236  1.09861  0.40547
     88   1.04565  1.76945  1.26993  1.62324     91 - -
          1.38629  1.38629  1.38629  1.38629
          0.08208  3.23400  3.23400  1.46634  0.26236  1.09861  0.40547
     89   1.05908  1.60261  1.47387  1.50141     92 - -
          1.38629  1.38629  1.38629  1.38629
          0.08167  3.23879  3.23879  1.46634  0.26236  1.09861  0.40547
     90   1.50397  1.52763  1.60531  1.02199     93 - -
          1.38629  1.38629  1.38629  1.38629
          0.08160  3.23964  3.23964  1.46634  0.26236  1.09861  0.40547
     91   1.58303  1.48812  1.61420  0.99479     94 - -
          1.38629  1.38629  1.38629  1.38629
          0.08146  3.24127  3.24127  1.46634  0.26236  1.09861  0.40547
     92   1.55071  1.07949  1.58469  1.41419     95 - -
          1.38629  1.38629  1.38629  1.38629
          0.08138  3.24216  3.24216  1.46634  0.26236  1.09861  0.40547
     93   1.29555  1.71464  1.05288  1.62307     96 - -
          1.38629  1.38629  1.38629  1.38629
          0.08112  3.24520  3.24520  1.46634  0.26236  1.09861  0.40547
     94   1.31265  1.68899  1.07725  1.58154     97 - -
          1.38629  1.38629  1.38629  1.38629
          0.08048  3.25290  3.25290  1.46634  0.26236  1.09861  0.40547
     95   1.40637  1.28820  1.50268  1.35997     98 - -
          1.38629  1.38629  1.38629  1.38629
          0.08003  3.25821  3.25821  1.46634  0.26236  1.09861  0.40547
     96   1.51863  1.54277  1.53033  1.04772     99 - -
          1.38629  1.38629  1.38629  1.38629
          0.07813  3.28131  3.28131  1.46634  0.26236  1.09861  0.40547
     97   1.48471  1.54245  1.58988  1.03388    100 - -
          1.38629  1.38629  1.38629  1.38629
          0.07436  3.32896  3.32896  1.46634  0.26236  1.09861  0.40547
     98   1.45204  1.58841  1.39122  1.16192    101 - -
          1.38629  1.38629  1.38629  1.38629
          0.07107  3.37263  3.37263  1.46634  0.26236  1.09861  0.40547
     99   1.50245  1.34949  1.70580  1.08941    102 - -
          1.38629  1.38629  1.38629  1.38629
          0.06492  3.46010  3.46010  1.46634  0.26236  1.09861  0.40547
    100   1.22329  1.59682  1.59754  1.20130    103 - -
          1.38629  1.38629  1.38629  1.38629
          0.06366  3.47900  3.47900  1.46634  0.26236  1.09861  0.40547
    101   1.07071  1.65704  1.43673  1.47478    104 - -
          1.38629  1.38629  1.38629  1.38629
          0.06329  3.48458  3.48458  1.46634  0.26236  1.09861  0.40547
    102   1.28860  1.55541  1.44663  1.28056    105 - -
          1.38629  1.38629  1.38629  1.38629
          0.06320  3.48597  3.48597  1.46634  0.26236  1.09861  0.40547
    103   1.55953  1.33501  1.78166  1.02652    106 - -
          1.38629  1.38629  1.38629  1.38629
          0.06257  3.49571  3.49571  1.46634  0.26236  1.09861  0.40547
    104   1.71724  1.81449  0.97832  1.26736    107 - -
          1.38629  1.38629  1.38629  1.38629
          0.05865  3.55848  3.55848  1.46634  0.26236  1.09861  0.40547
    105   1.48441  1.68732  0.95855  1.58523    108 - -
          1.38629  1.38629  1.38629  1.38629
          0.05569  3.60875  3.60875  1.46634  0.26236  1.09861  0.40547
    106   0.24748  2.74987  2.47268  2.64594    109 - -
          1.38629  1.38629  1.38629  1.38629
          0.04410  3.83647  3.83647  1.46634  0.26236  1.09861  0.40547
    107   2.65927  3.22504  0.16915  3.08209    110 - -
          1.38629  1.38629  1.38629  1.38629
          0.04440  3.85740  3.80270  1.46634  0.26236  1.09861  0.40547
    108   0.19668  3.07152  2.52760  2.94990    111 - -
          1.38669  1.38427  1.38536  1.38887
          0.04621  3.77723  3.80421  1.34678  0.30121  1.06248  0.42403
    109   2.66931  3.27138  0.16265  3.14997    113 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87489  3.87489  1.46634  0.26236  1.05182  0.42971
    110   2.78163  2.41903  2.85618  0.23374    114 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    111   2.80028  2.42338  2.87145  0.23071    115 - -
          1.38629  1.38629  1.38629  1.38629
          0.04389  3.87641  3.80679  1.46634  0.26236  1.09861  0.40547
    112   2.78125  2.40419  2.85546  0.23551    116 - -
          1.38501  1.38745  1.38745  1.38527
          0.04340  3.82980  3.87492  1.40983  0.27996  1.05274  0.42922
    113   2.73596  3.29478  0.15560  3.16551    122 - -
          1.38629  1.38629  1.38629  1.38629
          0.04300  3.87641  3.84624  1.46634  0.26236  1.09861  0.40547
    114   0.18799  3.07383  2.61631  2.95538    123 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87578  3.87578  1.46634  0.26236  1.07860  0.41562
    115   2.82052  2.42561  2.87801  0.22846    124 - -
          1.38687  1.38458  1.38687  1.38687
          0.04283  3.85381  3.87641  1.43770  0.27112  1.09861  0.40547
    116   2.66160  0.28181  2.72840  2.20345    126 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    117   1.52938  0.70034  2.07524  1.82396    127 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    118   2.82973  2.43124  2.87533  0.22735    128 - -
          1.38730  1.38730  1.38730  1.38327
          0.04321  3.83677  3.87641  1.41655  0.27780  1.09861  0.40547
    119   2.74260  3.31070  0.15323  3.18998    130 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    120   2.75009  3.29308  0.15387  3.18076    132 - -
          1.38629  1.38629  1.38629  1.38629
          0.04273  3.87641  3.85834  1.46634  0.26236  1.09861  0.40547
    121   3.07955  0.18487  3.14903  2.52680    133 - -
          1.38629  1.38629  1.38629  1.38629
          0.04383  3.87604  3.81003  1.46634  0.26236  1.08660  0.41153
    122   2.82233  2.42760  2.86334  0.22915    134 - -
          1.38629  1.38629  1.38629  1.38629
          0.04295  3.87500  3.84948  1.46634  0.26236  1.12110  0.39441
    123   3.10316  0.18010  3.15583  2.56001    135 - -
          1.38629  1.38629  1.38629  1.38629
          0.04242  3.87446  3.87446  1.46634  0.26236  1.06348  0.42350
    124   0.18041  3.12773  2.63381  3.00685    137 - -
          1.38629  1.38629  1.38629  1.38629
          0.04405  3.87588  3.80067  1.46634  0.26236  1.10719  0.40120
    125   2.72160  3.29803  0.15600  3.17690    138 - -
          1.38629  1.38629  1.38629  1.38629
          0.04496  3.87426  3.76379  1.46634  0.26236  1.05747  0.42669
    126   1.00452  2.34427  0.84730  2.21373    139 - -
          1.38629  1.38629  1.38629  1.38629
          0.04246  3.87345  3.87345  1.46634  0.26236  1.14507  0.38302
    127   0.67428  2.14439  1.80088  1.56933    140 - -
          1.38700  1.38700  1.38700  1.38417
          0.04308  3.84548  3.87345  1.43100  0.27321  1.07906  0.41539
    128   2.26118  0.94355  2.32464  0.89475    142 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87487  3.87487  1.46634  0.26236  1.12311  0.39344
    129   2.50271  2.93188  0.23250  2.62709    143 - -
          1.38629  1.38629  1.38629  1.38629
          0.04286  3.87487  3.85393  1.46634  0.26236  1.12311  0.39344
    130   0.18163  3.12033  2.62949  2.99907    144 - -
          1.38629  1.38629  1.38629  1.38629
          0.04242  3.87443  3.87443  1.46634  0.26236  1.12997  0.39015
    131   0.18796  3.08149  2.60913  2.95912    145 - -
          1.38629  1.38629  1.38629  1.38629
          0.04242  3.87443  3.87443  1.46634  0.26236  1.10502  0.40227
    132   3.06361  0.18928  3.11010  2.51174    148 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87496  3.87496  1.46634  0.26236  1.12178  0.39408
    133   2.72446  3.29634  0.15594  3.17518    149 - -
          1.38629  1.38629  1.38629  1.38629
          0.04374  3.87496  3.81463  1.46634  0.26236  1.12178  0.39408
    134   3.05494  0.19196  3.11324  2.48798    150 - -
          1.38629  1.38629  1.38629  1.38629
          0.04245  3.87366  3.87366  1.46634  0.26236  1.08150  0.41413
    135   2.76264  2.37821  2.84923  0.24046    151 - -
          1.39214  1.39214  1.36895  1.39214
          0.04966  3.66417  3.78002  1.22266  0.34877  1.12178  0.39408
    136   2.46747  3.09261  0.20160  2.94889    155 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.87289  3.79597  1.46634  0.26236  1.05876  0.42600
    137   2.62648  3.20850  0.17337  3.06993    156 - -
          1.38629  1.38629  1.38629  1.38629
          0.04247  3.87330  3.87330  1.46634  0.26236  1.04922  0.43111
    138   3.12114  0.17566  3.17519  2.58753    157 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87544  3.87544  1.46634  0.26236  1.11416  0.39778
    139   2.54452  3.03005  0.20964  2.77573    158 - -
          1.38717  1.38717  1.38367  1.38717
          0.04314  3.84092  3.87544  1.42287  0.27578  1.11416  0.39778
    140   2.70892  3.26085  0.15965  3.15599    160 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87544  3.87544  1.46634  0.26236  1.11416  0.39778
    141   2.75750  0.26345  2.84227  2.20851    161 - -
          1.38629  1.38629  1.38629  1.38629
          0.04301  3.87544  3.84672  1.46634  0.26236  1.11416  0.39778
    142   1.16818  2.38657  0.71145  2.24250    162 - -
          1.38629  1.38629  1.38629  1.38629
          0.04317  3.87484  3.83997  1.46634  0.26236  1.09496  0.40730
    143   2.01350  1.75417  1.60822  0.70687    164 - -
          1.38717  1.38717  1.38717  1.38367
          0.04317  3.84018  3.87470  1.42287  0.27578  1.07064  0.41975
    144   2.70614  3.21580  0.16567  3.08449    166 - -
          1.38629  1.38629  1.38629  1.38629
          0.04330  3.87588  3.83326  1.46634  0.26236  1.10719  0.40120
    145   2.80522  0.25362  2.74648  2.30892    167 - -
          1.39480  1.36722  1.38863  1.39480
          0.04742  3.67800  3.86140  1.28017  0.32572  1.07886  0.41549
    146   2.16306  0.69755  2.30539  1.24652    172 - -
          1.38784  1.38784  1.38784  1.38167
          0.04371  3.81554  3.87560  1.39169  0.28589  1.09812  0.40571
    147   2.82441  2.41246  2.88536  0.22913    174 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    148   0.29800  2.71400  2.37807  2.31568    175 - -
          1.38629  1.38629  1.38629  1.38629
          0.04312  3.87588  3.84136  1.46634  0.26236  1.10719  0.40120
    149   0.18186  3.11876  2.62891  2.99754    176 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87515  3.87515  1.46634  0.26236  1.08421  0.41274
    150   2.07346  0.68823  2.14393  1.36809    179 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    151   0.23119  2.97190  2.33005  2.84876    180 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    152   3.02714  0.18540  3.12421  2.56657    182 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    153   0.18660  3.10187  2.60846  2.96403    183 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    154   2.84033  2.43520  2.89755  0.22458    186 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    155   2.74933  3.29351  0.15371  3.18473    187 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.10719  0.40120
    156   3.13295  0.17248  3.19380  2.60616    188 - -
          1.38629  1.38629  1.38629  1.38629
          0.04383  3.87588  3.80987  1.46634  0.26236  1.10719  0.40120
    157   0.18441  3.11115  2.61406  2.98336    190 - -
          1.38629  1.38629  1.38629  1.38629
          0.04318  3.87446  3.83994  1.46634  0.26236  1.06348  0.42350
    158   0.21078  2.99675  2.55937  2.76871    193 - -
          1.38629  1.38629  1.38629  1.38629
          0.04373  3.87515  3.81520  1.46634  0.26236  1.08421  0.41274
    159   2.73091  3.28560  0.15780  3.13730    194 - -
          1.38629  1.38629  1.38629  1.38629
          0.04333  3.87460  3.83308  1.46634  0.26236  1.08759  0.41102
    160   2.82071  2.43013  2.88687  0.22733    195 - -
          1.38629  1.38629  1.38629  1.38629
          0.04241  3.87456  3.87456  1.46634  0.26236  1.12798  0.39110
    161   2.42252  0.28971  2.75111  2.31299    196 - -
          1.38629  1.38629  1.38629  1.38629
          0.04308  3.87456  3.84418  1.46634  0.26236  1.12798  0.39110
    162   2.65571  3.21456  0.17083  3.06595    198 - -
          1.38629  1.38629  1.38629  1.38629
          0.04880  3.87392  3.61746  1.46634  0.26236  1.10753  0.40104
    163   0.26557  2.74921  2.41061  2.53212    199 - -
          1.38440  1.38693  1.38693  1.38693
          0.04323  3.84350  3.86847  1.43473  0.27204  0.96193  0.48152
    164   0.68790  2.39215  1.21099  2.22529    202 - -
          1.38629  1.38629  1.38629  1.38629
          0.04297  3.87456  3.84899  1.46634  0.26236  1.12798  0.39110
    165   2.86995  0.23127  2.76864  2.44155    203 - -
          1.38629  1.38629  1.38629  1.38629
          0.04282  3.87402  3.85657  1.46634  0.26236  1.13632  0.38713
    166   2.70557  3.21174  0.16787  3.04873    204 - -
          1.38629  1.38629  1.38629  1.38629
          0.04304  3.87366  3.84674  1.46634  0.26236  1.12451  0.39276
    167   1.27540  1.73718  0.94284  1.86340    205 - -
          1.38401  1.38777  1.38777  1.38564
          0.04494  3.81622  3.81962  1.39509  0.28477  1.11813  0.39585
    168   1.43610  1.75040  1.44078  1.04498    207 - -
          1.38629  1.38629  1.38629  1.38629
          0.04381  3.87287  3.81388  1.46634  0.26236  1.10008  0.40473
    169   1.10765  1.67367  1.21128  1.69122    208 - -
          1.38629  1.38629  1.38629  1.38629
          0.04398  3.87276  3.80643  1.46634  0.26236  1.13909  0.38583
    170   1.00140  1.64966  1.52404  1.50198    209 - -
          1.38629  1.38629  1.38629  1.38629
          0.06334  3.87168  3.20506  1.46634  0.26236  1.06615  0.42210
    171   1.33022  1.28890  1.42797  1.51316    210 - -
          1.37342  1.39172  1.38658  1.39359
          0.08315  3.59712  2.94918  1.17543  0.36916  1.09581  0.40687
    172   1.20680  1.68666  1.13287  1.64194    212 - -
          1.38629  1.38629  1.38629  1.38629
          0.09745  3.83024  2.64303  1.46634  0.26236  1.51698  0.24766
    173   1.63407  1.28932  1.44452  1.22571    213 - -
          1.38629  1.38629  1.38629  1.38629
          0.10628  3.78263  2.55021  1.46634  0.26236  1.93953  0.15522
    174   1.46186  1.53492  1.46104  1.13717    214 - -
          1.38629  1.38629  1.38629  1.38629
          0.05825  3.72700  3.42599  1.46634  0.26236  1.17627  0.36879
    175   1.43769  1.33182  1.55472  1.24730    215 - -
          1.38629  1.38629  1.38629  1.38629
          0.13920  3.76569  2.23683  1.46634  0.26236  2.04570  0.13845
    176   1.51080  1.52879  1.22626  1.31274    216 - -
          1.38629  1.38629  1.38629  1.38629
          0.14909  3.67940  2.17796  1.46634  0.26236  1.60147  0.22515
    177   1.30236  1.43695  1.34004  1.47569    217 - -
          1.15721  1.98818  1.15121  1.45912
          0.52330  0.96656  3.61007  2.11599  0.12842  0.17626  1.82264
    178   1.88718  1.27137  1.65717  0.97451    302 - -
          1.38629  1.38629  1.38629  1.38629
          0.04255  3.87144  3.87144  1.46634  0.26236  1.01341  0.45095
    179   2.04664  1.85617  2.28201  0.49023    303 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87510  3.87510  1.46634  0.26236  1.11958  0.39515
    180   1.58552  1.26283  1.93297  1.00079    304 - -
          1.38629  1.38629  1.38629  1.38629
          0.05006  3.87510  3.57280  1.46634  0.26236  1.11958  0.39515
    181   1.71718  2.52349  0.44171  2.32984    305 - -
          1.14073  1.55147  1.46034  1.44257
          0.70250  1.19155  1.60494  2.14401  0.12464  1.20027  0.35827
    182   1.62447  1.29109  1.23255  1.44197    423 - -
          1.38629  1.38629  1.38629  1.38629
          0.08890  3.67003  2.82027  1.46634  0.26236  1.37943  0.28998
    183   1.49159  1.58301  1.38396  1.14242    424 - -
          1.38629  1.38629  1.38629  1.38629
          0.05305  3.68723  3.62602  1.46634  0.26236  0.93889  0.49604
    184   1.36850  1.62120  1.29023  1.29960    425 - -
          1.38629  1.38629  1.38629  1.38629
          0.05246  3.76807  3.57501  1.46634  0.26236  1.82746  0.17533
    185   1.38641  1.67057  1.37480  1.17442    426 - -
          1.38629  1.38629  1.38629  1.38629
          0.04922  3.76960  3.69024  1.46634  0.26236  1.47025  0.26119
    186   1.52429  1.82314  0.94138  1.46698    427 - -
          1.38629  1.38629  1.38629  1.38629
          0.04864  3.78631  3.69711  1.46634  0.26236  0.86678  0.54525
    187   1.63202  1.19761  1.41534  1.34820    428 - -
          1.38629  1.38629  1.38629  1.38629
          0.04550  3.82883  3.78329  1.46634  0.26236  0.71971  0.66727
    188   1.44677  1.64396  1.37282  1.14550    429 - -
          1.38629  1.38629  1.38629  1.38629
          0.04724  3.86103  3.68513  1.46634  0.26236  0.82708  0.57505
    189   1.55742  1.75881  0.92795  1.50640    430 - -
          1.38629  1.38629  1.38629  1.38629
          0.04298  3.87029  3.85306  1.46634  0.26236  1.05410  0.42848
    190   1.13813  1.58041  1.42691  1.45396    431 - -
          1.38688  1.38688  1.38453  1.38688
          0.04487  3.84968  3.79013  1.43679  0.27140  1.09217  0.40870
    191   1.51563  1.22231  1.89273  1.09327    433 - -
          1.38629  1.38629  1.38629  1.38629
          0.04582  3.87249  3.73042  1.46634  0.26236  1.06489  0.42276
    192   1.78489  1.73809  1.12216  1.10639    434 - -
          1.38629  1.38629  1.38629  1.38629
          0.04255  3.87138  3.87138  1.46634  0.26236  1.01596  0.44951
    193   0.20189  2.97298  2.56538  2.90459    435 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87500  3.87500  1.46634  0.26236  1.12112  0.39440
    194   2.55599  2.86677  0.21110  2.88577    436 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87500  3.87500  1.46634  0.26236  1.12112  0.39440
    195   2.25868  1.21252  2.35107  0.68757    437 - -
          1.38944  1.38944  1.38944  1.37693
          0.04512  3.75645  3.87500  1.32318  0.30964  1.09555  0.40700
    196   2.47441  2.86529  0.25781  2.45249    439 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    197   2.72524  3.29031  0.15738  3.15004    440 - -
          1.38629  1.38629  1.38629  1.38629
          0.04510  3.87554  3.75698  1.46634  0.26236  1.11264  0.39852
    198   3.07737  0.18157  3.13890  2.56880    441 - -
          1.38629  1.38629  1.38629  1.38629
          0.04248  3.87292  3.87292  1.46634  0.26236  1.15318  0.37926
    199   2.39845  3.07238  0.20941  2.96099    442 - -
          1.38727  1.38727  1.38338  1.38727
          0.04333  3.83469  3.87292  1.41828  0.27724  1.03463  0.43906
    200   1.18998  1.83206  1.01058  1.76211    444 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    201   0.18342  3.10359  2.62382  2.99233    445 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    202   2.74432  0.23973  2.92590  2.35125    448 - -
          1.38629  1.38629  1.38629  1.38629
          0.08045  3.87554  2.87246  1.46634  0.26236  1.11264  0.39852
    203   2.65167  3.14715  0.18156  2.94644    449 - -
          1.38629  1.38629  1.38629  1.38629
          0.04398  3.83906  3.83906  1.46634  0.26236  0.55907  0.84802
    204   2.74676  3.30374  0.15404  3.17291    450 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    205   2.72939  3.21518  0.16111  3.13749    452 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    206   2.73155  2.40050  2.77412  0.24615    454 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    207   2.66479  3.11667  0.18299  2.93170    455 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    208   0.24162  2.67614  2.51383  2.73549    457 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    209   2.76169  3.32480  0.15054  3.20419    458 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    210   2.73048  2.38371  2.68809  0.25542    459 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    211   0.18052  3.12706  2.63335  3.00612    460 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    212   0.18942  3.09433  2.58239  2.96296    464 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    213   2.28116  0.60692  2.33442  1.36281    465 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    214   1.21842  2.43208  0.66279  2.29227    466 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    215   2.93356  0.22696  2.95877  2.32321    468 - -
          1.38216  1.38767  1.38767  1.38767
          0.04357  3.82175  3.87554  1.39926  0.28340  1.11264  0.39852
    216   1.75020  2.09620  0.59960  1.86881    470 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    217   2.83800  2.43074  2.89527  0.22539    471 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    218   1.32174  2.24453  0.66233  2.19192    474 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    219   1.84829  2.42832  0.43361  2.24295    475 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    220   2.01292  2.37540  0.39254  2.32193    476 - -
          1.38629  1.38629  1.38629  1.38629
          0.26750  3.87554  1.54193  1.46634  0.26236  1.11264  0.39852
    221   2.00809  1.35562  2.02454  0.74252    477 - -
          1.38629  1.38629  1.38629  1.38629
          0.05279  3.66083  3.66083  1.46634  0.26236  0.18065  1.80014
    222   0.28292  2.78082  2.21661  2.58422    481 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    223   0.18052  3.12706  2.63335  3.00612    482 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    224   2.14623  0.87377  2.25921  1.01813    483 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    225   1.78446  0.61691  2.01213  1.84012    485 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    226   2.80634  2.41734  2.87691  0.23054    486 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    227   1.51204  2.51282  0.50473  2.35565    487 - -
          1.38759  1.38241  1.38759  1.38759
          0.04404  3.82487  3.85066  1.40306  0.28216  1.11264  0.39852
    228   2.80780  0.23822  2.88286  2.34698    490 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87501  3.87501  1.46634  0.26236  1.09601  0.40677
    229   3.11522  0.17802  3.17632  2.56440    491 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    230   2.16603  1.03655  2.19812  0.86826    492 - -
          1.38629  1.38629  1.38629  1.38629
          0.04296  3.87554  3.84862  1.46634  0.26236  1.11264  0.39852
    231   1.60381  1.52871  1.68789  0.92345    493 - -
          1.38689  1.38689  1.38689  1.38451
          0.04291  3.85145  3.87497  1.43656  0.27147  1.09466  0.40745
    232   1.33658  1.72671  1.53406  1.06790    496 - -
          1.38732  1.38323  1.38732  1.38732
          0.04326  3.83544  3.87554  1.41599  0.27798  1.11264  0.39852
    233   1.41963  1.69233  1.68265  0.94617    498 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    234   0.66454  2.14541  1.48777  1.94775    499 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    235   2.09302  1.78885  0.52057  2.15974    500 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    236   1.31456  1.73437  2.03086  0.85879    558 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    237   1.71682  1.29754  1.11925  1.51124    559 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    238   1.78480  1.59141  0.97874  1.37537    560 - -
          1.38603  1.38307  1.38804  1.38804
          0.04389  3.80792  3.87554  1.38261  0.28891  1.11264  0.39852
    239   2.52479  3.01070  0.20354  2.90348    562 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    240   2.76169  3.32480  0.15054  3.20419    563 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    241   2.02561  2.80480  0.30542  2.64851    564 - -
          1.38758  1.38758  1.38246  1.38758
          0.04348  3.82554  3.87554  1.40387  0.28189  1.11264  0.39852
    242   0.18105  3.12531  2.62956  3.00437    567 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    243   2.43955  1.66220  2.51352  0.44302    568 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    244   0.18209  3.12181  2.62206  3.00088    569 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    245   0.42063  2.47264  1.77649  2.41049    570 - -
          1.38629  1.38629  1.38629  1.38629
          0.04302  3.87554  3.84590  1.46634  0.26236  1.11264  0.39852
    246   2.44382  0.40502  2.28857  1.93241    571 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87491  3.87491  1.46634  0.26236  1.09285  0.40836
    247   1.33553  1.31089  1.72227  1.24222    573 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    248   1.33064  1.36132  1.38916  1.46932    574 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    249   1.75298  1.27387  1.82054  0.95436    576 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    250   1.96630  1.79052  1.62039  0.70253    577 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    251   1.90367  1.83859  0.56649  2.08407    578 - -
          1.38895  1.38895  1.37838  1.38895
          0.04467  3.77461  3.87554  1.34340  0.30240  1.11264  0.39852
    252   2.73661  3.31206  0.15355  3.19141    580 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    253   0.18052  3.12706  2.63335  3.00612    581 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    254   0.18501  3.11210  2.60142  2.99116    582 - -
          1.38629  1.38629  1.38629  1.38629
          0.04449  3.87554  3.78226  1.46634  0.26236  1.11264  0.39852
    255   0.18298  3.11546  2.62037  2.99410    583 - -
          1.38629  1.38629  1.38629  1.38629
          0.04329  3.87351  3.83606  1.46634  0.26236  1.07571  0.41711
    256   2.10228  0.62061  1.77418  1.76852    587 - -
          1.38629  1.38629  1.38629  1.38629
          0.04306  3.87419  3.84547  1.46634  0.26236  1.07084  0.41965
    257   1.68392  1.89184  0.76905  1.60891    588 - -
          1.38629  1.38629  1.38629  1.38629
          0.04269  3.87493  3.86136  1.46634  0.26236  1.12217  0.39389
    258   1.16327  1.89286  1.06627  1.64711    591 - -
          1.38384  1.38711  1.38711  1.38711
          0.04312  3.84237  3.87465  1.42564  0.27490  1.09790  0.40582
    259   1.60344  1.41528  1.30670  1.25447    593 - -
          1.38629  1.38629  1.38629  1.38629
          0.04281  3.87525  3.85586  1.46634  0.26236  1.11713  0.39634
    260   1.36465  1.68323  1.27410  1.27627    594 - -
          1.38629  1.38629  1.38629  1.38629
          0.04280  3.87485  3.85643  1.46634  0.26236  1.05060  0.43037
    261   1.85183  2.48474  0.44424  2.13377    595 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87603  3.87603  1.46634  0.26236  1.08637  0.41164
    262   2.20202  0.52312  2.13277  1.72460    596 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    263   2.69915  2.12191  2.76002  0.28816    597 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    264   0.18396  3.09350  2.62649  2.98871    598 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    265   0.18022  3.12878  2.63452  3.00798    599 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    266   2.56526  2.30294  2.53285  0.29611    600 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    267   0.25371  2.76248  2.34570  2.73074    601 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    268   3.13815  0.17210  3.19890  2.60459    603 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    269   2.48267  0.40518  2.51941  1.77718    604 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    270   2.33935  2.48535  0.30588  2.47886    606 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    271   1.70989  1.13267  1.19047  1.64577    607 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    272   0.19799  3.03943  2.53961  2.94012    608 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    273   2.78515  2.41936  2.87001  0.23243    609 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    274   0.41422  2.60679  1.72315  2.44336    610 - -
          1.37466  1.38692  1.39568  1.38803
          0.16742  3.55643  2.07451  1.11411  0.39780  1.09861  0.40547
    275   1.14068  1.29898  1.76348  1.44333    630 - -
          1.38629  1.38629  1.38629  1.38629
          0.04741  3.76560  3.76560  1.46634  0.26236  0.37185  1.16943
    276   1.52866  1.75415  1.10046  1.28229    631 - -
          1.38629  1.38629  1.38629  1.38629
          0.04279  3.86593  3.86593  1.46634  0.26236  0.87463  0.53960
    277   1.38936  1.22664  1.35971  1.60568    632 - -
          1.38629  1.38629  1.38629  1.38629
          0.04305  3.87554  3.84471  1.46634  0.26236  1.11264  0.39852
    278   1.55923  1.24923  1.89495  1.04227    633 - -
          1.38597  1.38597  1.38349  1.38975
          0.04541  3.74507  3.87489  1.31043  0.31431  1.09205  0.40876
    279   1.67332  0.93834  1.57719  1.53923    636 - -
          1.38629  1.38629  1.38629  1.38629
          0.26716  3.87554  1.54316  1.46634  0.26236  1.11264  0.39852
    280   1.37085  1.42056  1.50764  1.26196    637 - -
          1.38629  1.38629  1.38629  1.38629
          0.05781  3.66115  3.49119  1.46634  0.26236  2.49720  0.08590
    281   1.25030  1.51686  1.63162  1.20875    638 - -
          1.38629  1.38629  1.38629  1.38629
          0.05577  3.65680  3.56025  1.46634  0.26236  2.48674  0.08684
    282   1.30348  1.63394  1.40319  1.24672    639 - -
          1.38629  1.38629  1.38629  1.38629
          0.05988  3.65524  3.43382  1.46634  0.26236  2.53165  0.08287
    283   1.35655  1.60650  1.32858  1.28369    640 - -
          1.38629  1.38629  1.38629  1.38629
          0.05534  3.64881  3.58235  1.46634  0.26236  2.40509  0.09459
    284   1.39297  1.59422  1.38639  1.20858    641 - -
          1.33764  1.43795  1.46717  1.31102
          0.12179  2.47581  3.48778  0.78760  0.60685  2.49492  0.08611
    285   1.07502  1.64911  1.41392  1.49925    644 - -
          1.38629  1.38629  1.38629  1.38629
          0.06724  3.64781  3.24459  1.46634  0.26236  2.50570  0.08514
    286   1.33393  1.38453  1.55153  1.29392    645 - -
          1.11213  1.59385  1.23045  1.73819
          0.43896  1.11189  3.63610  1.76118  0.18855  0.17537  1.82724
    287   1.66994  1.93502  0.96073  1.25629    688 - -
          1.38629  1.38629  1.38629  1.38629
          0.04246  3.87350  3.87350  1.46634  0.26236  1.05074  0.43029
    288   1.38432  1.03174  1.69437  1.56348    689 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    289   0.84427  1.50311  1.85575  1.65362    690 - -
          1.38629  1.38629  1.38629  1.38629
          0.04344  3.87554  3.82757  1.46634  0.26236  1.11264  0.39852
    290   1.53172  1.91571  1.30903  1.00371    691 - -
          1.52156  1.80720  1.32202  1.04720
          0.36019  2.92796  1.39051  4.49408  0.01124  1.12866  0.39077
    291   1.79115  1.37013  0.90612  1.74257    843 - -
          1.38629  1.38629  1.38629  1.38629
          0.05575  3.61551  3.60012  1.46634  0.26236  2.02443  0.14164
    292   1.44719  1.62893  1.30105  1.21610    844 - -
          1.38629  1.38629  1.38629  1.38629
          0.05405  3.63796  3.63796  1.46634  0.26236  2.23548  0.11310
    293   1.69826  1.60451  1.64981  0.85820    845 - -
          1.42487  1.40646  1.42385  1.29585
          0.10144  2.66957  3.60529  0.63338  0.75671  2.43675  0.09151
    294   1.27457  1.60816  1.50422  1.21065    847 - -
          1.38629  1.38629  1.38629  1.38629
          0.05472  3.65083  3.60151  1.46634  0.26236  2.30491  0.10510
    295   1.57823  1.57619  1.34199  1.12217    848 - -
          1.53304  1.32681  1.57304  1.16673
          0.53351  0.94989  3.62410  0.54779  0.86329  2.47829  0.08762
    296   1.33778  1.72141  1.42251  1.14680    856 - -
          1.38629  1.38629  1.38629  1.38629
          0.05342  3.65700  3.64155  1.46634  0.26236  2.37801  0.09732
    297   1.40752  1.59080  1.34184  1.23745    857 - -
          1.38629  1.38629  1.38629  1.38629
          0.05280  3.66072  3.66072  1.46634  0.26236  0.18498  1.77857
    298   1.69068  1.74606  0.90265  1.44539    858 - -
          1.38629  1.38629  1.38629  1.38629
          0.04241  3.87460  3.87460  1.46634  0.26236  1.10951  0.40006
    299   1.08510  1.99325  1.20096  1.49176    860 - -
          1.38629  1.38629  1.38629  1.38629
          0.04346  3.87497  3.82720  1.46634  0.26236  1.09470  0.40742
    300   1.76533  1.65156  1.25216  1.04631    861 - -
          1.45395  1.41681  1.26525  1.42006
          0.10888  2.52251  3.77649  0.47016  0.98057  1.09408  0.40774
    301   1.59195  1.60315  0.89875  1.67062   1133 - -
          1.38629  1.38629  1.38629  1.38629
          0.04248  3.87311  3.87311  1.46634  0.26236  1.03984  0.43620
    302   0.22362  2.97423  2.38458  2.86174   1135 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.11264  0.39852
    303   0.18495  3.10582  2.61694  2.97521   1136 - -
          1.38629  1.38629  1.38629  1.38629
          0.04333  3.87554  3.83241  1.46634  0.26236  1.11264  0.39852
    304   0.18387  3.11090  2.62563  2.97590   1137 - -
          1.37731  1.41261  1.36040  1.39562
          0.06578  3.14879  3.87462  0.78853  0.60607  1.08390  0.41291
    305   2.51215  2.99502  0.20530  2.91007   1139 - -
          1.38629  1.38629  1.38629  1.38629
          0.06106  3.87554  3.25735  1.46634  0.26236  1.11264  0.39852
    306   1.31825  1.53704  1.25684  1.45745   1141 - -
          1.38629  1.38629  1.38629  1.38629
          0.23820  3.85763  1.65635  1.46634  0.26236  1.36045  0.29645
    307   1.31440  1.58545  1.32018  1.34930   1142 - -
          1.38629  1.38629  1.38629  1.38629
          0.11342  3.67164  2.50361  1.46634  0.26236  2.47944  0.08751
    308   1.77758  2.06508  0.57735  1.94660   1143 - -
          1.38629  1.38629  1.38629  1.38629
          0.05974  3.61364  3.47270  1.46634  0.26236  2.64973  0.07329
    309   1.78483  1.39299  0.91479  1.69695   1144 - -
          1.39439  1.69505  1.45608  1.09280
          0.48056  1.03957  3.57703  2.43144  0.09202  0.15409  1.94625
    310   1.72488  1.86840  1.46057  0.83165   1271 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87485  3.87485  1.46634  0.26236  1.09093  0.40933
    311   1.61339  1.54081  1.82090  0.85637   1272 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87554  3.87554  1.46634  0.26236  1.07113  0.41950
    312   1.34663  1.39026  1.85505  1.09533   1273 - -
          1.38629  1.38629  1.38629  1.38629
          0.04884  3.87641  3.61425  1.46634  0.26236  1.09861  0.40547
    313   1.03995  1.96819  1.28371  1.47050   1274 - -
          1.33905  1.60807  1.33929  1.28880
          0.72944  1.31375  1.39025  2.39257  0.09584  1.19384  0.36105
    314   1.79187  0.98006  1.30370  1.67912   1392 - -
          1.38629  1.38629  1.38629  1.38629
          0.05889  3.61121  3.50086  1.46634  0.26236  2.31137  0.10439
    315   1.85740  1.35643  1.86385  0.84102   1393 - -
          1.38629  1.38629  1.38629  1.38629
          0.05510  3.61914  3.61914  1.46634  0.26236  1.45475  0.26587
    316   1.46212  1.35253  1.61801  1.16675   1394 - -
          1.41773  1.41093  1.41773  1.30358
          0.08648  2.85479  3.67785  0.72526  0.66203  0.25005  1.50852
    317   1.58741  1.58539  1.51893  0.98958   1396 - -
          1.38629  1.38629  1.38629  1.38629
          0.04287  3.86419  3.86419  1.46634  0.26236  0.81576  0.58394
    318   2.58964  0.34556  2.61467  1.93840   1397 - -
          1.38629  1.38629  1.38629  1.38629
          0.04305  3.87641  3.84396  1.46634  0.26236  1.09861  0.40547
    319   1.97614  2.83504  0.30660  2.70701   1398 - -
          1.38998  1.38998  1.37530  1.38998
          0.04557  3.73781  3.87573  1.30134  0.31768  1.07709  0.41640
    320   2.11042  0.61823  1.69739  1.85307   1444 - -
          1.38629  1.38629  1.38629  1.38629
          0.04299  3.87641  3.84634  1.46634  0.26236  1.09861  0.40547
    321   2.05219  1.47621  2.10939  0.65060   1445 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87578  3.87578  1.46634  0.26236  1.10874  0.40044
    322   1.08865  1.76630  1.51431  1.30047   1446 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87578  3.87578  1.46634  0.26236  1.10874  0.40044
    323   1.18640  1.74254  1.58184  1.15833   1447 - -
          1.38629  1.38629  1.38629  1.38629
          0.04383  3.87578  3.81025  1.46634  0.26236  1.07866  0.41559
    324   1.09412  1.66711  1.39938  1.47131   1449 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87501  3.87501  1.46634  0.26236  1.05540  0.42779
    325   0.96113  2.22392  0.96436  2.05471   1450 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    326   2.63430  3.18896  0.17447  3.05520   1451 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    327   0.20077  3.04106  2.53762  2.89927   1452 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    328   2.13744  2.13822  1.91985  0.48199   1453 - -
          1.38738  1.38738  1.38738  1.38303
          0.04568  3.83374  3.77118  1.41282  0.27899  1.09861  0.40547
    329   1.99220  2.08314  0.56289  1.77486   1457 - -
          1.38629  1.38629  1.38629  1.38629
          0.04243  3.87411  3.87411  1.46634  0.26236  1.05989  0.42540
    330   1.12135  2.30630  0.79193  2.10732   1459 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87573  3.87573  1.46634  0.26236  1.10957  0.40003
    331   1.79365  2.51810  0.41033  2.41234   1460 - -
          1.38629  1.38629  1.38629  1.38629
          0.04300  3.87573  3.84687  1.46634  0.26236  1.10957  0.40003
    332   2.34376  0.45270  2.22467  1.83245   1462 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87512  3.87512  1.46634  0.26236  1.09032  0.40964
    333   2.20044  0.51972  2.26542  1.65667   1463 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87573  3.87573  1.46634  0.26236  1.10957  0.40003
    334   2.17751  0.79203  2.15437  1.14641   1464 - -
          1.38845  1.37987  1.38845  1.38845
          0.04423  3.79306  3.87573  1.36474  0.29497  1.10957  0.40003
    335   1.52722  2.55658  0.48580  2.40695   1466 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87573  3.87573  1.46634  0.26236  1.07706  0.41642
    336   1.88233  0.64647  2.04079  1.64017   1467 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    337   2.50327  3.16349  0.19001  3.01686   1469 - -
          1.38629  1.38629  1.38629  1.38629
          0.04279  3.87641  3.85547  1.46634  0.26236  1.09861  0.40547
    338   1.98945  1.92141  1.51307  0.69998   1476 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    339   1.84659  0.83597  1.72219  1.46925   1477 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    340   1.51563  1.27201  1.24947  1.54457   1478 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    341   1.88081  1.43233  1.22409  1.15595   1479 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    342   0.18140  3.12448  2.62653  3.00362   1481 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    343   2.84051  2.43532  2.89772  0.22454   1488 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    344   2.38882  1.46009  2.45883  0.52676   1489 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    345   0.18037  3.12792  2.63394  3.00705   1495 - -
          1.38709  1.38709  1.38709  1.38390
          0.04304  3.84451  3.87598  1.42664  0.27459  1.10564  0.40197
    346   2.71225  3.29552  0.15694  3.17464   1497 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    347   2.23469  0.49330  2.02581  1.89392   1498 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    348   2.83297  2.41736  2.89032  0.22759   1499 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    349   0.54706  2.26841  2.12697  1.61609   1500 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    350   2.75453  3.31026  0.15307  3.17521   1505 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    351   2.63504  2.37000  2.78988  0.25699   1506 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    352   2.47425  2.33984  2.70723  0.28408   1507 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    353   2.76235  3.32571  0.15041  3.20518   1509 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    354   2.75882  3.31872  0.15160  3.19158   1510 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    355   2.68126  2.19079  2.75470  0.27963   1512 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    356   1.60392  2.61471  0.44654  2.45497   1513 - -
          1.38080  1.38813  1.38813  1.38813
          0.04395  3.80495  3.87598  1.37854  0.29028  1.10564  0.40197
    357   0.89590  2.30451  0.99559  2.10006   1515 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    358   2.69064  3.25067  0.16527  3.08464   1516 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    359   2.65845  3.27159  0.16350  3.15040   1517 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    360   2.84051  2.43532  2.89772  0.22454   1518 - -
          1.38326  1.39022  1.39022  1.38152
          0.04576  3.72993  3.87598  1.29229  0.32109  1.10564  0.40197
    361   0.21811  2.99519  2.42396  2.85825   1523 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.08470  0.41249
    362   0.18803  3.10289  2.57963  2.98199   1524 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    363   1.31937  1.39249  1.85181  1.11691   1525 - -
          1.38740  1.38740  1.38740  1.38300
          0.04329  3.83328  3.87641  1.41226  0.27917  1.09861  0.40547
    364   2.35744  3.04932  0.22117  2.87591   1527 - -
          1.38629  1.38629  1.38629  1.38629
          0.04608  3.87641  3.71674  1.46634  0.26236  1.09861  0.40547
    365   2.74711  3.31387  0.15262  3.19276   1528 - -
          1.38629  1.38629  1.38629  1.38629
          0.04249  3.87282  3.87282  1.46634  0.26236  0.99504  0.46157
    366   3.04735  0.18141  3.14995  2.58268   1530 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    367   2.17113  1.03421  2.22937  0.86074   1531 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    368   2.26165  0.99364  2.33666  0.84643   1532 - -
          1.38629  1.38629  1.38629  1.38629
          0.04289  3.87641  3.85090  1.46634  0.26236  1.09861  0.40547
    369   0.18205  3.11208  2.63026  2.99832   1533 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87588  3.87588  1.46634  0.26236  1.08167  0.41404
    370   3.12760  0.17260  3.19475  2.60734   1534 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    371   3.13256  0.17282  3.18613  2.60671   1535 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    372   0.24762  2.85010  2.47960  2.55454   1536 - -
          1.38213  1.38769  1.38769  1.38769
          0.04354  3.82218  3.87641  1.39872  0.28357  1.09861  0.40547
    373   0.21349  2.97467  2.54847  2.76508   1542 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    374   2.73321  3.31146  0.15386  3.19095   1543 - -
          1.38629  1.38629  1.38629  1.38629
          0.04279  3.87641  3.85547  1.46634  0.26236  1.09861  0.40547
    375   2.04819  2.07829  0.44733  2.23911   1544 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    376   3.12086  0.17660  3.18186  2.57366   1545 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    377   1.62524  2.11841  0.70837  1.65826   1547 - -
          1.38286  1.38744  1.38744  1.38744
          0.04335  3.83106  3.87598  1.41007  0.27988  1.10564  0.40197
    378   0.28641  2.75442  2.31018  2.45159   1550 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    379   2.22664  0.60765  2.37368  1.36908   1551 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    380   2.70848  3.25589  0.16321  3.09209   1552 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    381   0.18633  3.09986  2.62122  2.95209   1553 - -
          1.38744  1.38744  1.38286  1.38744
          0.04335  3.83106  3.87598  1.41007  0.27988  1.10564  0.40197
    382   2.35043  1.45650  2.43630  0.53762   1555 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    383   1.63049  1.24895  1.03420  1.82110   1556 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    384   1.61713  1.27777  1.25795  1.43281   1557 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    385   1.56372  1.75181  0.79167  1.80730   1558 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    386   2.75306  2.39161  2.81155  0.24249   1559 - -
          1.38848  1.38848  1.38848  1.37977
          0.04424  3.79219  3.87598  1.36341  0.29543  1.10564  0.40197
    387   0.18947  3.05879  2.61290  2.95010   1573 - -
          1.38629  1.38629  1.38629  1.38629
          0.04276  3.87598  3.85751  1.46634  0.26236  1.10564  0.40197
    388   2.14051  2.45155  0.38481  2.15706   1574 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87559  3.87559  1.46634  0.26236  1.09333  0.40812
    389   2.84359  0.23848  2.72119  2.42857   1575 - -
          1.38629  1.38629  1.38629  1.38629
          0.04290  3.87598  3.85088  1.46634  0.26236  1.10564  0.40197
    390   2.09942  0.92855  2.04636  1.04088   1576 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.08892  0.41035
    391   2.70875  3.25594  0.16072  3.13957   1577 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    392   1.69836  2.51350  0.45600  2.28066   1579 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    393   1.89134  1.06795  1.95264  1.01192   1580 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    394   2.43718  0.46225  2.42536  1.63846   1581 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    395   2.80305  2.34809  2.86105  0.24002   1582 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    396   2.66907  3.24773  0.16675  3.09202   1584 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    397   0.18100  3.12583  2.62942  3.00496   1585 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    398   2.76235  3.32571  0.15041  3.20518   1586 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    399   0.18308  3.11383  2.62125  2.99266   1587 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    400   2.69675  3.28645  0.15900  3.16543   1590 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    401   2.42169  2.89236  0.22359  2.87987   1591 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    402   1.06753  2.00855  1.03449  1.79245   1592 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    403   2.29746  1.81147  2.46189  0.42955   1593 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    404   2.68838  3.27182  0.16140  3.14385   1595 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.08470  0.41249
    405   0.28873  2.79282  2.15270  2.61230   1596 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    406   1.75301  1.38963  2.05353  0.80006   1597 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    407   3.12743  0.17494  3.18832  2.58468   1598 - -
          1.38618  1.38054  1.38924  1.38924
          0.04489  3.76485  3.87641  1.33115  0.30676  1.09861  0.40547
    408   1.11623  2.08288  0.86799  2.05477   1600 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    409   2.56889  2.79822  0.21763  2.84663   1601 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    410   2.35091  0.34016  2.60950  2.12451   1603 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    411   2.88485  0.20566  3.00653  2.51872   1604 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    412   0.19828  2.99980  2.59582  2.89171   1605 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    413   3.08509  0.18184  3.10376  2.58147   1607 - -
          1.38800  1.38119  1.38800  1.38800
          0.04381  3.81032  3.87641  1.38443  0.28830  1.09861  0.40547
    414   0.18177  3.11901  2.62945  2.99793   1609 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    415   2.14706  0.55384  2.29148  1.57350   1610 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    416   2.64112  2.30494  2.54382  0.28716   1611 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    417   2.73404  3.24586  0.15826  3.15873   1613 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    418   2.75474  3.32244  0.15126  3.20198   1614 - -
          1.38629  1.38629  1.38629  1.38629
          0.04287  3.87641  3.85192  1.46634  0.26236  1.09861  0.40547
    419   1.64491  2.33391  0.50792  2.22276   1615 - -
          1.38629  1.38629  1.38629  1.38629
          0.04302  3.87590  3.84573  1.46634  0.26236  1.08235  0.41370
    420   0.18387  3.11219  2.62295  2.97862   1617 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87578  3.87578  1.46634  0.26236  1.07860  0.41562
    421   3.10357  0.17854  3.17231  2.56772   1618 - -
          1.38916  1.38916  1.38916  1.37775
          0.04482  3.76781  3.87641  1.33455  0.30554  1.09861  0.40547
    422   2.82208  2.41074  2.86914  0.23065   1620 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    423   2.75460  3.31035  0.15293  3.17798   1621 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    424   0.19016  3.08534  2.57381  2.97182   1622 - -
          1.38294  1.38742  1.38742  1.38742
          0.04330  3.83252  3.87641  1.41133  0.27948  1.09861  0.40547
    425   2.65477  3.26455  0.16482  3.13679   1624 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    426   0.18305  3.10822  2.62322  2.99520   1625 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    427   2.86449  0.25898  2.93040  2.13897   1626 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    428   0.18492  3.11126  2.60350  2.99034   1628 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    429   3.14190  0.17111  3.20260  2.61161   1629 - -
          1.38629  1.38629  1.38629  1.38629
          0.04583  3.87641  3.72672  1.46634  0.26236  1.09861  0.40547
    430   2.66684  3.14637  0.18446  2.88297   1630 - -
          1.38629  1.38629  1.38629  1.38629
          0.04248  3.87306  3.87306  1.46634  0.26236  1.00135  0.45789
    431   2.75563  3.31858  0.15179  3.19266   1631 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    432   2.16733  0.58792  2.21208  1.51157   1633 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    433   3.10203  0.18180  3.16330  2.53841   1634 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    434   3.02691  0.18916  3.07318  2.55612   1636 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    435   0.24307  2.76984  2.46305  2.68912   1637 - -
          1.38629  1.38629  1.38629  1.38629
          0.04440  3.87641  3.78527  1.46634  0.26236  1.09861  0.40547
    436   1.95621  2.51535  0.39083  2.28989   1638 - -
          1.38629  1.38629  1.38629  1.38629
          0.04242  3.87443  3.87443  1.46634  0.26236  1.03878  0.43678
    437   0.18022  3.12878  2.63452  3.00798   1639 - -
          1.38629  1.38629  1.38629  1.38629
          0.04292  3.84980  3.87641  1.43268  0.27269  1.09861  0.40547
    438   3.12081  0.17389  3.18944  2.59972   1641 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    439   2.68794  2.37965  2.81491  0.24912   1642 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    440   3.09302  0.18062  3.16287  2.55642   1643 - -
          1.38629  1.38629  1.38629  1.38629
          0.04333  3.87641  3.83135  1.46634  0.26236  1.09861  0.40547
    441   3.11780  0.17730  3.17887  2.56931   1644 - -
          1.38629  1.38629  1.38629  1.38629
          0.04483  3.87546  3.76819  1.46634  0.26236  1.06880  0.42071
    442   2.81207  2.41212  2.87857  0.23057   1645 - -
          1.38942  1.38942  1.38942  1.37698
          0.04515  3.75619  3.87407  1.32395  0.30936  1.02840  0.44251
    443   0.18563  3.10573  2.60277  2.98462   1647 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    444   3.13536  0.17284  3.19614  2.59937   1648 - -
          1.38754  1.38257  1.38754  1.38754
          0.04341  3.82781  3.87641  1.40556  0.28134  1.09861  0.40547
    445   2.75577  3.32296  0.15113  3.20251   1655 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    446   2.76302  3.32662  0.15027  3.20617   1656 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    447   2.71780  3.29825  0.15656  3.17120   1658 - -
          1.37500  1.39009  1.39009  1.39009
          0.04563  3.73492  3.87641  1.29735  0.31918  1.09861  0.40547
    448   0.20769  3.00998  2.54057  2.82296   1660 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    449   2.74990  3.30302  0.15340  3.18182   1661 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    450   2.75569  3.32292  0.15114  3.20247   1662 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    451   3.11244  0.17658  3.15096  2.59608   1663 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    452   0.22159  2.95073  2.55017  2.68264   1666 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    453   2.75329  3.31874  0.15170  3.19815   1667 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    454   3.12587  0.17392  3.17768  2.60294   1668 - -
          1.38754  1.38257  1.38754  1.38754
          0.04420  3.82780  3.84042  1.40555  0.28134  1.09861  0.40547
    455   0.18171  3.11955  2.62949  2.99841   1670 - -
          1.38629  1.38629  1.38629  1.38629
          0.04282  3.87565  3.85471  1.46634  0.26236  1.07476  0.41761
    456   2.75753  3.30709  0.15204  3.19483   1672 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    457   2.75335  2.26242  2.81246  0.25860   1673 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    458   1.49388  2.23250  0.60944  2.08277   1674 - -
          1.38142  1.38792  1.38792  1.38792
          0.04376  3.81282  3.87598  1.38795  0.28713  1.10564  0.40197
    459   2.27843  3.04414  0.22851  2.91511   1678 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.10564  0.40197
    460   2.47618  3.16928  0.19079  3.04498   1679 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87598  3.87598  1.46634  0.26236  1.08470  0.41249
    461   2.72276  3.30607  0.15515  3.18551   1680 - -
          1.38629  1.38629  1.38629  1.38629
          0.04501  3.87641  3.76004  1.46634  0.26236  1.09861  0.40547
    462   0.19209  3.08273  2.56174  2.96106   1681 - -
          1.38629  1.38629  1.38629  1.38629
          0.04244  3.87385  3.87385  1.46634  0.26236  1.07633  0.41679
    463   0.18421  3.10948  2.62524  2.97213   1682 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87519  3.87519  1.46634  0.26236  1.07288  0.41859
    464   2.79015  2.41968  2.83202  0.23478   1683 - -
          1.38629  1.38629  1.38629  1.38629
          0.04376  3.87615  3.81300  1.46634  0.26236  1.10281  0.40337
    465   0.96827  1.31006  1.96660  1.55815   1684 - -
          1.38629  1.38629  1.38629  1.38629
          0.04348  3.82618  3.87480  1.40555  0.28134  1.06107  0.42478
    466   2.73349  2.40729  2.80225  0.24299   1687 - -
          1.38629  1.38629  1.38629  1.38629
          0.04234  3.87615  3.87615  1.46634  0.26236  1.10281  0.40337
    467   2.82940  2.43324  2.89253  0.22594   1688 - -
          1.38629  1.38629  1.38629  1.38629
          0.04234  3.87615  3.87615  1.46634  0.26236  1.10281  0.40337
    468   1.99962  1.57306  0.67669  1.90443   1689 - -
          1.38629  1.38629  1.38629  1.38629
          0.04234  3.87615  3.87615  1.46634  0.26236  1.09026  0.40967
    469   2.01970  0.80864  1.30375  1.89493   1690 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    470   0.83821  2.15499  1.21369  1.86747   1691 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    471   3.14190  0.17111  3.20260  2.61161   1693 - -
          1.38629  1.38629  1.38629  1.38629
          0.04313  3.87641  3.84042  1.46634  0.26236  1.09861  0.40547
    472   0.18286  3.10660  2.62775  2.99333   1695 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87565  3.87565  1.46634  0.26236  1.07476  0.41761
    473   0.18371  3.10604  2.61852  2.99300   1696 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    474   2.84133  2.43586  2.89851  0.22436   1697 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    475   2.74673  3.31001  0.15299  3.18918   1698 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    476   2.58240  3.10445  0.18471  3.03218   1699 - -
          1.38629  1.38629  1.38629  1.38629
          0.04331  3.87641  3.83216  1.46634  0.26236  1.09861  0.40547
    477   1.81727  2.72439  0.36006  2.59949   1701 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87548  3.87548  1.46634  0.26236  1.06933  0.42043
    478   2.09444  0.65368  1.53726  1.95358   1702 - -
          1.38629  1.38629  1.38629  1.38629
          0.04287  3.87641  3.85200  1.46634  0.26236  1.09861  0.40547
    479   2.72905  3.20200  0.16189  3.13497   1703 - -
          1.38727  1.38336  1.38727  1.38727
          0.04366  3.83743  3.85490  1.41798  0.27734  1.08240  0.41367
    480   0.89738  1.38353  1.68935  1.85130   1708 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87597  3.87597  1.46634  0.26236  1.08466  0.41252
    481   0.19536  3.05637  2.56261  2.93180   1709 - -
          1.38629  1.38629  1.38629  1.38629
          0.04299  3.87641  3.84636  1.46634  0.26236  1.09861  0.40547
    482   0.18307  3.11371  2.62154  2.99250   1710 - -
          1.36935  1.39201  1.39201  1.39201
          0.09113  3.66942  2.78692  1.22729  0.34685  1.10873  0.40044
    483   2.02358  1.54408  0.65631  1.99841   1713 - -
          1.38629  1.38629  1.38629  1.38629
          0.04687  3.83405  3.72288  1.46634  0.26236  0.53844  0.87625
    484   2.53407  0.42749  2.59119  1.64202   1714 - -
          1.38629  1.38629  1.38629  1.38629
          0.04784  3.87226  3.65324  1.46634  0.26236  0.98089  0.46997
    485   2.91482  0.22512  2.89842  2.38316   1715 - -
          1.38629  1.38629  1.38629  1.38629
          0.04255  3.87133  3.87133  1.46634  0.26236  0.97727  0.47214
    486   2.80513  2.41782  2.86286  0.23158   1717 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87592  3.87592  1.46634  0.26236  1.08306  0.41333
    487   2.73173  3.26827  0.15932  3.12140   1718 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    488   0.18413  3.11026  2.62615  2.97154   1719 - -
          1.38179  1.38557  1.38892  1.38892
          0.07010  3.77659  3.10567  1.34468  0.30195  1.09861  0.40547
    489   1.91840  1.27248  2.14939  0.78424   1723 - -
          1.38629  1.38629  1.38629  1.38629
          0.04340  3.85205  3.85205  1.46634  0.26236  1.42585  0.27484
    490   1.95386  1.32374  0.80656  1.92590   1724 - -
          1.38629  1.38629  1.38629  1.38629
          0.04340  3.85205  3.85205  1.46634  0.26236  0.65510  0.73270
    491   1.97917  0.71484  1.50964  1.88680   1725 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    492   0.19695  3.02195  2.59916  2.88727   1726 - -
          1.38629  1.38629  1.38629  1.38629
          0.04313  3.87641  3.84042  1.46634  0.26236  1.09861  0.40547
    493   2.71930  3.22272  0.16127  3.14253   1727 - -
          1.38820  1.38060  1.38820  1.38820
          0.04402  3.80219  3.87565  1.37563  0.29126  1.07476  0.41761
    494   3.12367  0.17416  3.18463  2.59761   1729 - -
          1.38629  1.38629  1.38629  1.38629
          0.04384  3.87641  3.80889  1.46634  0.26236  1.09861  0.40547
    495   1.12241  1.52987  1.22040  1.81505   1730 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87497  3.87497  1.46634  0.26236  1.05411  0.42848
    496   0.18505  3.08827  2.62010  2.98459   1731 - -
          1.38213  1.38857  1.38857  1.38592
          0.04562  3.78917  3.81755  1.35935  0.29683  1.09861  0.40547
    497   2.25031  0.77189  2.34023  1.09008   1733 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87516  3.87516  1.46634  0.26236  1.05976  0.42547
    498   2.37394  2.99221  0.22569  2.83460   1734 - -
          1.38629  1.38629  1.38629  1.38629
          0.04401  3.87641  3.80198  1.46634  0.26236  1.09861  0.40547
    499   3.11633  0.17756  3.17745  2.56818   1736 - -
          1.38629  1.38629  1.38629  1.38629
          0.04240  3.87481  3.87481  1.46634  0.26236  1.04961  0.43090
    500   2.61170  0.29211  2.77865  2.13895   1737 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    501   2.73852  3.30445  0.15411  3.18354   1738 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    502   2.95996  0.21123  3.02475  2.40769   1740 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    503   2.68797  3.24904  0.16359  3.12174   1741 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    504   2.84133  2.43586  2.89851  0.22436   1742 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    505   2.75136  3.31147  0.15305  3.17934   1752 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    506   0.91468  1.75752  1.63232  1.46357   1753 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    507   1.38580  2.44249  0.57201  2.31725   1754 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    508   1.93237  1.58703  1.38430  0.91588   1758 - -
          1.38629  1.38629  1.38629  1.38629
          0.04333  3.87641  3.83126  1.46634  0.26236  1.09861  0.40547
    509   2.75062  3.31220  0.15276  3.18601   1761 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87546  3.87546  1.46634  0.26236  1.06874  0.42074
    510   0.18022  3.12878  2.63452  3.00798   1762 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    511   1.00736  1.90118  1.90048  1.09086   1763 - -
          1.38791  1.38791  1.38147  1.38791
          0.04493  3.81382  3.82265  1.38863  0.28690  1.09861  0.40547
    512   2.75001  3.29752  0.15447  3.16470   1765 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87527  3.87527  1.46634  0.26236  1.06309  0.42371
    513   0.19879  3.06243  2.52906  2.92305   1766 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    514   0.38102  2.09111  2.31536  2.35858   1767 - -
          1.38629  1.38629  1.38629  1.38629
          0.08010  3.87641  2.87798  1.46634  0.26236  1.09861  0.40547
    515   2.62237  3.15792  0.18080  2.99075   1769 - -
          1.38629  1.38629  1.38629  1.38629
          0.04448  3.84025  3.81575  1.46634  0.26236  0.55211  0.85740
    516   2.44471  2.64459  0.28382  2.41559   1773 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87590  3.87590  1.46634  0.26236  1.08235  0.41370
    517   2.02730  0.73773  2.16955  1.28778   1774 - -
          1.38629  1.38629  1.38629  1.38629
          0.04365  3.87641  3.81742  1.46634  0.26236  1.09861  0.40547
    518   2.44598  0.51203  2.52277  1.45311   1775 - -
          1.40959  1.36663  1.40959  1.36043
          0.06764  3.23695  3.64499  0.86409  0.54721  1.05967  0.42552
    519   2.57707  2.13599  2.54779  0.31797   1810 - -
          1.38629  1.38629  1.38629  1.38629
          0.04257  3.87104  3.87104  1.46634  0.26236  0.95120  0.48821
    520   2.40356  2.29121  2.58402  0.31062   1811 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    521   1.62190  0.68154  2.13099  1.72642   1812 - -
          1.38629  1.38629  1.38629  1.38629
          0.04287  3.87641  3.85192  1.46634  0.26236  1.09861  0.40547
    522   2.58872  3.16931  0.18401  2.97734   1813 - -
          1.37623  1.39182  1.38538  1.39182
          0.04717  3.67559  3.87590  1.23365  0.34422  1.08235  0.41370
    523   2.74427  3.31102  0.15343  3.18287   1847 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    524   1.38763  2.19766  0.69031  1.98159   1848 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    525   2.20708  2.22547  2.35138  0.37582   1849 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    526   2.39647  1.51149  2.47185  0.50426   1851 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    527   2.76144  3.32052  0.15080  3.20279   1853 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    528   2.84133  2.43586  2.89851  0.22436   1855 - -
          1.38629  1.38629  1.38629  1.38629
          0.04372  3.87641  3.81452  1.46634  0.26236  1.09861  0.40547
    529   0.18885  3.09917  2.57554  2.97806   1856 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87509  3.87509  1.46634  0.26236  1.05778  0.42653
    530   0.18114  3.12569  2.62787  3.00490   1859 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    531   0.18022  3.12878  2.63452  3.00798   1860 - -
          1.38629  1.38629  1.38629  1.38629
          0.07935  3.87641  2.89039  1.46634  0.26236  1.09861  0.40547
    532   1.78048  1.40213  0.84039  1.87192   1861 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  0.55739  0.85027
    533   2.30894  0.65496  2.36430  1.24773   1862 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    534   1.52351  1.67773  1.75882  0.86036   1863 - -
          1.38629  1.38629  1.38629  1.38629
          0.04305  3.87641  3.84379  1.46634  0.26236  1.09861  0.40547
    535   3.11409  0.17459  3.18539  2.59809   1865 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87573  3.87573  1.46634  0.26236  1.07698  0.41646
    536   2.52836  2.31092  2.42503  0.31120   1909 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    537   1.80584  1.99905  1.41825  0.78075   1910 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    538   2.68363  2.39742  2.81923  0.24708   1911 - -
          1.38629  1.38629  1.38629  1.38629
          0.04469  3.87641  3.77292  1.46634  0.26236  1.09861  0.40547
    539   1.78812  1.08319  2.03482  1.01195   1912 - -
          1.38629  1.38629  1.38629  1.38629
          0.04243  3.87415  3.87415  1.46634  0.26236  1.03082  0.44117
    540   0.90560  1.93888  1.22078  1.85255   1913 - -
          1.38629  1.38629  1.38629  1.38629
          0.04269  3.87641  3.85996  1.46634  0.26236  1.09861  0.40547
    541   1.78806  1.65257  1.32317  0.98118   1914 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87607  3.87607  1.46634  0.26236  1.08767  0.41098
    542   1.54407  1.22911  1.71104  1.16072   1916 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    543   0.92651  1.72481  1.53199  1.56181   1917 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    544   1.69599  2.44273  0.45470  2.35365   1919 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    545   1.62394  2.17737  0.64153  1.81368   1920 - -
          1.38629  1.38629  1.38629  1.38629
          0.04409  3.87641  3.79823  1.46634  0.26236  1.09861  0.40547
    546   2.22012  2.94630  0.24751  2.84516   1921 - -
          1.38629  1.38629  1.38629  1.38629
          0.04241  3.87473  3.87473  1.46634  0.26236  1.04717  0.43221
    547   0.23963  2.94654  2.29031  2.82476   1922 - -
          1.38629  1.38629  1.38629  1.38629
          0.04330  3.87641  3.83271  1.46634  0.26236  1.09861  0.40547
    548   0.91295  1.58334  1.45198  1.83719   1923 - -
          1.41631  1.27565  1.43099  1.43099
          0.08472  2.83577  3.79156  0.60080  0.79490  1.08764  0.41100
    549   2.51785  2.83337  0.23120  2.70345   1926 - -
          1.38629  1.38629  1.38629  1.38629
          0.06980  3.87421  3.06503  1.46634  0.26236  1.13338  0.38852
    550   0.26038  2.83505  2.24877  2.73337   1927 - -
          1.38629  1.38629  1.38629  1.38629
          0.17201  3.84799  1.98992  1.46634  0.26236  1.42912  0.27380
    551   0.27718  2.73144  2.31556  2.54789   1928 - -
          1.37331  1.38852  1.38967  1.39380
          0.14590  3.46305  2.25930  1.16908  0.37201  2.20766  0.11649
    552   1.19979  1.59398  1.24581  1.57061   1930 - -
          1.38629  1.38629  1.38629  1.38629
          0.08231  3.64446  2.93978  1.46634  0.26236  1.55102  0.23830
    553   1.31403  1.54828  1.13870  1.61739   1931 - -
          1.38629  1.38629  1.38629  1.38629
          0.12338  3.66338  2.40320  1.46634  0.26236  2.42187  0.09294
    554   1.42443  1.62449  1.22112  1.31885   1932 - -
          1.38629  1.38629  1.38629  1.38629
          0.07032  3.59881  3.20524  1.46634  0.26236  2.68758  0.07047
    555   1.53776  1.51203  1.25782  1.27152   1933 - -
          1.50961  1.34319  1.50607  1.21668
          0.12274  2.54885  3.28788  1.18966  0.36287  2.71987  0.06815
    556   1.31040  1.58847  1.60011  1.12647   1937 - -
          1.38629  1.38629  1.38629  1.38629
          0.05881  3.57587  3.53634  1.46634  0.26236  2.64371  0.07375
    557   1.08643  1.67797  1.42288  1.44898   1938 - -
          1.38629  1.38629  1.38629  1.38629
          0.06217  3.57765  3.43149  1.46634  0.26236  2.73836  0.06686
    558   1.35155  1.60969  1.42162  1.20434   1939 - -
          1.42844  1.42844  1.27310  1.42431
          0.11264  2.57190  3.50193  0.62131  0.77055  2.62050  0.07555
    559   1.43276  1.48232  1.30751  1.33276   1941 - -
          1.38629  1.38629  1.38629  1.38629
          0.06681  3.57500  3.30735  1.46634  0.26236  2.67237  0.07159
    560   1.26980  1.81698  1.16903  1.40272   1942 - -
          1.40486  1.28429  1.42415  1.43954
          0.49603  1.01556  3.54544  2.19208  0.11843  0.14691  1.99049
    561   1.60715  1.84078  1.37452  0.94704   1992 - -
          1.38629  1.38629  1.38629  1.38629
          0.04250  3.87267  3.87267  1.46634  0.26236  1.03250  0.44024
    562   0.81177  1.91356  1.77127  1.43439   1993 - -
          1.38629  1.38629  1.38629  1.38629
          0.04373  3.87542  3.81464  1.46634  0.26236  1.11444  0.39765
    563   0.68758  1.96374  1.75954  1.68873   1994 - -
          1.38629  1.38629  1.38629  1.38629
          0.04383  3.87412  3.81150  1.46634  0.26236  1.02996  0.44164
    564   1.26270  1.82019  1.80894  0.93831   1995 - -
          1.55345  1.23558  1.34855  1.43464
          0.79998  1.30128  1.27841  2.40559  0.09454  1.11992  0.39498
    565   1.66675  1.33200  1.70405  1.00719   2056 - -
          1.38629  1.38629  1.38629  1.38629
          0.06729  3.57704  3.29356  1.46634  0.26236  2.47434  0.08798
    566   1.43604  1.35068  1.56991  1.22077   2057 - -
          1.38629  1.38629  1.38629  1.38629
          0.06163  3.57637  3.44839  1.46634  0.26236  2.65388  0.07298
    567   1.37422  1.50394  1.49535  1.20218   2058 - -
          1.38629  1.38629  1.38629  1.38629
          0.05766  3.57511  3.57511  1.46634  0.26236  2.67467  0.07142
    568   1.33463  1.59031  1.35555  1.29071   2059 - -
          1.38629  1.38629  1.38629  1.38629
          0.05812  3.57712  3.55751  1.46634  0.26236  2.58628  0.07829
    569   1.45275  1.64374  1.28996  1.21222   2060 - -
          1.42929  1.42929  1.42165  1.27395
          0.11133  2.56698  3.55466  0.61436  0.77868  2.57020  0.07961
    570   1.34837  1.38177  1.45786  1.36074   2062 - -
          1.38629  1.38629  1.38629  1.38629
          0.05706  3.58526  3.58526  1.46634  0.26236  2.34495  0.10076
    571   1.48403  1.39975  1.52019  1.17782   2063 - -
          1.38629  1.38629  1.38629  1.38629
          0.05632  3.59782  3.59782  1.46634  0.26236  1.54016  0.24124
    572   1.35120  1.67850  1.25417  1.31265   2064 - -
          1.38629  1.38629  1.38629  1.38629
          0.05524  3.65523  3.57958  1.46634  0.26236  1.12373  0.39314
    573   2.18153  2.07363  2.01173  0.46578   2065 - -
          1.27410  1.42958  1.42533  1.42512
          0.09839  2.66333  3.73015  0.58670  0.81229  0.25108  1.50491
    574   2.54385  2.65406  0.23673  2.78279   2067 - -
          1.38629  1.38629  1.38629  1.38629
          0.04244  3.87384  3.87384  1.46634  0.26236  1.13909  0.38583
    575   0.29687  2.40744  2.42289  2.54910   2068 - -
          1.38629  1.38629  1.38629  1.38629
          0.04244  3.87384  3.87384  1.46634  0.26236  1.13909  0.38583
    576   2.13563  0.40950  2.35960  2.09244   2069 - -
          1.38629  1.38629  1.38629  1.38629
          0.04324  3.87384  3.83785  1.46634  0.26236  1.02227  0.44594
    577   2.38567  2.74100  0.27124  2.51293   2070 - -
          1.38629  1.38629  1.38629  1.38629
          0.04576  3.87565  3.73010  1.46634  0.26236  1.07476  0.41761
    578   1.94118  2.30145  0.54505  1.73422   2071 - -
          1.38629  1.38629  1.38629  1.38629
          0.04247  3.87316  3.87316  1.46634  0.26236  1.00397  0.45637
    579   2.40607  2.25289  2.24467  0.35843   2072 - -
          1.27361  1.43090  1.43090  1.41886
          0.08944  2.83810  3.61133  0.60154  0.79400  1.09861  0.40547
    580   0.23910  2.94166  2.29963  2.82027   2074 - -
          1.38629  1.38629  1.38629  1.38629
          0.04261  3.87010  3.87010  1.46634  0.26236  0.92991  0.50185
    581   1.99227  0.63287  1.93393  1.67147   2075 - -
          1.42985  1.27052  1.42985  1.42451
          0.08160  2.85367  3.87641  0.60979  0.78409  1.09861  0.40547
    582   2.10734  0.69676  1.95896  1.43030   2077 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    583   1.67254  1.43770  1.67175  0.94974   2078 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    584   1.38301  1.71250  1.18439  1.33625   2079 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    585   1.16161  1.33581  1.58824  1.51510   2080 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    586   1.05028  1.52117  1.66644  1.41558   2081 - -
          1.42792  1.27571  1.42866  1.42159
          0.08518  2.83584  3.77292  0.60035  0.79545  1.09861  0.40547
    587   2.13291  2.28962  0.39643  2.23037   2083 - -
          1.42802  1.27268  1.42563  1.42802
          0.08007  2.87925  3.87415  0.62481  0.76650  1.03082  0.44117
    588   0.28510  2.47645  2.43381  2.57286   2085 - -
          1.38629  1.38629  1.38629  1.38629
          0.04975  3.87641  3.58259  1.46634  0.26236  1.09861  0.40547
    589   0.54517  2.33851  1.65829  2.01501   2086 - -
          1.46773  1.17797  1.46446  1.46773
          0.11042  2.87113  3.03845  0.95204  0.48768  0.98338  0.46848
    590   1.61064  1.99017  0.89181  1.37178   2089 - -
          1.38629  1.38629  1.38629  1.38629
          0.04361  3.84725  3.84725  1.46634  0.26236  1.36938  0.29338
    591   0.29643  2.64859  2.20165  2.58816   2090 - -
          1.38629  1.38629  1.38629  1.38629
          0.04350  3.84971  3.84971  1.46634  0.26236  0.63152  0.75882
    592   0.28107  2.75164  2.44655  2.35799   2091 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    593   2.74565  3.28672  0.15441  3.18208   2092 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    594   2.50401  0.38642  2.40858  1.90506   2093 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    595   1.13482  1.22309  1.71591  1.58767   2094 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    596   1.94143  0.46836  2.37238  1.98620   2095 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    597   2.97725  0.20985  2.98064  2.43494   2097 - -
          1.46698  1.31164  1.46698  1.31164
          0.07935  2.89039  3.87641  0.96084  0.48219  1.09861  0.40547
    598   2.55145  2.66346  0.23400  2.79754   2100 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    599   2.37705  3.09992  0.20951  2.97320   2101 - -
          1.42745  1.42745  1.42745  1.27211
          0.07935  2.89039  3.87641  0.62967  0.76093  1.09861  0.40547
    600   2.46488  0.27629  2.77964  2.36097   2103 - -
          1.42745  1.42745  1.42745  1.27211
          0.07935  2.89039  3.87641  0.62967  0.76093  1.09861  0.40547
    601   2.15180  2.11161  2.48720  0.38634   2105 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    602   0.27680  2.76849  2.45682  2.37160   2106 - -
          1.38629  1.38629  1.38629  1.38629
          0.04381  3.87641  3.81041  1.46634  0.26236  1.09861  0.40547
    603   0.27176  2.50884  2.46329  2.63886   2107 - -
          1.34969  1.34969  1.50490  1.34969
          0.08031  2.87501  3.87500  1.19772  0.35937  1.05509  0.42796
    604   2.31788  0.40717  2.24008  2.04380   2111 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    605   2.69830  2.13696  2.76310  0.28559   2112 - -
          1.27211  1.42745  1.42745  1.42745
          0.07935  2.89039  3.87641  0.62967  0.76093  1.09861  0.40547
    606   1.07214  1.21740  1.96055  1.50985   2114 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    607   2.67521  0.34542  2.74463  1.83941   2115 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    608   2.53956  2.92206  0.24002  2.51748   2116 - -
          1.38629  1.38629  1.38629  1.38629
          0.04334  3.87641  3.83088  1.46634  0.26236  1.09861  0.40547
    609   2.69891  2.12403  2.75978  0.28786   2117 - -
          1.31164  1.31164  1.46698  1.46698
          0.07943  2.88943  3.87545  0.96084  0.48219  1.11402  0.39785
    610   2.51009  2.59206  0.25115  2.71859   2120 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    611   2.73869  0.26824  2.54992  2.38020   2122 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    612   3.13548  0.17211  3.19631  2.60746   2123 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    613   0.27660  2.76952  2.45722  2.37217   2124 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    614   2.37440  3.04733  0.21518  2.93657   2125 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    615   3.07042  0.18519  3.11048  2.55014   2126 - -
          1.21745  1.34338  1.50721  1.50721
          0.08249  2.85295  3.83946  1.17940  0.36739  1.11402  0.39785
    616   0.27917  2.76248  2.44565  2.36673   2130 - -
          1.38629  1.38629  1.38629  1.38629
          0.04241  3.87469  3.87469  1.46634  0.26236  1.04603  0.43283
    617   2.73653  3.27654  0.15678  3.15688   2131 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    618   2.66088  0.28683  2.50352  2.32607   2132 - -
          1.38629  1.38629  1.38629  1.38629
          0.04283  3.87641  3.85390  1.46634  0.26236  1.09861  0.40547
    619   2.43677  0.29142  2.75040  2.28814   2133 - -
          1.38629  1.38629  1.38629  1.38629
          0.04235  3.87594  3.87594  1.46634  0.26236  1.08366  0.41303
    620   2.37271  3.08240  0.21213  2.95524   2134 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    621   2.92843  0.23542  2.99304  2.24293   2135 - -
          1.42745  1.42745  1.42745  1.27211
          0.07935  2.89039  3.87641  0.62967  0.76093  1.09861  0.40547
    622   2.53612  2.63913  0.24021  2.76552   2137 - -
          1.38629  1.38629  1.38629  1.38629
          0.04354  3.87641  3.82218  1.46634  0.26236  1.09861  0.40547
    623   2.54365  2.65400  0.23653  2.78562   2138 - -
          1.31393  1.31393  1.46927  1.45936
          0.08168  2.85276  3.87526  0.93466  0.49876  1.06278  0.42387
    624   2.78116  2.39979  2.86186  0.23555   2141 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    625   0.28171  2.48935  2.41587  2.61387   2142 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    626   0.27762  2.76697  2.45622  2.36657   2143 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    627   2.14710  1.87493  1.81063  0.56870   2144 - -
          1.46165  1.18180  1.46165  1.47156
          0.08158  2.85391  3.87641  0.95096  0.48836  1.09861  0.40547
    628   0.27619  2.50114  2.43972  2.62893   2147 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    629   2.86149  0.24550  2.95220  2.22308   2148 - -
          1.49730  1.35187  1.50721  1.21745
          0.08158  2.85391  3.87641  1.17940  0.36739  1.09861  0.40547
    630   2.28809  3.02477  0.23010  2.89106   2153 - -
          1.38629  1.38629  1.38629  1.38629
          0.04334  3.87641  3.83088  1.46634  0.26236  1.09861  0.40547
    631   1.72551  1.79880  1.22500  1.01428   2154 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    632   0.20095  3.06117  2.49718  2.93939   2155 - -
          1.38629  1.38629  1.38629  1.38629
          0.04314  3.87545  3.84093  1.46634  0.26236  1.11402  0.39785
    633   2.23281  2.35797  0.34770  2.38759   2156 - -
          1.42745  1.42745  1.42745  1.27211
          0.07949  2.88870  3.87472  0.62967  0.76093  1.09096  0.40931
    634   2.43861  2.51895  0.27279  2.64616   2158 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    635   1.86574  2.33360  0.52523  1.85244   2159 - -
          1.38629  1.38629  1.38629  1.38629
          0.04307  3.87545  3.84397  1.46634  0.26236  1.11402  0.39785
    636   1.67863  1.72639  1.20467  1.09167   2160 - -
          1.42745  1.42745  1.27211  1.42745
          0.07948  2.88876  3.87478  0.62967  0.76093  1.09298  0.40829
    637   2.31839  2.42173  0.34946  2.22812   2162 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    638   3.04104  0.19055  3.09334  2.52126   2163 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    639   1.10565  1.77564  1.25960  1.53311   2164 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    640   0.28051  2.75850  2.43998  2.36392   2165 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    641   2.36122  2.53169  0.28002  2.65355   2167 - -
          1.41993  1.27450  1.42984  1.42984
          0.08166  2.85295  3.87545  0.60992  0.78393  1.11402  0.39785
    642   2.45708  0.28241  2.77299  2.32402   2169 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    643   2.71217  3.29932  0.15659  3.17853   2170 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    644   2.83952  2.43467  2.89677  0.22475   2171 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    645   2.83952  2.43467  2.89677  0.22475   2173 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    646   0.98469  2.17232  1.02654  1.86895   2174 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    647   1.58237  1.61974  2.09060  0.74876   2175 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    648   2.25593  0.91585  2.31418  0.92583   2177 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    649   2.48090  0.27082  2.80310  2.37559   2178 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.11402  0.39785
    650   2.37697  3.05422  0.21348  2.95191   2179 - -
          1.38629  1.38629  1.38629  1.38629
          0.04238  3.87545  3.87545  1.46634  0.26236  1.06849  0.42087
    651   2.37180  3.10385  0.20988  2.97334   2180 - -
          1.38629  1.38629  1.38629  1.38629
          0.04319  3.87641  3.83767  1.46634  0.26236  1.09861  0.40547
    652   0.24178  2.94600  2.27669  2.82017   2181 - -
          1.38629  1.38629  1.38629  1.38629
          0.04237  3.87560  3.87560  1.46634  0.26236  1.07295  0.41855
    653   0.63323  1.97994  2.04225  1.60291   2182 - -
          1.42306  1.42980  1.27446  1.42675
          0.08155  2.85442  3.87641  0.61019  0.78361  1.09861  0.40547
    654   2.83879  2.42977  2.89601  0.22539   2184 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    655   1.86587  1.68010  1.93072  0.66584   2185 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    656   0.27095  2.51142  2.46542  2.64202   2186 - -
          1.17722  1.46698  1.46698  1.46698
          0.08348  2.89039  3.70756  0.96084  0.48219  1.09861  0.40547
    657   2.28185  0.83409  2.35281  0.99822   2189 - -
          1.38629  1.38629  1.38629  1.38629
          0.04250  3.87260  3.87260  1.46634  0.26236  1.15812  0.37699
    658   2.53435  2.30091  2.33111  0.32389   2190 - -
          1.38629  1.38629  1.38629  1.38629
          0.04398  3.87260  3.80659  1.46634  0.26236  0.98927  0.46497
    659   2.76088  3.32370  0.15070  3.20299   2191 - -
          1.38629  1.38629  1.38629  1.38629
          0.04239  3.87500  3.87500  1.46634  0.26236  1.05509  0.42796
    660   2.52765  2.91525  0.24221  2.51240   2192 - -
          1.38629  1.38629  1.38629  1.38629
          0.04515  3.87641  3.75409  1.46634  0.26236  1.09861  0.40547
    661   2.53489  2.91589  0.24151  2.51171   2193 - -
          1.27211  1.42745  1.42745  1.42745
          0.07957  2.88769  3.87371  0.62967  0.76093  1.01875  0.44792
    662   2.31898  0.35526  2.61061  2.06244   2196 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    663   2.60324  3.05211  0.20654  2.72857   2197 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    664   2.70980  2.14422  2.77035  0.28283   2198 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    665   0.27975  2.48646  2.44747  2.59946   2199 - -
          1.38629  1.38629  1.38629  1.38629
          0.07935  2.89039  3.87641  1.40798  0.28056  1.09861  0.40547
    666   0.28759  2.45851  2.43748  2.56410   2204 - -
          1.38629  1.38629  1.38629  1.38629
          0.04233  3.87641  3.87641  1.46634  0.26236  1.09861  0.40547
    667   0.27222  2.50891  2.45910  2.63883   2205 - -
          1.38629  1.38629  1.38629  1.38629
          0.04313  3.87641  3.84042  1.46634  0.26236  1.09861  0.40547
    668   2.49746  2.89444  0.24850  2.49610   2206 - -
          1.38629  1.38629  1.38629  1.38629
          0.04292  3.87565  3.85055  1.46634  0.26236  1.07476  0.41761
    669   1.49204  1.30712  1.17048  1.63851   2207 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    670   2.45309  2.86849  0.25732  2.47614   2208 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    671   1.64165  0.99387  1.97095  1.21444   2209 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    672   1.38888  1.92640  0.91274  1.59184   2211 - -
          1.42822  1.27288  1.42822  1.42502
          0.08011  2.87801  3.87589  0.62318  0.76838  1.10705  0.40127
    673   2.40833  0.46957  2.51461  1.59029   2213 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    674   2.46306  2.73949  0.27478  2.40263   2214 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    675   2.34870  1.35901  2.41982  0.58222   2215 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    676   0.18294  3.11779  2.62078  2.99215   2217 - -
          1.38629  1.38629  1.38629  1.38629
          0.04236  3.87589  3.87589  1.46634  0.26236  1.10705  0.40127
    677   2.73981  3.30962  0.15354  3.18885   2218 - -
          1.27211  1.42745  1.42745  1.42745
          0.07939  2.88987  3.87589  0.62967  0.76093  1.10705  0.40127
    678   2.40137  2.54628  0.27190  2.67211   2220 - -
          1.42745  1.42745  1.42745  1.27211
          0.07939  2.88987  3.87589  0.62967  0.76093  1.10705  0.40127
    679   2.59013  0.38410  2.63203  1.76030   2222 - -
          1.38629  1.38629  1.38629  1.38629
          0.04403  3.87589  3.80137  1.46634  0.26236  1.10705  0.40127
    680   2.06502  2.44899  0.41047  2.09179   2223 - -
          1.28145  1.28145  1.38308  1.64026
          0.08098  2.86445  3.87428  2.27578  0.10838  1.05778  0.42652
    681   2.50808  2.60303  0.25080  2.71279   2238 - -
          1.38629  1.38629  1.38629  1.38629
          0.07939  3.87589  2.88987  1.46634  0.26236  1.10705  0.40127
    682   1.64725  1.51040  1.73245  0.89221   2239 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    683   1.90855  1.52889  1.99532  0.69523   2240 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    684   1.40193  1.70803  1.65410  0.96393   2241 - -
          1.38629  1.38629  1.38629  1.38629
          0.04467  3.84042  3.80745  1.46634  0.26236  1.54883  0.23889
    685   1.47707  1.67738  1.09344  1.38722   2242 - -
          1.38746  1.38746  1.38279  1.38746
          0.04500  3.79394  3.83970  1.40904  0.28021  1.52296  0.24598
    686   1.66993  1.89328  1.54493  0.80333   2245 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    687   1.99691  1.29506  2.12556  0.75290   2246 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    688   0.33827  2.57630  2.04271  2.51002   2247 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    689   0.42605  2.03403  2.21936  2.23090   2248 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    690   2.68606  3.20107  0.16952  3.05625   2249 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    691   2.32790  1.86534  2.48877  0.40850   2250 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84042  3.84042  1.46634  0.26236  1.54883  0.23889
    692   2.15817  0.56906  1.92571  1.75658   2251 - -
          1.39213  1.38900  1.38873  1.37540
          0.05001  3.63021  3.80443  1.22327  0.34852  1.54883  0.23889
    693   0.93050  1.90634  1.60264  1.36392   2253 - -
          1.38629  1.38629  1.38629  1.38629
          0.04396  3.83963  3.83963  1.46634  0.26236  1.49637  0.25353
    694   1.98965  2.56242  0.36460  2.38959   2254 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    695   1.01705  1.77685  1.28468  1.64803   2255 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    696   1.73083  1.64231  1.68809  0.81090   2256 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    697   2.60660  3.13855  0.18333  2.98827   2257 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    698   2.71783  2.37994  2.80577  0.24722   2258 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    699   2.04413  2.38187  0.41896  2.11696   2259 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    700   0.24352  2.86234  2.48268  2.58384   2261 - -
          1.37833  1.38896  1.38896  1.38896
          0.04630  3.73936  3.84096  1.34262  0.30267  1.54341  0.24035
    701   0.19561  3.04736  2.57707  2.91533   2263 - -
          1.38629  1.38629  1.38629  1.38629
          0.04439  3.84096  3.81913  1.46634  0.26236  1.54341  0.24035
    702   0.19542  3.05092  2.57042  2.92445   2264 - -
          1.38629  1.38629  1.38629  1.38629
          0.04440  3.84049  3.81924  1.46634  0.26236  1.52628  0.24506
    703   1.57335  1.93553  1.10614  1.14737   2265 - -
          1.38629  1.38629  1.38629  1.38629
          0.04449  3.84050  3.81540  1.46634  0.26236  1.54799  0.23911
    704   1.69586  0.76368  1.84324  1.64867   2266 - -
          1.38629  1.38629  1.38629  1.38629
          0.04444  3.83996  3.81812  1.46634  0.26236  1.52828  0.24450
    705   2.26046  0.47365  2.28576  1.76448   2267 - -
          1.38629  1.38629  1.38629  1.38629
          0.04394  3.84003  3.84003  1.46634  0.26236  1.51004  0.24962
    706   1.99470  0.75524  2.08583  1.30992   2268 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    707   1.33733  1.28643  1.37271  1.57128   2269 - -
          1.38629  1.38629  1.38629  1.38629
          0.04438  3.84096  3.81971  1.46634  0.26236  1.54341  0.24035
    708   1.72507  1.57389  0.87287  1.62532   2270 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84050  3.84050  1.46634  0.26236  1.54799  0.23911
    709   1.67451  2.19965  0.56929  1.99633   2271 - -
          1.38629  1.38629  1.38629  1.38629
          0.04441  3.84050  3.81867  1.46634  0.26236  1.54799  0.23911
    710   2.66953  3.22015  0.16796  3.09281   2272 - -
          1.38820  1.38259  1.38620  1.38820
          0.04666  3.76658  3.79595  1.37565  0.29126  1.51004  0.24962
    711   2.99900  0.19817  3.03090  2.50519   2316 - -
          1.38629  1.38629  1.38629  1.38629
          0.04394  3.84000  3.84000  1.46634  0.26236  1.50892  0.24993
    712   2.75866  2.35397  2.81833  0.24599   2317 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    713   2.24533  0.77573  2.33253  1.08860   2318 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    714   0.19584  3.03443  2.58027  2.91873   2319 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    715   0.20057  3.02370  2.56926  2.87313   2320 - -
          1.38171  1.38441  1.38954  1.38954
          0.04682  3.71867  3.84096  1.31892  0.31119  1.54341  0.24035
    716   3.02798  0.19193  3.06997  2.52827   2376 - -
          1.38749  1.38272  1.38749  1.38749
          0.04497  3.79422  3.84096  1.40784  0.28060  1.54341  0.24035
    717   2.07352  0.69928  1.99546  1.42146   2378 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    718   1.65266  1.27250  1.47845  1.20284   2379 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    719   1.69572  1.37054  1.24277  1.29470   2380 - -
          1.38629  1.38629  1.38629  1.38629
          0.04501  3.84096  3.79241  1.46634  0.26236  1.54341  0.24035
    720   1.58924  2.23541  0.57491  2.06974   2381 - -
          1.38629  1.38629  1.38629  1.38629
          0.04444  3.83990  3.81806  1.46634  0.26236  1.50543  0.25093
    721   2.03868  2.48833  0.39985  2.15134   2382 - -
          1.38629  1.38629  1.38629  1.38629
          0.04805  3.84049  3.67164  1.46634  0.26236  1.52628  0.24506
    722   0.79979  1.92220  1.46818  1.74899   2383 - -
          1.38629  1.38629  1.38629  1.38629
          0.04535  3.83701  3.78192  1.46634  0.26236  1.41311  0.27890
    723   0.82746  1.74449  1.66893  1.61114   2384 - -
          1.38629  1.38629  1.38629  1.38629
          0.09412  3.83975  2.68340  1.46634  0.26236  1.50036  0.25238
    724   1.66289  0.95835  1.65436  1.44532   2385 - -
          1.38758  1.38758  1.38245  1.38758
          0.05224  3.74286  3.60410  1.40362  0.28197  0.76919  0.62248
    725   2.02213  1.92132  1.92656  0.55240   2397 - -
          1.38629  1.38629  1.38629  1.38629
          0.04457  3.83649  3.81555  1.46634  0.26236  1.39793  0.28383
    726   2.51257  2.92856  0.22634  2.68802   2399 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84051  3.84051  1.46634  0.26236  1.52698  0.24487
    727   2.93434  0.21605  2.94932  2.42179   2400 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    728   0.93037  1.71528  1.49819  1.59879   2401 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    729   1.90232  1.70023  1.78779  0.69153   2402 - -
          1.38629  1.38629  1.38629  1.38629
          0.04439  3.84096  3.81913  1.46634  0.26236  1.54341  0.24035
    730   1.97819  1.72820  2.13943  0.56854   2403 - -
          1.38875  1.38258  1.38875  1.38510
          0.04684  3.74651  3.80951  1.35147  0.29956  1.52628  0.24506
    731   1.60004  1.58233  1.43409  1.03766   2405 - -
          1.38629  1.38629  1.38629  1.38629
          0.04393  3.84029  3.84029  1.46634  0.26236  1.51914  0.24705
    732   1.80944  2.30953  0.45151  2.29977   2406 - -
          1.38629  1.38629  1.38629  1.38629
          0.04439  3.84096  3.81913  1.46634  0.26236  1.54341  0.24035
    733   0.47624  2.34066  1.98006  1.93404   2407 - -
          1.38629  1.38629  1.38629  1.38629
          0.04392  3.84049  3.84049  1.46634  0.26236  1.52628  0.24506
    734   0.97493  1.77807  1.83873  1.22146   2408 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    735   0.19569  3.04869  2.57053  2.92219   2410 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    736   3.05642  0.18582  3.11986  2.54644   2411 - -
          1.38801  1.38801  1.38801  1.38117
          0.04544  3.77459  3.84096  1.38409  0.28842  1.54341  0.24035
    737   2.20690  2.09073  1.88448  0.48702   2413 - -
          1.38629  1.38629  1.38629  1.38629
          0.04429  3.84096  3.82345  1.46634  0.26236  1.54341  0.24035
    738   1.72109  2.47022  0.44621  2.33807   2414 - -
          1.38629  1.38629  1.38629  1.38629
          0.04495  3.84058  3.79543  1.46634  0.26236  1.52967  0.24412
    739   1.66176  1.63516  0.93768  1.49726   2415 - -
          1.38629  1.38629  1.38629  1.38629
          0.04451  3.83997  3.81488  1.46634  0.26236  1.50808  0.25017
    740   1.51519  1.24677  1.56681  1.25846   2416 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.84042  3.81858  1.46634  0.26236  1.52373  0.24577
    741   1.19115  1.81990  1.46323  1.19534   2417 - -
          1.39641  1.39641  1.39641  1.35654
          0.05309  3.49915  3.84049  1.09408  0.40774  1.52628  0.24506
    742   1.28110  1.75678  1.00877  1.68740   2419 - -
          1.56335  1.23529  1.23529  1.56511
          0.08913  2.75198  3.84096  1.40049  0.28300  1.54341  0.24035
    743   1.15028  1.93783  1.18743  1.45060   2424 - -
          1.38629  1.38629  1.38629  1.38629
          0.04390  3.84096  3.84096  1.46634  0.26236  1.54341  0.24035
    744   3.01816  0.19013  3.09997  2.53571   2425 - -
          1.45834  1.52705  1.33364  1.24937
          0.08872  2.75794  3.84096  5.87488  0.00281  1.54341  0.24035
    745   2.68372  2.32833  2.74583  0.26131   3788 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    746   0.98560  1.89702  1.81503  1.15857   3789 - -
          1.38629  1.38629  1.38629  1.38629
          0.04959  3.79811  3.65083  1.46634  0.26236  1.54341  0.24035
    747   2.63244  3.15172  0.17868  3.01698   3790 - -
          1.38629  1.38629  1.38629  1.38629
          0.04603  3.79455  3.79455  1.46634  0.26236  1.42948  0.27369
    748   0.21455  2.96054  2.49911  2.82768   3791 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    749   2.28678  2.91574  0.24417  2.79874   3792 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    750   1.94643  1.98724  1.58257  0.66418   3793 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    751   1.26711  1.66277  1.19237  1.49059   3794 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    752   1.72064  0.96114  1.96655  1.20847   3796 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    753   1.32103  1.81796  0.97853  1.63517   3797 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    754   1.70282  2.31870  0.51211  2.11861   3798 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    755   1.59800  1.68882  1.12553  1.24312   3801 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    756   0.30043  2.56546  2.35132  2.43761   3803 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    757   2.54807  3.04918  0.19636  2.94396   3804 - -
          1.38629  1.38629  1.38629  1.38629
          0.04732  3.79811  3.73805  1.46634  0.26236  1.54341  0.24035
    758   0.47290  2.50070  1.60982  2.35540   3805 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79672  3.79672  1.46634  0.26236  1.49650  0.25349
    759   2.43966  3.01422  0.21260  2.89590   3809 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    760   2.55244  3.11337  0.19015  2.97949   3810 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    761   1.12770  1.73720  1.41950  1.35335   3811 - -
          1.38629  1.38629  1.38629  1.38629
          0.04708  3.79811  3.74755  1.46634  0.26236  1.54341  0.24035
    762   1.08096  1.90471  1.17445  1.59515   3812 - -
          1.38629  1.38629  1.38629  1.38629
          0.04758  3.79695  3.72877  1.46634  0.26236  1.50387  0.25137
    763   0.70689  2.18578  1.35446  1.99254   3813 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79653  3.79653  1.46634  0.26236  1.49020  0.25532
    764   1.76955  1.81853  0.67943  1.82995   3815 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    765   2.08962  1.49502  2.13177  0.62849   3816 - -
          1.38629  1.38629  1.38629  1.38629
          0.04636  3.79811  3.77717  1.46634  0.26236  1.54341  0.24035
    766   2.10814  2.84560  0.28285  2.70602   3831 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    767   2.58495  3.05478  0.19393  2.92339   3832 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    768   0.21047  2.97205  2.52436  2.83891   3834 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    769   0.21522  2.95269  2.51530  2.80351   3837 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    770   2.54533  2.01023  2.61042  0.33674   3838 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    771   2.49547  2.27306  2.53144  0.30788   3839 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    772   2.22731  0.46343  2.24574  1.85018   3841 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    773   2.40274  0.39445  2.41734  1.92197   3842 - -
          1.38629  1.38629  1.38629  1.38629
          0.04657  3.79764  3.76892  1.46634  0.26236  1.54793  0.23913
    774   1.35211  1.47325  1.61852  1.15857   3843 - -
          1.38629  1.38629  1.38629  1.38629
          0.04591  3.79698  3.79698  1.46634  0.26236  1.52539  0.24531
    775   1.32991  1.70172  1.11012  1.49785   3845 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    776   2.53671  3.10409  0.19272  2.97010   3847 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    777   2.46381  2.27799  2.59547  0.30410   3848 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    778   2.61622  3.08996  0.18549  2.98146   3851 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    779   2.36191  2.21677  2.37655  0.35108   3852 - -
          1.38895  1.38895  1.38895  1.37838
          0.04838  3.69671  3.79764  1.34340  0.30240  1.54793  0.23913
    780   0.23189  2.86440  2.46408  2.73550   3854 - -
          1.38629  1.38629  1.38629  1.38629
          0.04755  3.79764  3.72908  1.46634  0.26236  1.54793  0.23913
    781   2.44422  2.98462  0.21674  2.85583   3855 - -
          1.38629  1.38629  1.38629  1.38629
          0.04596  3.79604  3.79604  1.46634  0.26236  1.49435  0.25411
    782   1.54833  0.84182  1.69606  1.75408   3856 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    783   2.33127  2.97915  0.23085  2.84499   3857 - -
          1.38629  1.38629  1.38629  1.38629
          0.04884  3.79764  3.67908  1.46634  0.26236  1.54793  0.23913
    784   2.63288  3.15229  0.17858  3.01760   3863 - -
          1.38629  1.38629  1.38629  1.38629
          0.04602  3.79481  3.79481  1.46634  0.26236  1.45579  0.26555
    785   2.68117  2.30926  2.74333  0.26419   3864 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    786   2.14177  2.86811  0.27382  2.72914   3865 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    787   0.29477  2.76358  2.12057  2.62732   3866 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
    788   0.21457  2.95530  2.51653  2.80827   3867 - -
          1.38629  1.38629  1.38629  1.38629
          0.04645  3.79764  3.77396  1.46634  0.26236  1.52698  0.24487
    789   0.21261  2.96323  2.52021  2.82284   3868 - -
          1.38152  1.39208  1.39208  1.37957
          0.05135  3.58888  3.79757  1.22485  0.34786  1.52485  0.24546
    790   2.66442  2.32565  2.70021  0.26729   3874 - -
          1.38629  1.38629  1.38629  1.38629
          0.04753  3.79811  3.72955  1.46634  0.26236  1.54341  0.24035
    791   1.88105  1.73304  0.80515  1.49698   3875 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79652  3.79652  1.46634  0.26236  1.48990  0.25540
    792   2.79090  0.26467  2.85926  2.17274   3876 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    793   2.47382  3.02396  0.21191  2.84570   3877 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    794   2.47366  1.85652  2.54062  0.38465   3878 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    795   0.24885  2.82818  2.45486  2.58614   3879 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    796   2.47617  3.05349  0.20481  2.91991   3881 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    797   0.21027  2.97301  2.52505  2.83994   3882 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    798   2.11252  2.05950  1.68398  0.56931   3883 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    799   0.22117  2.90387  2.49382  2.79657   3884 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    800   2.62410  2.23748  2.69403  0.28348   3885 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    801   1.55986  1.14162  1.69120  1.25094   3886 - -
          1.38820  1.38820  1.38609  1.38269
          0.04766  3.72446  3.79811  1.37541  0.29134  1.54341  0.24035
    802   1.21055  1.62444  1.47525  1.28654   3889 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    803   2.12561  2.55205  0.33122  2.46900   3890 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    804   2.02554  2.35411  0.40174  2.26388   3891 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    805   0.25834  2.73007  2.43381  2.59355   3892 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    806   1.54966  2.53336  0.48415  2.38521   3894 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    807   2.61248  3.14584  0.18102  3.01187   3895 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    808   0.21875  2.91261  2.50623  2.80399   3897 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    809   0.21810  2.91441  2.51006  2.80580   3898 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    810   2.31312  0.56588  2.35017  1.43617   3899 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    811   0.28832  2.70529  2.24870  2.54987   3900 - -
          1.38629  1.38629  1.38629  1.38629
          0.04820  3.79811  3.70317  1.46634  0.26236  1.54341  0.24035
    812   2.67317  0.31666  2.74333  1.98026   3901 - -
          1.38629  1.38629  1.38629  1.38629
          0.04597  3.79588  3.79588  1.46634  0.26236  1.46953  0.26141
    813   2.78131  0.26857  2.84981  2.15662   3902 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    814   0.87098  1.95424  1.22731  1.91931   3903 - -
          1.38353  1.38722  1.38722  1.38722
          0.04673  3.76183  3.79811  1.42069  0.27648  1.54341  0.24035
    815   1.64170  2.58136  0.44157  2.43440   3905 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    816   1.79535  2.07532  2.24233  0.50716   3906 - -
          1.37977  1.39175  1.38576  1.38793
          0.05083  3.63205  3.76804  1.28402  0.32424  1.54341  0.24035
    817   2.18365  2.55981  0.36693  2.14393   3910 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79743  3.79743  1.46634  0.26236  1.51984  0.24686
    818   2.53575  3.02527  0.20170  2.90203   3911 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    819   2.71234  0.26486  2.68477  2.32205   3912 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    820   2.63843  3.15955  0.17728  3.02541   3915 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    821   0.25842  2.77696  2.43467  2.55266   3916 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    822   0.21091  2.97112  2.52110  2.83809   3917 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    823   2.29079  2.96277  0.23837  2.82634   3918 - -
          1.39078  1.38341  1.38024  1.39078
          0.05009  3.63271  3.79811  1.27104  0.32926  1.54341  0.24035
    824   2.48327  2.79772  0.23393  2.74636   3922 - -
          1.38629  1.38629  1.38629  1.38629
          0.04679  3.79811  3.75929  1.46634  0.26236  1.54341  0.24035
    825   2.94493  0.20866  3.01147  2.44757   3923 - -
          1.38629  1.38629  1.38629  1.38629
          0.04687  3.79722  3.75687  1.46634  0.26236  1.51302  0.24877
    826   1.85345  2.68036  0.36232  2.54200   3924 - -
          1.39458  1.39458  1.37626  1.37990
          0.05026  3.62758  3.79719  1.31821  0.31145  1.51182  0.24911
    827   1.46362  2.19141  0.63298  2.07279   3931 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    828   1.85192  0.73956  1.76734  1.63499   3932 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    829   2.05298  1.39843  2.13608  0.68014   3933 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    830   1.66888  1.19361  1.86079  1.04167   3935 - -
          1.38629  1.38629  1.38629  1.38629
          0.04700  3.79811  3.75096  1.46634  0.26236  1.54341  0.24035
    831   1.49901  1.51416  1.63514  1.01685   3936 - -
          1.38629  1.38629  1.38629  1.38629
          0.04591  3.79703  3.79703  1.46634  0.26236  1.50653  0.25062
    832   2.88364  0.22863  2.95072  2.34187   3937 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    833   2.65148  2.30792  2.70315  0.27051   3938 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    834   2.31089  2.96529  0.23546  2.82894   3939 - -
          1.38629  1.38629  1.38629  1.38629
          0.04700  3.79811  3.75096  1.46634  0.26236  1.54341  0.24035
    835   2.48020  2.99566  0.21147  2.86687   3940 - -
          1.38629  1.38629  1.38629  1.38629
          0.04591  3.79703  3.79703  1.46634  0.26236  1.50653  0.25062
    836   1.17286  1.57195  1.31518  1.53966   3941 - -
          1.38348  1.38956  1.38260  1.38956
          0.04894  3.67520  3.79811  1.31822  0.31144  1.54341  0.24035
    837   1.78299  0.78331  1.99930  1.42902   3943 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    838   1.67959  1.06225  1.80990  1.19007   3944 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    839   1.30175  2.02030  0.91705  1.63152   3945 - -
          1.38629  1.38629  1.38629  1.38629
          0.04732  3.79811  3.73805  1.46634  0.26236  1.54341  0.24035
    840   1.28552  1.76790  1.71797  0.98518   3946 - -
          1.38629  1.38629  1.38629  1.38629
          0.04652  3.79672  3.77184  1.46634  0.26236  1.49650  0.25349
    841   1.22813  1.63959  1.68472  1.11595   3947 - -
          1.38806  1.38103  1.38806  1.38806
          0.04755  3.72937  3.79754  1.38193  0.28914  1.52390  0.24572
    842   0.64155  1.81218  2.01754  1.73023   3951 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    843   2.73659  0.28274  2.78658  2.12140   3953 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    844   2.68993  2.32843  2.75196  0.26024   3954 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    845   2.63843  3.15955  0.17728  3.02541   3955 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    846   0.21027  2.97301  2.52505  2.83994   3956 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    847   2.90218  0.21759  2.93035  2.43886   4020 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    848   2.06223  2.73286  0.30803  2.61859   4021 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    849   2.86327  0.23284  2.90588  2.34406   4022 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    850   2.66875  2.33229  2.74299  0.26239   4023 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    851   2.14715  2.17971  0.40454  2.27472   4025 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    852   0.22029  2.93923  2.48226  2.79270   4026 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    853   2.12402  2.42150  0.43682  1.92708   4027 - -
          1.38705  1.38705  1.38705  1.38402
          0.04658  3.76813  3.79811  1.42850  0.27400  1.54341  0.24035
    854   2.34641  2.90473  0.24186  2.74328   4031 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    855   1.61745  0.91674  1.82819  1.42267   4032 - -
          1.38629  1.38629  1.38629  1.38629
          0.04679  3.79811  3.75929  1.46634  0.26236  1.54341  0.24035
    856   1.37269  2.02726  0.82073  1.74430   4034 - -
          1.38629  1.38629  1.38629  1.38629
          0.04590  3.79722  3.79722  1.46634  0.26236  1.51302  0.24877
    857   2.90153  0.22194  2.96842  2.37823   4035 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    858   2.52766  2.97999  0.20944  2.84173   4036 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    859   0.22609  2.89377  2.48144  2.75891   4037 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    860   0.23155  2.86087  2.45196  2.75905   4045 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    861   0.22879  2.92066  2.41849  2.78792   4046 - -
          1.38629  1.38629  1.38629  1.38629
          0.04664  3.79811  3.76566  1.46634  0.26236  1.54341  0.24035
    862   2.63132  3.14783  0.17920  3.01331   4047 - -
          1.38629  1.38629  1.38629  1.38629
          0.04649  3.79737  3.77227  1.46634  0.26236  1.51798  0.24738
    863   2.80738  0.25352  2.85641  2.24339   4048 - -
          1.38629  1.38629  1.38629  1.38629
          0.04639  3.79754  3.77654  1.46634  0.26236  1.52373  0.24577
    864   2.05558  2.46704  0.39522  2.17491   4050 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79763  3.79763  1.46634  0.26236  1.52694  0.24488
    865   2.06922  2.12906  2.34626  0.41697   4051 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    866   2.56455  3.12000  0.18825  2.98613   4052 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    867   2.62891  3.12712  0.18091  3.00600   4053 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    868   2.63843  3.15955  0.17728  3.02541   4054 - -
          1.38784  1.38784  1.38167  1.38784
          0.04781  3.73806  3.77714  1.39170  0.28589  1.54341  0.24035
    869   2.30274  2.58708  0.35104  2.11344   4056 - -
          1.38629  1.38629  1.38629  1.38629
          0.04650  3.79763  3.77192  1.46634  0.26236  1.52696  0.24487
    870   0.21052  2.97183  2.52420  2.83867   4057 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79753  3.79753  1.46634  0.26236  1.52325  0.24590
    871   2.53212  2.92938  0.22060  2.73272   4058 - -
          1.38629  1.38629  1.38629  1.38629
          0.04647  3.79811  3.77239  1.46634  0.26236  1.54341  0.24035
    872   2.95165  0.20710  3.01811  2.45441   4060 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79753  3.79753  1.46634  0.26236  1.52325  0.24590
    873   0.50271  2.46723  1.55340  2.31505   4061 - -
          1.38300  1.38740  1.38740  1.38740
          0.04690  3.75495  3.79811  1.41222  0.27919  1.54341  0.24035
    874   0.21540  2.93422  2.51519  2.81740   4063 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    875   0.21274  2.96408  2.51237  2.83103   4064 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    876   2.68825  0.26857  2.80735  2.23337   4065 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    877   0.31782  2.52626  2.19515  2.51374   4067 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    878   2.63843  3.15955  0.17728  3.02541   4068 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    879   2.62218  3.15099  0.17961  3.01697   4069 - -
          1.38693  1.38693  1.38439  1.38693
          0.04646  3.77305  3.79811  1.43462  0.27208  1.54341  0.24035
    880   0.23007  2.85318  2.47725  2.75059   4075 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    881   2.69211  2.33361  2.75411  0.25922   4076 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    882   2.69384  2.33775  2.75582  0.25841   4078 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    883   0.21492  2.95569  2.51018  2.81183   4079 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    884   2.63110  3.13450  0.18007  3.01043   4082 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    885   0.21400  2.95712  2.51742  2.81310   4083 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    886   2.67221  2.33086  2.72910  0.26343   4084 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    887   0.21666  2.94006  2.49996  2.81602   4085 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    888   2.93656  0.20748  3.01318  2.46293   4086 - -
          1.38738  1.38303  1.38738  1.38738
          0.04689  3.75544  3.79811  1.41282  0.27899  1.54341  0.24035
    889   2.95442  0.20582  3.02086  2.46328   4092 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    890   2.94754  0.20802  3.01402  2.45057   4094 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    891   2.44400  2.06698  2.38620  0.36436   4095 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    892   2.42059  2.95837  0.22811  2.76164   4096 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    893   2.63546  3.15444  0.17810  3.02017   4098 - -
          1.38725  1.38344  1.38725  1.38725
          0.04676  3.76070  3.79811  1.41929  0.27692  1.54341  0.24035
    894   2.68970  2.33565  2.75173  0.25938   4100 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    895   0.21637  2.94466  2.50339  2.81111   4101 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    896   2.61400  3.14665  0.18080  3.01267   4102 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    897   2.69384  2.33775  2.75582  0.25841   4103 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    898   2.95171  0.20723  3.01814  2.45307   4104 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    899   2.90510  0.21967  2.97778  2.39068   4105 - -
          1.38642  1.37987  1.38946  1.38946
          0.04884  3.67879  3.79811  1.32230  0.30996  1.54341  0.24035
    900   0.37111  2.47135  2.24755  2.12107   4107 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    901   2.15199  0.45029  2.36327  1.88262   4108 - -
          1.38724  1.38347  1.38724  1.38724
          0.04675  3.76110  3.79811  1.41980  0.27676  1.54341  0.24035
    902   2.39763  2.96244  0.22432  2.84194   4110 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    903   2.94538  0.20739  3.00706  2.46180   4111 - -
          1.38629  1.38629  1.38629  1.38629
          0.04642  3.79811  3.77473  1.46634  0.26236  1.54341  0.24035
    904   2.13631  0.57539  2.26779  1.53301   4113 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79758  3.79758  1.46634  0.26236  1.52507  0.24540
    905   2.24501  2.11945  0.38986  2.33487   4114 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    906   2.69384  2.33775  2.75582  0.25841   4115 - -
          1.38268  1.38750  1.38750  1.38750
          0.04700  3.75096  3.79811  1.40734  0.28076  1.54341  0.24035
    907   0.21849  2.92815  2.50936  2.78948   4117 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    908   0.21401  2.95768  2.51789  2.81187   4118 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    909   0.21027  2.97301  2.52505  2.83994   4119 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    910   2.96138  0.20416  3.02776  2.47100   4120 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    911   2.54171  2.99000  0.20927  2.81669   4122 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    912   0.43597  2.37484  2.02296  2.05517   4123 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    913   2.69384  2.33775  2.75582  0.25841   4124 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    914   2.60881  3.10288  0.18503  2.98820   4125 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    915   1.06270  1.81156  1.30881  1.50986   4126 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    916   1.26383  1.71050  1.06977  1.64213   4127 - -
          1.38808  1.38096  1.38808  1.38808
          0.04754  3.72906  3.79811  1.38089  0.28949  1.54341  0.24035
    917   1.76720  1.56111  1.94484  0.74176   4129 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    918   0.79170  2.32434  1.09102  2.17856   4130 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    919   2.69042  0.29969  2.77217  2.05124   4131 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    920   2.62652  2.20756  2.67860  0.28896   4132 - -
          1.38808  1.38808  1.38808  1.38096
          0.04754  3.72906  3.79811  1.38089  0.28949  1.54341  0.24035
    921   0.45384  2.27520  2.00409  2.06157   4134 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    922   2.17834  2.89531  0.26395  2.75708   4135 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    923   1.51335  1.73120  0.95138  1.52994   4136 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    924   2.04507  1.60786  2.19995  0.58070   4137 - -
          1.38769  1.38769  1.38213  1.38769
          0.04717  3.74387  3.79811  1.39872  0.28357  1.54341  0.24035
    925   2.42779  2.87605  0.23002  2.79866   4140 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    926   2.35078  2.17430  2.24122  0.37879   4141 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    927   1.70058  1.57986  1.43954  0.98248   4142 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    928   2.02832  2.34605  0.42890  2.10805   4143 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    929   2.06269  2.18809  0.46261  2.03165   4144 - -
          1.38629  1.38629  1.38629  1.38629
          0.05141  3.79811  3.58647  1.46634  0.26236  1.54341  0.24035
    930   1.48771  1.73160  0.90978  1.63735   4145 - -
          1.38629  1.38629  1.38629  1.38629
          0.06563  3.79281  3.19449  1.46634  0.26236  1.53656  0.24223
    931   1.44229  1.69477  1.08886  1.41316   4146 - -
          1.38629  1.38629  1.38629  1.38629
          0.06962  3.77551  3.11613  1.46634  0.26236  1.73655  0.19374
    932   1.50681  1.59738  1.02481  1.52742   4148 - -
          1.38629  1.38629  1.38629  1.38629
          0.13546  3.75387  2.27049  1.46634  0.26236  1.77071  0.18658
    933   1.65452  1.30617  1.31200  1.31424   4149 - -
          1.33163  1.42049  1.46031  1.33866
          0.20507  1.85717  3.53020  0.36213  1.19135  0.49723  0.93703
    934   1.50617  1.52541  1.53942  1.06072   4239 - -
          1.38629  1.38629  1.38629  1.38629
          0.08330  3.79023  2.85880  1.46634  0.26236  1.31531  0.31251
    935   1.62106  1.84436  1.81330  0.73175   4240 - -
          1.38629  1.38629  1.38629  1.38629
          0.04846  3.76303  3.72586  1.46634  0.26236  0.89613  0.52450
    936   1.42344  1.27138  1.81085  1.15468   4241 - -
          1.38629  1.38629  1.38629  1.38629
          0.08254  3.79726  2.86831  1.46634  0.26236  1.51431  0.24841
    937   1.30539  1.37022  1.30275  1.59406   4242 - -
          1.08839  1.49598  1.51895  1.51289
          0.49031  1.76230  1.53286  0.25425  1.49386  1.48175  0.25779
    938   1.44479  1.22578  1.51530  1.38257   4391 - -
          1.38629  1.38629  1.38629  1.38629
          0.06079  3.56087  3.48778  1.46634  0.26236  0.79251  0.60277
    939   1.60682  1.17106  1.27289  1.56342   4392 - -
          1.38629  1.38629  1.38629  1.38629
          0.05064  3.70137  3.70137  1.46634  0.26236  0.91000  0.51504
    940   1.58693  1.08299  1.52847  1.42713   4394 - -
          1.38709  1.38709  1.38709  1.38391
          0.04943  3.73080  3.71907  1.42674  0.27455  1.30972  0.31457
    941   1.51167  1.18979  1.59321  1.30232   4396 - -
          1.38629  1.38629  1.38629  1.38629
          0.04771  3.77705  3.74222  1.46634  0.26236  1.28191  0.32505
    942   1.69556  1.42845  1.63175  0.96434   4397 - -
          1.38629  1.38629  1.38629  1.38629
          0.04630  3.78891  3.78891  1.46634  0.26236  1.28459  0.32402
    943   2.11168  1.92616  1.90557  0.53696   4398 - -
          1.39326  1.38765  1.38903  1.37532
          0.05245  3.55153  3.79811  1.18590  0.36452  1.54341  0.24035
    944   2.18024  0.54049  2.08080  1.71652   4400 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    945   1.12129  1.51343  1.45176  1.51491   4401 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    946   2.40215  2.53257  0.28501  2.55087   4402 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    947   2.44792  2.00097  2.44109  0.36925   4403 - -
          1.38770  1.38209  1.38770  1.38770
          0.04718  3.74341  3.79811  1.39816  0.28376  1.54341  0.24035
    948   1.75752  2.32831  0.49479  2.11722   4408 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    949   1.58137  0.98939  1.70718  1.42244   4409 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    950   2.46689  0.44884  2.53992  1.61993   4410 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    951   2.31797  2.61810  0.29410  2.48428   4412 - -
          1.38629  1.38629  1.38629  1.38629
          0.04732  3.79811  3.73791  1.46634  0.26236  1.54341  0.24035
    952   1.47119  1.07365  1.74184  1.37283   4413 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79672  3.79672  1.46634  0.26236  1.49638  0.25352
    953   0.25095  2.72210  2.43132  2.68414   4414 - -
          1.38637  1.37887  1.38999  1.38999
          0.05051  3.66003  3.74981  1.30116  0.31775  1.54341  0.24035
    954   2.49924  2.79406  0.23093  2.76643   4424 - -
          1.38629  1.38629  1.38629  1.38629
          0.04591  3.79700  3.79700  1.46634  0.26236  1.50563  0.25087
    955   2.31844  0.52845  2.32344  1.54121   4425 - -
          1.38713  1.38713  1.38379  1.38713
          0.05005  3.76514  3.66312  1.42479  0.27517  1.54341  0.24035
    956   2.07486  2.07471  2.19319  0.45056   4427 - -
          1.38629  1.38629  1.38629  1.38629
          0.04601  3.79487  3.79487  1.46634  0.26236  1.43884  0.27076
    957   0.22325  2.90083  2.50043  2.76372   4428 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    958   0.21027  2.97301  2.52505  2.83994   4429 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    959   2.50749  0.28346  2.74348  2.29252   4430 - -
          1.38751  1.38751  1.38267  1.38751
          0.04700  3.75075  3.79811  1.40709  0.28085  1.54341  0.24035
    960   2.13300  2.80748  0.28298  2.69380   4433 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    961   2.71095  0.28279  2.71815  2.17284   4435 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    962   0.60824  2.35095  1.39652  2.18075   4437 - -
          1.38629  1.38629  1.38629  1.38629
          0.04650  3.79811  3.77150  1.46634  0.26236  1.54341  0.24035
    963   1.60062  1.92757  2.07638  0.63990   4439 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79750  3.79750  1.46634  0.26236  1.52255  0.24610
    964   2.52986  2.26241  2.45574  0.31412   4440 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    965   0.21397  2.96222  2.50260  2.82934   4442 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    966   0.21027  2.97301  2.52505  2.83994   4443 - -
          1.38629  1.38629  1.38629  1.38629
          0.04629  3.79811  3.78003  1.46634  0.26236  1.54341  0.24035
    967   2.22001  2.90056  0.25781  2.75425   4444 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79770  3.79770  1.46634  0.26236  1.52923  0.24424
    968   2.21581  1.12203  2.29003  0.76776   4445 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    969   0.73107  1.97783  1.57901  1.74836   4446 - -
          1.38685  1.38685  1.38464  1.38685
          0.04638  3.77629  3.79811  1.43868  0.27081  1.54341  0.24035
    970   1.70638  1.09477  1.70801  1.19522   4453 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    971   1.56863  1.32076  1.81275  1.01741   4454 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    972   2.91808  0.21528  2.96591  2.42890   4455 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    973   2.93213  0.21252  2.99873  2.42680   4456 - -
          1.38751  1.38267  1.38751  1.38751
          0.04700  3.75075  3.79811  1.40709  0.28085  1.54341  0.24035
    974   2.28486  2.85212  0.25187  2.76229   4458 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    975   2.95356  0.20597  3.02001  2.46292   4459 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    976   2.94734  0.20739  3.01385  2.45673   4460 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    977   2.67389  2.33096  2.74163  0.26221   4461 - -
          1.38722  1.38722  1.38352  1.38722
          0.04673  3.76168  3.79811  1.42050  0.27653  1.54341  0.24035
    978   2.62629  3.13372  0.18071  3.00733   4464 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
    979   2.27920  2.92144  0.24629  2.77934   4465 - -
          1.38629  1.38629  1.38629  1.38629
          0.04718  3.79811  3.74341  1.46634  0.26236  1.54341  0.24035
    980   2.62576  3.15123  0.17929  3.01696   4466 - -
          1.38629  1.38629  1.38629  1.38629
          0.04670  3.79685  3.76440  1.46634  0.26236  1.50065  0.25229
    981   2.23703  2.65118  0.32606  2.29370   4468 - -
          1.38629  1.38629  1.38629  1.38629
          0.04590  3.79737  3.79737  1.46634  0.26236  1.51798  0.24738
    982   0.21506  2.94823  2.51156  2.81458   4469 - -
          1.38629  1.38629  1.38629  1.38629
          0.04729  3.79811  3.73915  1.46634  0.26236  1.54341  0.24035
    983   2.49295  2.83536  0.22895  2.76037   4470 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    984   2.67964  2.33348  2.74738  0.26090   4472 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    985   0.21618  2.94687  2.50678  2.80716   4473 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    986   2.74865  0.28190  2.81766  2.10462   4477 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    987   2.55260  3.11170  0.19034  2.97761   4478 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    988   1.75915  1.73296  0.73851  1.75318   4479 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    989   1.84670  1.04314  2.04593  1.01988   4481 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    990   2.83249  0.23283  2.84541  2.39984   4482 - -
          1.38704  1.38704  1.38407  1.38704
          0.04662  3.76753  3.79675  1.42945  0.27370  1.55631  0.23688
    991   2.60180  3.06784  0.18950  2.95722   4484 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79675  3.79675  1.46634  0.26236  1.55631  0.23688
    992   2.94348  0.20785  3.00441  2.46014   4485 - -
          1.38629  1.38629  1.38629  1.38629
          0.04692  3.79675  3.75523  1.46634  0.26236  1.55631  0.23688
    993   0.21438  2.94735  2.51472  2.82025   4486 - -
          1.38629  1.38629  1.38629  1.38629
          0.04648  3.79580  3.77436  1.46634  0.26236  1.56521  0.23451
    994   0.21255  2.96172  2.51791  2.82811   4488 - -
          1.38629  1.38629  1.38629  1.38629
          0.04745  3.79531  3.73526  1.46634  0.26236  1.49055  0.25521
    995   2.57222  2.96237  0.20236  2.89789   4490 - -
          1.38629  1.38629  1.38629  1.38629
          0.04647  3.79577  3.77477  1.46634  0.26236  1.50540  0.25094
    996   1.15640  2.06472  0.93165  1.80408   4491 - -
          1.38629  1.38629  1.38629  1.38629
          0.04670  3.79668  3.76423  1.46634  0.26236  1.53591  0.24240
    997   1.71902  1.42740  1.63692  0.95127   4492 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79642  3.79642  1.46634  0.26236  1.52694  0.24488
    998   2.64186  2.31133  2.69959  0.27127   4493 - -
          1.38621  1.38854  1.38642  1.38402
          0.04881  3.71121  3.76394  1.36087  0.29630  1.51091  0.24937
    999   0.85650  2.31939  1.01305  2.17235   4496 - -
          1.38629  1.38629  1.38629  1.38629
          0.04590  3.79735  3.79735  1.46634  0.26236  1.51739  0.24754
   1000   0.22133  2.92000  2.50407  2.76680   4497 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1001   0.21159  2.96608  2.52129  2.83285   4498 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1002   0.21027  2.97301  2.52505  2.83994   4499 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1003   2.95221  0.20587  3.01869  2.46544   4500 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1004   2.69384  2.33775  2.75582  0.25841   4502 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1005   2.80298  0.25784  2.87110  2.20714   4503 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1006   0.21614  2.93615  2.50875  2.81438   4504 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1007   0.22599  2.87487  2.48655  2.77013   4505 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1008   0.21106  2.96887  2.52281  2.83570   4506 - -
          1.39177  1.37006  1.39177  1.39177
          0.05103  3.59970  3.79811  1.23565  0.34340  1.54341  0.24035
   1009   2.28322  2.66897  0.31827  2.28950   4513 - -
          1.38629  1.38629  1.38629  1.38629
          0.04747  3.79811  3.73173  1.46634  0.26236  1.54341  0.24035
   1010   2.41968  3.03023  0.21387  2.89512   4514 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79657  3.79657  1.46634  0.26236  1.55797  0.23644
   1011   0.21093  2.96989  2.52280  2.83659   4515 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79657  3.79657  1.46634  0.26236  1.55797  0.23644
   1012   0.21249  2.96348  2.51981  2.82484   4516 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79657  3.79657  1.46634  0.26236  1.55797  0.23644
   1013   2.67148  2.28998  2.73380  0.26839   4518 - -
          1.38629  1.38629  1.38629  1.38629
          0.04643  3.79657  3.77563  1.46634  0.26236  1.55797  0.23644
   1014   2.17687  2.19850  2.47333  0.36914   4519 - -
          1.38629  1.38629  1.38629  1.38629
          0.04686  3.79609  3.75840  1.46634  0.26236  1.56242  0.23525
   1015   2.63360  3.15322  0.17841  3.01860   4520 - -
          1.38744  1.38286  1.38744  1.38744
          0.05731  3.75031  3.43624  1.41007  0.27988  1.53274  0.24327
   1016   0.24085  2.85460  2.43327  2.67787   4522 - -
          1.38629  1.38629  1.38629  1.38629
          0.04642  3.78635  3.78635  1.46634  0.26236  1.58308  0.22984
   1017   2.87817  0.21824  2.96347  2.42826   4523 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78789  3.78789  1.46634  0.26236  1.63588  0.21664
   1018   2.61267  3.12245  0.18376  2.98626   4524 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78789  3.78789  1.46634  0.26236  1.63588  0.21664
   1019   2.61314  3.12325  0.18363  2.98708   4525 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78789  3.78789  1.46634  0.26236  1.63588  0.21664
   1020   2.61138  3.12026  0.18412  2.98402   4526 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78789  3.78789  1.46634  0.26236  1.63588  0.21664
   1021   2.40846  2.95284  0.22572  2.81485   4527 - -
          1.38624  1.38624  1.38326  1.38943
          0.04965  3.69820  3.74363  1.36828  0.29376  1.63588  0.21664
   1022   1.55564  2.29505  0.54775  2.20781   4530 - -
          1.38629  1.38629  1.38629  1.38629
          0.05154  3.78687  3.59107  1.46634  0.26236  1.60039  0.22542
   1023   2.74919  0.26740  2.81217  2.20203   4531 - -
          1.38629  1.38629  1.38629  1.38629
          0.04849  3.78299  3.70575  1.46634  0.26236  1.49026  0.25530
   1024   2.81046  0.24510  2.87874  2.29269   4532 - -
          1.38629  1.38629  1.38629  1.38629
          0.04834  3.78583  3.70899  1.46634  0.26236  1.54709  0.23936
   1025   2.67528  0.27472  2.74083  2.23670   4533 - -
          1.38629  1.38629  1.38629  1.38629
          0.04641  3.78656  3.78656  1.46634  0.26236  1.38042  0.28965
   1026   2.51476  3.01316  0.20420  2.90627   4535 - -
          1.38905  1.37808  1.38905  1.38905
          0.04868  3.68888  3.79347  1.33917  0.30390  1.55334  0.23767
   1027   2.89198  0.21506  2.98165  2.43808   4540 - -
          1.38629  1.38629  1.38629  1.38629
          0.04604  3.79423  3.79423  1.46634  0.26236  1.57962  0.23074
   1028   0.21572  2.94980  2.51219  2.80347   4541 - -
          1.38629  1.38629  1.38629  1.38629
          0.04604  3.79423  3.79423  1.46634  0.26236  1.57962  0.23074
   1029   2.94033  0.20867  2.99912  2.45738   4543 - -
          1.38629  1.38629  1.38629  1.38629
          0.04604  3.79423  3.79423  1.46634  0.26236  1.57962  0.23074
   1030   0.21194  2.96515  2.51938  2.83151   4544 - -
          1.38629  1.38629  1.38629  1.38629
          0.04604  3.79423  3.79423  1.46634  0.26236  1.57962  0.23074
   1031   0.21287  2.96244  2.51371  2.82885   4545 - -
          1.38629  1.38629  1.38629  1.38629
          0.04737  3.79423  3.73972  1.46634  0.26236  1.57962  0.23074
   1032   2.60117  3.07754  0.18830  2.96869   4548 - -
          1.38629  1.38629  1.38629  1.38629
          0.05248  3.79297  3.55447  1.46634  0.26236  1.59110  0.22778
   1033   2.81363  0.25238  2.88191  2.23457   4552 - -
          1.38629  1.38629  1.38629  1.38629
          0.04712  3.78689  3.75672  1.46634  0.26236  1.64451  0.21456
   1034   2.18984  2.88813  0.26346  2.74898   4554 - -
          1.38629  1.38629  1.38629  1.38629
          0.04971  3.78619  3.65693  1.46634  0.26236  1.62024  0.22046
   1035   2.61106  3.12260  0.18391  2.98597   4556 - -
          1.38629  1.38629  1.38629  1.38629
          0.04748  3.78375  3.74494  1.46634  0.26236  1.54154  0.24086
   1036   2.30038  1.66331  2.39988  0.47878   4557 - -
          1.38945  1.38945  1.38181  1.38449
          0.04916  3.71201  3.74894  1.39346  0.28531  1.65212  0.21275
   1037   2.61185  3.12849  0.18315  2.99225   4560 - -
          1.38629  1.38629  1.38629  1.38629
          0.04683  3.78513  3.77036  1.46634  0.26236  1.62670  0.21887
   1038   2.60665  3.09646  0.18642  2.97424   4561 - -
          1.38629  1.38629  1.38629  1.38629
          0.04646  3.78555  3.78555  1.46634  0.26236  1.60281  0.22481
   1039   0.21920  2.93866  2.48481  2.80413   4562 - -
          1.38629  1.38629  1.38629  1.38629
          0.04640  3.78678  3.78678  1.46634  0.26236  1.54653  0.23951
   1040   2.33418  2.67453  0.30565  2.32764   4563 - -
          1.38629  1.38629  1.38629  1.38629
          0.04751  3.78914  3.73884  1.46634  0.26236  1.62514  0.21926
   1041   2.48114  0.37317  2.41438  1.97776   4565 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78797  3.78797  1.46634  0.26236  1.63524  0.21679
   1042   0.22601  2.92060  2.44477  2.78645   4566 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78797  3.78797  1.46634  0.26236  1.63524  0.21679
   1043   2.65744  2.28412  2.72021  0.27161   4567 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.78797  3.78797  1.46634  0.26236  1.59755  0.22614
   1044   2.55910  3.04999  0.19552  2.94013   4569 - -
          1.38629  1.38629  1.38629  1.38629
          0.04630  3.78884  3.78884  1.46634  0.26236  1.62773  0.21862
   1045   2.50746  2.05720  2.59180  0.33432   4570 - -
          1.38629  1.38629  1.38629  1.38629
          0.04630  3.78884  3.78884  1.46634  0.26236  1.61027  0.22294
   1046   2.43556  2.80712  0.26490  2.46760   4572 - -
          1.38629  1.38629  1.38629  1.38629
          0.04628  3.78924  3.78924  1.46634  0.26236  1.31099  0.31410
   1047   2.63150  3.13795  0.17977  3.01188   4573 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1048   1.88042  1.88557  2.24389  0.52817   4574 - -
          1.38629  1.38629  1.38629  1.38629
          0.04679  3.79752  3.75983  1.46634  0.26236  1.54901  0.23884
   1049   2.69109  2.33589  2.75316  0.25910   4577 - -
          1.38629  1.38629  1.38629  1.38629
          0.04593  3.79666  3.79666  1.46634  0.26236  1.51944  0.24697
   1050   2.67870  2.30382  2.74089  0.26532   4578 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1051   0.21214  2.96336  2.51960  2.83001   4580 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1052   0.21473  2.95585  2.50396  2.82264   4581 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1053   2.69273  2.33700  2.75474  0.25869   4585 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1054   2.69273  2.33700  2.75474  0.25869   4586 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.54901  0.23884
   1055   2.85994  0.23563  2.91319  2.31918   4587 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79752  3.79752  1.46634  0.26236  1.52310  0.24594
   1056   2.62596  3.13571  0.18057  3.00851   4589 - -
          1.38629  1.38629  1.38629  1.38629
          0.04832  3.79811  3.69850  1.46634  0.26236  1.54341  0.24035
   1057   0.21957  2.92433  2.50198  2.78850   4591 - -
          1.38629  1.38629  1.38629  1.38629
          0.04664  3.79576  3.76763  1.46634  0.26236  1.53103  0.24375
   1058   1.06350  1.65845  1.87048  1.17030   4592 - -
          1.38629  1.38629  1.38629  1.38629
          0.04597  3.79591  3.79591  1.46634  0.26236  1.53604  0.24237
   1059   2.51797  3.00520  0.20664  2.87282   4593 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79655  3.79655  1.46634  0.26236  1.55818  0.23638
   1060   1.76567  0.55597  2.19029  1.94124   4594 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79655  3.79655  1.46634  0.26236  1.55818  0.23638
   1061   0.58384  2.19902  2.09315  1.57004   4595 - -
          1.38629  1.38629  1.38629  1.38629
          0.04594  3.79655  3.79655  1.46634  0.26236  1.51666  0.24775
   1062   0.21303  2.96094  2.51396  2.82765   4596 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79750  3.79750  1.46634  0.26236  1.52235  0.24615
   1063   2.70288  0.24437  2.86261  2.37868   4598 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1064   2.23825  2.65560  0.28699  2.62304   4599 - -
          1.38878  1.38878  1.37887  1.38878
          0.04820  3.70317  3.79811  1.35036  0.29995  1.54341  0.24035
   1065   2.91917  0.21286  2.98599  2.43882   4601 - -
          1.38629  1.38629  1.38629  1.38629
          0.04664  3.79811  3.76566  1.46634  0.26236  1.54341  0.24035
   1066   2.60933  3.09532  0.18801  2.94598   4603 - -
          1.38629  1.38629  1.38629  1.38629
          0.04590  3.79737  3.79737  1.46634  0.26236  1.51798  0.24738
   1067   0.48530  1.93942  2.11150  2.12321   4604 - -
          1.38629  1.38629  1.38629  1.38629
          0.04727  3.79811  3.73972  1.46634  0.26236  1.54341  0.24035
   1068   0.27675  2.79674  2.19909  2.66149   4606 - -
          1.38629  1.38629  1.38629  1.38629
          0.04802  3.79676  3.71127  1.46634  0.26236  1.49779  0.25312
   1069   2.04313  2.73754  0.31438  2.58482   4610 - -
          1.38629  1.38629  1.38629  1.38629
          0.04678  3.79611  3.76159  1.46634  0.26236  1.47681  0.25924
   1070   0.21346  2.96310  2.50658  2.83007   4611 - -
          1.38629  1.38629  1.38629  1.38629
          0.04590  3.79732  3.79732  1.46634  0.26236  1.51637  0.24783
   1071   0.21027  2.97301  2.52505  2.83994   4613 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1072   2.89914  0.21575  2.98425  2.42573   4614 - -
          1.38629  1.38629  1.38629  1.38629
          0.04817  3.79811  3.70442  1.46634  0.26236  1.54341  0.24035
   1073   2.95622  0.20522  3.02274  2.46691   4615 - -
          1.38629  1.38629  1.38629  1.38629
          0.04597  3.79591  3.79591  1.46634  0.26236  1.47049  0.26112
   1074   2.68557  2.31811  2.74765  0.26230   4617 - -
          1.38781  1.38781  1.38781  1.38176
          0.04729  3.73916  3.79811  1.39302  0.28545  1.54341  0.24035
   1075   2.68924  2.32678  2.75127  0.26057   4619 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1076   0.21027  2.97301  2.52505  2.83994   4620 - -
          1.39423  1.39423  1.39423  1.36284
          0.05337  3.52132  3.79811  1.15580  0.37805  1.54341  0.24035
   1077   2.96138  0.20416  3.02776  2.47100   4622 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1078   2.95171  0.20723  3.01814  2.45307   4623 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1079   0.98430  1.80974  1.93084  1.14704   4625 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1080   1.17606  2.25282  0.76356  2.11694   4626 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1081   1.92597  1.67253  0.63856  1.97728   4627 - -
          1.38753  1.38753  1.38260  1.38753
          0.04702  3.74982  3.79811  1.40595  0.28121  1.54341  0.24035
   1082   1.64880  1.66233  1.09532  1.26023   4629 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1083   2.55956  0.36468  2.64674  1.84921   4630 - -
          1.38780  1.38780  1.38780  1.38180
          0.04727  3.73972  3.79811  1.39370  0.28523  1.54341  0.24035
   1084   2.67375  2.33192  2.74316  0.26197   4633 - -
          1.38629  1.38629  1.38629  1.38629
          0.04652  3.79811  3.77055  1.46634  0.26236  1.54341  0.24035
   1085   2.58402  2.29141  2.66498  0.28262   4634 - -
          1.38629  1.38629  1.38629  1.38629
          0.04663  3.79748  3.76650  1.46634  0.26236  1.54937  0.23874
   1086   2.52668  3.09431  0.19485  2.96007   4636 - -
          1.38629  1.38629  1.38629  1.38629
          0.04714  3.79678  3.74623  1.46634  0.26236  1.49832  0.25297
   1087   0.21718  2.93269  2.50553  2.80801   4637 - -
          1.38767  1.38216  1.38767  1.38767
          0.04722  3.74316  3.79695  1.39926  0.28340  1.50388  0.25137
   1088   2.50997  0.28394  2.74309  2.28721   4639 - -
          1.38629  1.38629  1.38629  1.38629
          0.06839  3.79811  3.13059  1.46634  0.26236  1.54341  0.24035
   1089   0.22384  2.90454  2.48414  2.77443   4640 - -
          1.38244  1.38758  1.38758  1.38758
          0.04812  3.72630  3.77660  1.40351  0.28201  1.06058  0.42504
   1090   2.59990  2.29124  2.69253  0.27857   4644 - -
          1.38629  1.38629  1.38629  1.38629
          0.04779  3.79811  3.71915  1.46634  0.26236  1.54341  0.24035
   1091   1.59542  1.25345  1.18518  1.58004   4645 - -
          1.50218  1.22204  1.48099  1.36526
          0.26151  1.57546  3.76367  0.28022  1.40903  1.48186  0.25775
   1092   1.52944  1.15968  1.47780  1.42040   4648 - -
          1.38534  1.38492  1.38746  1.38746
          0.04749  3.75178  3.77640  1.40926  0.28014  1.51787  0.24741
   1093   1.29635  1.35032  1.57231  1.34804   4650 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79763  3.79763  1.46634  0.26236  1.52696  0.24487
   1094   1.53424  1.45849  1.22359  1.35627   4651 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1095   1.30392  1.69169  1.28337  1.31967   4652 - -
          1.38629  1.38629  1.38629  1.38629
          0.05050  3.79811  3.61819  1.46634  0.26236  1.54341  0.24035
   1096   1.94112  2.16862  0.58702  1.68126   4653 - -
          1.32598  1.40427  1.39101  1.42676
          0.19661  1.87427  3.68792  0.75630  0.63375  1.40475  0.28161
   1097   0.74804  1.82120  1.87988  1.54991   4668 - -
          1.38654  1.38452  1.38382  1.39031
          0.05028  3.64622  3.77437  1.28860  0.32249  1.46121  0.26391
   1098   0.80841  1.61396  1.70511  1.75111   4670 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79763  3.79763  1.46634  0.26236  1.52675  0.24493
   1099   1.36313  1.43901  1.41920  1.32776   4671 - -
          1.38757  1.38543  1.38757  1.38461
          0.04753  3.74821  3.77830  1.40399  0.28185  1.54341  0.24035
   1100   1.42630  1.26354  1.44378  1.42247   4673 - -
          1.38629  1.38629  1.38629  1.38629
          0.04719  3.79766  3.74342  1.46634  0.26236  1.52787  0.24462
   1101   1.63312  1.26111  1.50902  1.20326   4674 - -
          1.38629  1.38629  1.38629  1.38629
          0.04680  3.79686  3.76033  1.46634  0.26236  1.50101  0.25219
   1102   1.37858  1.44520  1.61999  1.15689   4675 - -
          1.38629  1.38629  1.38629  1.38629
          0.04650  3.79728  3.77190  1.46634  0.26236  1.51481  0.24827
   1103   1.59480  1.27053  1.31765  1.39190   4676 - -
          1.38629  1.38629  1.38629  1.38629
          0.04633  3.79753  3.77898  1.46634  0.26236  1.52352  0.24583
   1104   1.74205  1.17510  1.68955  1.10428   4677 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79769  3.79769  1.46634  0.26236  1.52886  0.24435
   1105   0.75462  1.81070  1.71958  1.67596   4679 - -
          1.39361  1.39003  1.37171  1.38998
          0.05278  3.54066  3.79811  1.17498  0.36936  1.54341  0.24035
   1106   2.42801  2.79282  0.27036  2.43689   4682 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1107   0.23123  2.89110  2.48611  2.69272   4683 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1108   1.33475  2.41986  0.60708  2.27397   4684 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1109   0.31491  2.56964  2.33125  2.33916   4685 - -
          1.38053  1.39627  1.38423  1.38423
          0.05245  3.55139  3.79811  1.22697  0.34698  1.54341  0.24035
   1110   1.92882  1.67429  1.71300  0.71967   4688 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1111   1.18705  1.82677  1.12668  1.56142   4689 - -
          1.38629  1.38629  1.38629  1.38629
          0.04699  3.79811  3.75133  1.46634  0.26236  1.54341  0.24035
   1112   1.54255  1.56658  1.18748  1.30042   4690 - -
          1.38815  1.38983  1.38344  1.38378
          0.05366  3.66445  3.62567  1.30731  0.31546  1.50681  0.25053
   1113   1.36504  1.72388  1.19340  1.33534   4692 - -
          1.38629  1.38629  1.38629  1.38629
          0.04686  3.79391  3.76070  1.46634  0.26236  1.41121  0.27951
   1114   1.47776  1.78271  1.03990  1.38557   4693 - -
          1.38629  1.38629  1.38629  1.38629
          0.04776  3.79735  3.72110  1.46634  0.26236  1.51739  0.24754
   1115   1.59306  1.62279  1.24276  1.16872   4695 - -
          1.38629  1.38629  1.38629  1.38629
          0.08201  3.79633  2.87731  1.46634  0.26236  1.54339  0.24036
   1116   1.35307  1.42153  1.46211  1.31504   4696 - -
          1.38629  1.38629  1.38629  1.38629
          0.07095  3.76231  3.09521  1.46634  0.26236  1.69436  0.20299
   1117   1.74410  1.58131  1.09229  1.25862   4697 - -
          1.44381  1.45853  1.42583  1.23414
          0.12956  2.32435  3.74354  0.45693  1.00300  0.73827  0.64998
   1118   1.78570  1.52404  1.86347  0.77793   4713 - -
          1.38629  1.38629  1.38629  1.38629
          0.04779  3.79811  3.71913  1.46634  0.26236  1.54341  0.24035
   1119   1.81335  1.05229  1.23171  1.62982   4714 - -
          1.38629  1.38629  1.38629  1.38629
          0.14578  3.79627  2.17865  1.46634  0.26236  1.56082  0.23568
   1120   1.68434  0.68711  2.02742  1.71631   4715 - -
          1.38629  1.38629  1.38629  1.38629
          0.14903  3.70114  2.17367  1.46634  0.26236  2.09197  0.13175
   1121   1.75895  0.95449  1.64744  1.38541   4716 - -
          1.32734  1.50328  1.18081  1.58285
          0.26978  1.57039  3.55817  1.88534  0.16461  0.37185  1.16944
   1122   1.77800  1.63459  1.56188  0.85273   4767 - -
          1.38629  1.38629  1.38629  1.38629
          0.04607  3.79362  3.79362  1.46634  0.26236  1.40305  0.28216
   1123   2.06507  1.88056  2.03675  0.52724   4768 - -
          1.38629  1.38629  1.38629  1.38629
          0.04675  3.79811  3.76095  1.46634  0.26236  1.54341  0.24035
   1124   1.50529  1.00789  1.81943  1.38253   4769 - -
          1.38629  1.38629  1.38629  1.38629
          0.07819  3.79726  2.94162  1.46634  0.26236  1.55147  0.23818
   1125   1.69892  2.42649  0.48323  2.18937   4770 - -
          1.46611  1.56613  1.05043  1.55808
          0.50543  1.43238  1.84507  1.71773  0.19781  1.69519  0.20281
   1126   1.51427  1.69546  0.89148  1.67950   4823 - -
          1.38629  1.38629  1.38629  1.38629
          0.05580  3.62461  3.58946  1.46634  0.26236  0.71806  0.66884
   1127   1.81766  2.00085  0.74216  1.48593   4824 - -
          1.38629  1.38629  1.38629  1.38629
          0.04853  3.74296  3.74296  1.46634  0.26236  0.76710  0.62428
   1128   1.18955  2.00306  0.92725  1.80131   4825 - -
          1.38629  1.38629  1.38629  1.38629
          0.04598  3.79567  3.79567  1.46634  0.26236  1.46312  0.26333
   1129   1.10376  2.05090  0.97015  1.82801   4826 - -
          1.30660  1.42694  1.42351  1.39291
          0.06723  3.15569  3.79811  1.06805  0.42110  1.54341  0.24035
   1130   1.66628  0.80795  1.78564  1.62155   4832 - -
          1.28463  1.40595  1.44479  1.41751
          0.13761  2.57152  2.95371  0.50955  0.91820  1.54341  0.24035
   1131   1.45261  1.40339  1.56821  1.16520   4835 - -
          1.38629  1.38629  1.38629  1.38629
          0.04841  3.76793  3.72305  1.46634  0.26236  0.94855  0.48988
   1132   1.66563  1.21857  1.36794  1.34460   4836 - -
          1.38629  1.38629  1.38629  1.38629
          0.04658  3.79708  3.76895  1.46634  0.26236  1.50830  0.25011
   1133   1.44171  1.55300  1.18452  1.40254   4837 - -
          1.38629  1.38629  1.38629  1.38629
          0.04589  3.79747  3.79747  1.46634  0.26236  1.52136  0.24643
   1134   1.41030  1.66271  1.19573  1.33249   4838 - -
          1.38629  1.38629  1.38629  1.38629
          0.04905  3.79811  3.67107  1.46634  0.26236  1.54341  0.24035
   1135   0.99364  1.94649  1.41017  1.41513   4839 - -
          1.38629  1.38629  1.38629  1.38629
          0.04600  3.79507  3.79507  1.46634  0.26236  1.44491  0.26888
   1136   1.64912  1.24909  1.23294  1.47150   4840 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1137   0.24283  2.84568  2.39720  2.71018   4841 - -
          1.38629  1.38629  1.38629  1.38629
          0.06671  3.79811  3.16714  1.46634  0.26236  1.54341  0.24035
   1138   2.90461  0.21665  2.97234  2.42095   4842 - -
          1.38629  1.38629  1.38629  1.38629
          0.04681  3.77820  3.77820  1.46634  0.26236  1.08462  0.41253
   1139   0.21311  2.96133  2.51960  2.81852   4848 - -
          1.38629  1.38629  1.38629  1.38629
          0.04859  3.79811  3.68824  1.46634  0.26236  1.54341  0.24035
   1140   2.62169  3.14416  0.18044  3.00955   4849 - -
          1.38629  1.38629  1.38629  1.38629
          0.04598  3.79550  3.79550  1.46634  0.26236  1.45805  0.26486
   1141   2.49378  3.07763  0.20010  2.94342   4850 - -
          1.38629  1.38629  1.38629  1.38629
          0.04586  3.79811  3.79811  1.46634  0.26236  1.54341  0.24035
   1142   2.69106  2.33112  2.75308  0.25971   4852 - -
          1.38629  1.38629  1.38629  1.38629
          0.04636  3.79811  3.77717  1.46634  0.26236  1.54341  0.24035
   1143   2.63763  3.15851  0.17747  3.02428   4853 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
   1144   1.90609  1.09946  1.04708  1.78780   4854 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
   1145   2.67459  2.32780  2.73684  0.26295   4855 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
   1146   2.63500  3.15397  0.17819  3.01964   4856 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  1.54793  0.23913
   1147   2.96027  0.20439  3.02668  2.47012   4858 - -
          1.38629  1.38629  1.38629  1.38629
          0.04588  3.79764  3.79764  1.46634  0.26236  0.55404  0.85478
   1148   0.26214  2.85509  2.23991  2.70936   4859 - -
          1.43144  1.27610  1.43144  1.41490
          0.08676  2.78870  3.83508  0.59730  0.79916  1.09861  0.40547
   1149   2.57564  2.04269  2.60847  0.32772   4861 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1150   2.47557  2.57685  0.25860  2.69206   4862 - -
          1.43144  1.43144  1.27610  1.41490
          0.08676  2.78870  3.83508  0.59730  0.79916  1.09861  0.40547
   1151   2.42059  2.51759  0.28026  2.59172   4864 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1152   2.21243  0.84134  2.27180  1.03196   4865 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1153   2.65375  2.15144  2.71585  0.29149   4866 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1154   2.43720  2.74967  0.27929  2.38246   4867 - -
          1.31973  1.31973  1.45669  1.45853
          0.08720  2.78217  3.83508  0.94007  0.49528  1.09861  0.40547
   1155   2.45010  2.22209  2.26088  0.35514   4870 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1156   2.96226  0.19802  3.06217  2.51139   4871 - -
          1.43190  1.27494  1.41535  1.43190
          0.08720  2.78207  3.83508  0.59385  0.80341  1.09861  0.40547
   1157   2.44492  2.52433  0.27073  2.65449   4873 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1158   2.18208  2.24034  2.51318  0.35702   4874 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1159   2.38857  0.30063  2.70207  2.29444   4875 - -
          1.43144  1.43144  1.41490  1.27610
          0.08676  2.78870  3.83508  0.59730  0.79916  1.09861  0.40547
   1160   0.21065  2.97949  2.54560  2.80189   4877 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1161   2.32433  2.99692  0.22814  2.87885   4878 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1162   2.33278  0.33058  2.62261  2.19055   4879 - -
          1.43144  1.41490  1.43144  1.27610
          0.08676  2.78870  3.83508  0.59730  0.79916  1.09861  0.40547
   1163   2.72388  2.36544  2.74817  0.25305   4881 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1164   3.02507  0.19406  3.08909  2.49748   4882 - -
          1.38391  1.40045  1.36090  1.40045
          0.04952  3.62268  3.83508  1.33216  0.30640  1.09861  0.40547
   1165   2.64205  3.20118  0.17197  3.07759   4886 - -
          1.39046  1.39046  1.39046  1.37391
          0.04793  3.68083  3.83508  1.28323  0.32454  1.09861  0.40547
   1166   2.72380  2.36525  2.74810  0.25309   4888 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1167   2.66230  3.15190  0.17710  3.00088   4889 - -
          1.39046  1.39046  1.39046  1.37391
          0.05059  3.68083  3.72434  1.28323  0.32454  1.09861  0.40547
   1168   2.52328  1.94024  2.55907  0.35845   4891 - -
          1.38629  1.38629  1.38629  1.38629
          0.04427  3.83255  3.83255  1.46634  0.26236  1.13691  0.38685
   1169   2.78783  0.26134  2.83898  2.20784   4892 - -
          1.39460  1.39460  1.37806  1.37806
          0.04886  3.67829  3.79763  1.34176  0.30298  1.13691  0.38685
   1170   2.66090  3.17126  0.17610  3.00317   4895 - -
          1.38629  1.38629  1.38629  1.38629
          0.08312  3.83178  2.84576  1.46634  0.26236  1.14824  0.38154
   1171   2.61386  2.31709  2.71161  0.27213   4896 - -
          1.38629  1.38629  1.38629  1.38629
          0.04951  3.79468  3.65676  1.46634  0.26236  0.58949  0.80881
   1172   2.62333  3.15760  0.17766  3.04313   4897 - -
          1.38629  1.38629  1.38629  1.38629
          0.04445  3.82857  3.82857  1.46634  0.26236  0.98278  0.46883
   1173   0.20289  3.02053  2.53661  2.88731   4898 - -
          1.39046  1.39046  1.39046  1.37391
          0.05198  3.67942  3.67253  1.28323  0.32454  1.12013  0.39488
   1174   2.41154  2.99436  0.21667  2.89940   4900 - -
          1.38629  1.38629  1.38629  1.38629
          0.04638  3.82988  3.74600  1.46634  0.26236  1.00720  0.45451
   1175   0.31348  2.69566  2.06383  2.59516   4901 - -
          1.38629  1.38629  1.38629  1.38629
          0.04430  3.83196  3.83196  1.46634  0.26236  1.09695  0.40630
   1176   2.74285  2.34200  2.80301  0.24994   4902 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1177   2.68534  3.22639  0.16631  3.09407   4903 - -
          1.38629  1.38629  1.38629  1.38629
          0.04803  3.83304  3.67878  1.46634  0.26236  1.12959  0.39033
   1178   2.75305  2.37750  2.81318  0.24402   4904 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1179   2.68315  2.21859  2.74464  0.27626   4907 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1180   2.36397  2.85756  0.24857  2.67906   4908 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1181   2.68011  3.19725  0.16892  3.07921   4909 - -
          1.38848  1.38848  1.37977  1.38848
          0.04640  3.74564  3.82943  1.36341  0.29543  1.18209  0.36620
   1182   2.66013  3.13316  0.17602  3.03911   4911 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1183   2.73557  2.36394  2.79593  0.24841   4913 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1184   2.70574  2.27816  2.76201  0.26456   4914 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1185   0.20232  3.00215  2.55450  2.88685   4915 - -
          1.38629  1.38629  1.38629  1.38629
          0.04569  3.82943  3.77472  1.46634  0.26236  1.18209  0.36620
   1186   0.19791  3.03358  2.56827  2.90511   4916 - -
          1.38629  1.38629  1.38629  1.38629
          0.04447  3.82820  3.82820  1.46634  0.26236  1.14448  0.38330
   1187   2.67716  3.20051  0.16922  3.07521   4917 - -
          1.38629  1.38629  1.38629  1.38629
          0.04577  3.82943  3.77157  1.46634  0.26236  1.18209  0.36620
   1188   2.73177  2.37189  2.80137  0.24735   4918 - -
          1.39156  1.37554  1.39156  1.38659
          0.05058  3.63644  3.77343  1.24277  0.34050  1.14233  0.38430
   1189   2.94001  0.21122  2.96893  2.45135   4920 - -
          1.38629  1.38629  1.38629  1.38629
          0.04447  3.82820  3.82820  1.46634  0.26236  1.14448  0.38330
   1190   3.01469  0.19438  3.06845  2.51203   4921 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1191   2.72704  0.27905  2.77578  2.15602   4922 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.18209  0.36620
   1192   2.31996  2.94715  0.23917  2.78137   4923 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82943  3.82943  1.46634  0.26236  1.02783  0.44283
   1193   2.59807  0.29976  2.75433  2.11247   4924 - -
          1.36791  1.39250  1.39250  1.39250
          0.04990  3.61080  3.83304  1.21077  0.35378  1.12959  0.39033
   1194   0.19602  3.04324  2.57508  2.91553   4933 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1195   0.19895  3.02037  2.56846  2.90087   4934 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1196   3.03721  0.19000  3.10121  2.52472   4935 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1197   2.69089  3.22610  0.16609  3.09005   4936 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1198   0.19697  3.04026  2.56879  2.91258   4938 - -
          1.38629  1.38629  1.38629  1.38629
          0.04496  3.83304  3.80212  1.46634  0.26236  1.12959  0.39033
   1199   2.63687  3.20350  0.17243  3.07526   4939 - -
          1.38847  1.38847  1.37978  1.38847
          0.04739  3.70378  3.83236  1.31181  0.31380  1.13969  0.38554
   1200   3.02095  0.19276  3.07870  2.51887   4941 - -
          1.38629  1.38629  1.38629  1.38629
          0.04428  3.83236  3.83236  1.46634  0.26236  1.13969  0.38554
   1201   2.69163  3.22873  0.16536  3.10029   4942 - -
          1.38629  1.38629  1.38629  1.38629
          0.04518  3.83236  3.79361  1.46634  0.26236  1.13969  0.38554
   1202   2.76598  0.22955  2.92922  2.42183   4943 - -
          1.38629  1.38629  1.38629  1.38629
          0.04432  3.83151  3.83151  1.46634  0.26236  1.11350  0.39811
   1203   0.19862  3.02224  2.56938  2.90296   4944 - -
          1.38334  1.38728  1.38728  1.38728
          0.04518  3.79361  3.83236  1.41765  0.27745  1.13969  0.38554
   1204   0.20166  2.99724  2.56324  2.88873   4951 - -
          1.38629  1.38629  1.38629  1.38629
          0.04504  3.83236  3.79943  1.46634  0.26236  1.13969  0.38554
   1205   3.03945  0.18901  3.10351  2.53237   4952 - -
          1.38629  1.38629  1.38629  1.38629
          0.04432  3.83164  3.83164  1.46634  0.26236  1.11740  0.39620
   1206   3.04113  0.18870  3.10513  2.53368   4953 - -
          1.38629  1.38629  1.38629  1.38629
          0.04428  3.83236  3.83236  1.46634  0.26236  1.10876  0.40043
   1207   3.03867  0.18958  3.10266  2.52743   4954 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1208   2.22531  1.40837  2.32482  0.59852   4955 - -
          1.38629  1.38629  1.38629  1.38629
          0.04458  3.83304  3.81870  1.46634  0.26236  1.12959  0.39033
   1209   2.32994  1.44540  2.40098  0.55092   4957 - -
          1.38629  1.38629  1.38629  1.38629
          0.04427  3.83273  3.83273  1.46634  0.26236  1.11990  0.39499
   1210   0.96931  2.28590  0.92350  2.10500   4958 - -
          1.38629  1.38629  1.38629  1.38629
          0.04529  3.83304  3.78813  1.46634  0.26236  1.12959  0.39033
   1211   2.23443  1.57217  2.33945  0.52938   4961 - -
          1.38629  1.38629  1.38629  1.38629
          0.04430  3.83205  3.83205  1.46634  0.26236  1.09941  0.40507
   1212   2.00306  0.95825  1.97846  1.06935   4962 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1213   1.66193  1.25797  1.44050  1.24068   4963 - -
          1.38130  1.39000  1.39000  1.38391
          0.04762  3.69460  3.83304  1.30076  0.31790  1.12959  0.39033
   1214   2.22475  1.63757  2.30196  0.51518   4966 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1215   1.85411  1.85017  1.98457  0.60010   4967 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1216   0.51142  2.30002  2.16219  1.68724   4968 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1217   2.51744  2.94901  0.21495  2.80738   4969 - -
          1.38629  1.38629  1.38629  1.38629
          0.04587  3.83304  3.76399  1.46634  0.26236  1.12959  0.39033
   1218   2.75695  2.38010  2.81695  0.24311   4971 - -
          1.38629  1.38629  1.38629  1.38629
          0.04567  3.83149  3.77364  1.46634  0.26236  1.08338  0.41317
   1219   2.59056  2.34370  2.73222  0.26922   4972 - -
          1.38629  1.38629  1.38629  1.38629
          0.04431  3.83175  3.83175  1.46634  0.26236  1.14865  0.38135
   1220   2.06179  2.86382  0.28734  2.72622   4973 - -
          1.38629  1.38629  1.38629  1.38629
          0.04912  3.83175  3.63961  1.46634  0.26236  1.14865  0.38135
   1221   2.95714  0.20628  2.98737  2.47686   4975 - -
          1.38629  1.38629  1.38629  1.38629
          0.04898  3.82715  3.64873  1.46634  0.26236  1.21366  0.35255
   1222   2.43522  0.46769  2.48431  1.59655   4976 - -
          1.38629  1.38629  1.38629  1.38629
          0.04558  3.82289  3.78592  1.46634  0.26236  1.23924  0.34193
   1223   0.20683  2.97861  2.54326  2.85821   4978 - -
          1.38629  1.38629  1.38629  1.38629
          0.05982  3.82275  3.31863  1.46634  0.26236  1.23489  0.34371
   1224   1.70322  1.87429  0.88362  1.38168   4979 - -
          1.38629  1.38629  1.38629  1.38629
          0.04581  3.80915  3.78922  1.46634  0.26236  0.92746  0.50345
   1225   2.80815  0.25679  2.88953  2.20228   4981 - -
          1.38836  1.37575  1.39058  1.39058
          0.05871  3.66476  3.46068  1.27871  0.32628  1.26693  0.33086
   1226   0.52617  2.12774  1.73719  2.17142   4983 - -
          1.38467  1.38895  1.38895  1.38261
          0.19197  3.71232  1.89547  1.34307  0.30252  1.33381  0.30581
   1227   1.60118  1.35985  1.29646  1.31623   4985 - -
          1.40363  1.54728  1.20108  1.42462
          0.38041  1.23529  3.66245  1.53781  0.24188  0.24852  1.51393
   1228   2.05657  1.99266  2.07444  0.49405   5166 - -
          1.38629  1.38629  1.38629  1.38629
          0.04432  3.83163  3.83163  1.46634  0.26236  1.08736  0.41114
   1229   1.33622  1.75347  1.89299  0.88341   5167 - -
          1.38629  1.38629  1.38629  1.38629
          0.04474  3.83304  3.81181  1.46634  0.26236  1.12959  0.39033
   1230   0.98447  1.58053  1.62675  1.49644   5168 - -
          1.38629  1.38629  1.38629  1.38629
          0.04910  3.83258  3.63963  1.46634  0.26236  1.11527  0.39724
   1231   1.17030  2.00238  1.05100  1.58414   5169 - -
          1.39674  1.84171  1.05644  1.40096
          0.32079  2.49688  1.64984  2.50196  0.08548  1.13619  0.38719
   1232   2.15411  2.27148  0.38718  2.28410   5515 - -
          1.38629  1.38629  1.38629  1.38629
          0.05375  3.64331  3.64331  1.46634  0.26236  0.34018  1.24355
   1233   1.75998  1.39772  1.45645  1.05633   5516 - -
          1.38629  1.38629  1.38629  1.38629
          0.04536  3.80894  3.80894  1.46634  0.26236  1.36717  0.29414
   1234   2.20676  1.72356  2.08432  0.53252   5517 - -
          1.38974  1.38974  1.38104  1.38469
          0.04898  3.68113  3.78947  1.31096  0.31411  0.94974  0.48913
   1235   2.39439  3.05033  0.21422  2.91402   5519 - -
          1.38629  1.38629  1.38629  1.38629
          0.04470  3.82311  3.82311  1.46634  0.26236  1.24624  0.33909
   1236   1.82969  2.71176  0.36166  2.56914   5520 - -
          1.38629  1.38629  1.38629  1.38629
          0.04582  3.82357  3.77497  1.46634  0.26236  1.20878  0.35462
   1237   2.64763  3.17694  0.17443  3.04639   5521 - -
          1.39252  1.36784  1.39252  1.39252
          0.05150  3.60061  3.77692  1.20993  0.35413  1.02767  0.44292
   1238   1.58935  1.04849  1.45082  1.55543   5524 - -
          1.38629  1.38629  1.38629  1.38629
          0.04447  3.82832  3.82832  1.46634  0.26236  1.00068  0.45828
   1239   0.22060  2.93979  2.47485  2.79837   5525 - -
          1.38629  1.38629  1.38629  1.38629
          0.05279  3.83304  3.51396  1.46634  0.26236  1.12959  0.39033
   1240   2.98228  0.20002  3.05743  2.48170   5526 - -
          1.39665  1.39188  1.39665  1.36046
          0.05417  3.47676  3.82487  1.08780  0.41092  0.92514  0.50497
   1241   2.68152  2.31362  2.76423  0.26187   5531 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1242   2.68444  0.28965  2.79539  2.10271   5532 - -
          1.37591  1.38549  1.39193  1.39193
          0.04938  3.62923  3.83304  1.22996  0.34574  1.12959  0.39033
   1243   1.71947  2.04837  2.14315  0.55407   5534 - -
          1.37298  1.39077  1.39077  1.39077
          0.04832  3.66792  3.83304  1.27134  0.32914  1.12959  0.39033
   1244   0.57102  2.06183  1.89929  1.84416   5536 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1245   1.03081  2.14924  0.93959  1.99569   5537 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1246   1.31176  1.48808  1.23014  1.54836   5538 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83304  3.83304  1.46634  0.26236  1.12959  0.39033
   1247   2.18979  2.49256  0.33012  2.44728   5539 - -
          1.38215  1.38859  1.38586  1.38859
          0.04633  3.74515  3.83304  1.35859  0.29709  1.12959  0.39033
   1248   0.49749  2.40632  1.63843  2.23014   5541 - -
          1.38629  1.38629  1.38629  1.38629
          0.04473  3.83304  3.81204  1.46634  0.26236  1.12959  0.39033
   1249   1.86587  2.52777  0.41160  2.27488   5542 - -
          1.38629  1.38629  1.38629  1.38629
          0.04427  3.83258  3.83258  1.46634  0.26236  1.08675  0.41145
   1250   0.19897  3.03455  2.55503  2.90704   5545 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1251   3.02989  0.19167  3.09394  2.51607   5547 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1252   2.49445  2.06205  2.61789  0.33225   5548 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1253   2.67074  3.15515  0.17336  3.05052   5550 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1254   3.02625  0.19027  3.09786  2.53044   5551 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1255   2.96908  0.20817  3.02681  2.42912   5552 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1256   1.76340  2.05984  0.64254  1.74234   5553 - -
          1.39556  1.39556  1.35900  1.39556
          0.04900  3.64228  3.83369  1.29893  0.31859  1.11994  0.39497
   1257   1.93649  2.16586  0.56777  1.74669   5564 - -
          1.38629  1.38629  1.38629  1.38629
          0.04465  3.83369  3.81479  1.46634  0.26236  1.11994  0.39497
   1258   1.90654  1.64242  1.43326  0.86902   5566 - -
          1.38699  1.38699  1.38421  1.38699
          0.04550  3.80585  3.80571  1.43167  0.27300  1.10725  0.40117
   1259   2.24892  2.89990  0.25574  2.73164   5586 - -
          1.38629  1.38629  1.38629  1.38629
          0.10568  3.83308  2.54282  1.46634  0.26236  1.10146  0.40405
   1260   0.73432  1.98657  2.00064  1.39533   5587 - -
          1.38629  1.38629  1.38629  1.38629
          0.04958  3.77503  3.67153  1.46634  0.26236  0.44992  1.01522
   1261   1.90313  1.12402  2.07084  0.91667   5588 - -
          1.38629  1.38629  1.38629  1.38629
          0.04433  3.83132  3.83132  1.46634  0.26236  1.05141  0.42993
   1262   0.23807  2.88132  2.39856  2.73421   5589 - -
          1.38629  1.38629  1.38629  1.38629
          0.06638  3.83369  3.15612  1.46634  0.26236  1.11994  0.39497
   1263   0.21197  2.95090  2.52259  2.83932   5590 - -
          1.36853  1.38557  1.39566  1.39566
          0.05393  3.49304  3.81250  1.11460  0.39757  0.71713  0.66973
   1264   1.04109  1.42951  1.42721  1.78661   5602 - -
          1.39253  1.39253  1.39253  1.36780
          0.04990  3.61022  3.83369  1.20951  0.35431  1.11994  0.39497
   1265   1.73907  0.88782  1.80672  1.39201   5604 - -
          1.38629  1.38629  1.38629  1.38629
          0.04464  3.83369  3.81527  1.46634  0.26236  1.11994  0.39497
   1266   1.78081  0.70191  1.97994  1.62059   5605 - -
          1.38629  1.38629  1.38629  1.38629
          0.04622  3.83328  3.74937  1.46634  0.26236  1.12599  0.39205
   1267   2.60119  3.15945  0.17988  3.03664   5606 - -
          1.36494  1.40308  1.40984  1.36814
          0.08226  2.87047  3.80327  0.64359  0.74529  1.05312  0.42901
   1268   2.68300  3.21678  0.16702  3.09285   5608 - -
          1.37430  1.39032  1.39032  1.39032
          0.04791  3.68338  3.83307  1.28826  0.32262  1.10109  0.40423
   1269   0.19780  3.03456  2.57108  2.90197   5610 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1270   2.64403  3.20905  0.17124  3.08104   5611 - -
          1.38629  1.38629  1.38629  1.38629
          0.04493  3.83369  3.80286  1.46634  0.26236  1.11994  0.39497
   1271   2.67901  3.22664  0.16657  3.09851   5614 - -
          1.38407  1.38704  1.38704  1.38704
          0.04493  3.80373  3.83301  1.42937  0.27373  1.09928  0.40513
   1272   0.19807  3.03733  2.56085  2.90980   5617 - -
          1.36255  1.39434  1.39434  1.39434
          0.04788  3.68400  3.83369  1.34509  0.30180  1.11994  0.39497
   1273   0.20216  3.02472  2.53464  2.89725   5620 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1274   2.69667  3.23671  0.16415  3.10864   5621 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1275   2.69299  3.23023  0.16509  3.10198   5622 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1276   2.35662  2.02585  2.50225  0.36892   5623 - -
          1.38629  1.38629  1.38629  1.38629
          0.04527  3.83369  3.78834  1.46634  0.26236  1.11994  0.39497
   1277   2.64169  3.18666  0.17381  3.05770   5626 - -
          1.38629  1.38629  1.38629  1.38629
          0.04427  3.83268  3.83268  1.46634  0.26236  1.08962  0.40999
   1278   2.15325  2.83637  0.28024  2.66422   5629 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1279   2.69667  3.23671  0.16415  3.10864   5630 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1280   2.69473  3.23329  0.16465  3.10513   5632 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83369  3.83369  1.46634  0.26236  1.11994  0.39497
   1281   0.20119  3.02768  2.54076  2.90021   5633 - -
          1.37430  1.39032  1.39032  1.39032
          0.04788  3.68400  3.83369  1.28826  0.32262  1.08294  0.41340
   1282   2.42667  1.67184  2.49098  0.44482   5635 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1283   2.61121  3.04595  0.19314  2.90704   5636 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1284   0.19612  3.04405  2.57271  2.91660   5637 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1285   3.01860  0.19529  3.07856  2.49483   5638 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1286   2.66502  3.16539  0.17541  3.01405   5640 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1287   2.75372  2.36280  2.81366  0.24569   5641 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1288   2.99055  0.19600  3.06611  2.51176   5642 - -
          1.38629  1.38629  1.38629  1.38629
          0.08405  3.83450  2.83013  1.46634  0.26236  1.10756  0.40102
   1289   0.23860  2.81053  2.46789  2.69804   5643 - -
          1.37430  1.39032  1.39032  1.39032
          0.04975  3.64670  3.79639  1.28826  0.32262  0.55528  0.85311
   1290   0.24361  2.90923  2.30629  2.77970   5646 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1291   1.09335  2.37226  0.76867  2.22554   5647 - -
          1.37430  1.39032  1.39032  1.39032
          0.04784  3.68481  3.83450  1.28826  0.32262  1.10756  0.40102
   1292   2.76262  2.38388  2.82244  0.24179   5649 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1293   2.89648  0.20734  3.02176  2.48498   5650 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1294   0.51057  1.78312  2.17020  2.14063   5654 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1295   2.41357  2.22815  2.18206  0.37111   5657 - -
          1.38629  1.38629  1.38629  1.38629
          0.04474  3.83450  3.81009  1.46634  0.26236  1.10756  0.40102
   1296   3.00444  0.19784  3.05261  2.49262   5658 - -
          1.38629  1.38629  1.38629  1.38629
          0.04421  3.83397  3.83397  1.46634  0.26236  1.09128  0.40915
   1297   0.20546  3.01533  2.51318  2.88796   5659 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1298   2.71912  2.28347  2.77973  0.26126   5661 - -
          1.38629  1.38629  1.38629  1.38629
          0.04491  3.83450  3.80303  1.46634  0.26236  1.10756  0.40102
   1299   2.66093  3.19648  0.17117  3.06762   5662 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83381  3.83381  1.46634  0.26236  1.08660  0.41153
   1300   1.94595  1.00954  1.09114  1.85197   5663 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1301   3.02902  0.19168  3.08456  2.52175   5665 - -
          1.38629  1.38629  1.38629  1.38629
          0.04495  3.83450  3.80129  1.46634  0.26236  1.10756  0.40102
   1302   2.97347  0.20947  3.03821  2.40864   5666 - -
          1.38629  1.38629  1.38629  1.38629
          0.04459  3.83377  3.81744  1.46634  0.26236  1.11866  0.39559
   1303   2.73586  0.29981  2.80460  2.01238   5668 - -
          1.38629  1.38629  1.38629  1.38629
          0.04424  3.83341  3.83341  1.46634  0.26236  1.07501  0.41748
   1304   2.30619  2.27573  2.58188  0.32572   5669 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83450  3.83450  1.46634  0.26236  1.10756  0.40102
   1305   2.69512  2.36169  2.75964  0.25503   5670 - -
          1.38629  1.38629  1.38629  1.38629
          0.04467  3.83450  3.81341  1.46634  0.26236  1.08095  0.41442
   1306   0.19682  3.03831  2.57301  2.91064   5671 - -
          1.37430  1.39032  1.39032  1.39032
          0.04783  3.68493  3.83462  1.28826  0.32262  1.08460  0.41255
   1307   2.30793  1.41544  2.38252  0.57023   5676 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1308   2.42422  3.08732  0.20596  2.95715   5677 - -
          1.38767  1.38216  1.38767  1.38767
          0.04541  3.78129  3.83508  1.39926  0.28340  1.09861  0.40547
   1309   1.35521  1.51318  1.49529  1.21162   5679 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1310   2.04103  0.68739  1.63864  1.75461   5680 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1311   2.20680  0.76396  2.26091  1.13983   5681 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1312   1.23488  1.94237  1.83827  0.89975   5683 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1313   2.69398  3.23392  0.16463  3.10598   5684 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1314   2.69891  3.23970  0.16366  3.11187   5685 - -
          1.39032  1.39032  1.37430  1.39032
          0.04781  3.68539  3.83508  1.28826  0.32262  1.09861  0.40547
   1315   2.68209  3.20691  0.16848  3.07591   5687 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1316   3.03224  0.19195  3.09619  2.51057   5688 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1317   2.30408  1.94898  2.22188  0.43182   5689 - -
          1.38799  1.38124  1.38799  1.38799
          0.04569  3.76955  3.83508  1.38510  0.28808  1.09861  0.40547
   1318   0.45981  2.38335  2.00428  1.95478   5691 - -
          1.38629  1.38629  1.38629  1.38629
          0.04569  3.83508  3.76955  1.46634  0.26236  1.09861  0.40547
   1319   2.99262  0.19540  3.06525  2.51705   5692 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83362  3.83362  1.46634  0.26236  1.05540  0.42779
   1320   0.19523  3.04731  2.57794  2.91992   5693 - -
          1.37770  1.38016  1.39372  1.39372
          0.05091  3.57425  3.83508  1.17160  0.37088  1.09861  0.40547
   1321   2.50362  0.27883  2.73921  2.33382   5695 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1322   0.24783  2.89056  2.30039  2.75293   5696 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1323   2.99595  0.19705  3.03869  2.51380   5697 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1324   2.17597  2.93784  0.25762  2.80287   5698 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1325   2.73128  2.30917  2.79162  0.25593   5699 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1326   2.24632  2.68741  0.27783  2.67758   5700 - -
          1.38791  1.38147  1.38791  1.38791
          0.04645  3.77249  3.79909  1.38863  0.28690  1.09861  0.40547
   1327   2.41892  0.29971  2.70692  2.27100   5702 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83429  3.83429  1.46634  0.26236  1.07476  0.41761
   1328   2.74916  2.37732  2.80914  0.24467   5703 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1329   0.19523  3.04731  2.57794  2.91992   5704 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1330   3.04741  0.18754  3.11122  2.53858   5705 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1331   0.19523  3.04731  2.57794  2.91992   5708 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1332   0.20133  3.02836  2.53833  2.90110   5709 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1333   2.76372  2.38461  2.82350  0.24154   5710 - -
          1.38629  1.38629  1.38629  1.38629
          0.04542  3.83508  3.78085  1.46634  0.26236  1.09861  0.40547
   1334   2.69698  3.23712  0.16408  3.10909   5711 - -
          1.38780  1.38780  1.38180  1.38780
          0.04557  3.77549  3.83388  1.39370  0.28523  1.06278  0.42387
   1335   2.63258  3.07795  0.18350  3.00179   5715 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1336   1.77346  1.01815  1.72609  1.23438   5716 - -
          1.38735  1.38528  1.38735  1.38520
          0.04512  3.79366  3.83508  1.41436  0.27850  1.09861  0.40547
   1337   1.66729  1.20174  1.38578  1.34538   5718 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1338   1.63163  1.94698  0.74496  1.67701   5719 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1339   1.75764  2.01573  0.67311  1.69171   5720 - -
          1.38629  1.38629  1.38629  1.38629
          0.04451  3.83508  3.81990  1.46634  0.26236  1.09861  0.40547
   1340   1.92504  1.81253  1.64495  0.69742   5721 - -
          1.38629  1.38629  1.38629  1.38629
          0.04559  3.83475  3.77381  1.46634  0.26236  1.08852  0.41055
   1341   0.21570  2.97364  2.48851  2.81552   5722 - -
          1.38312  1.38736  1.38736  1.38736
          0.04518  3.79213  3.83373  1.41415  0.27857  1.05840  0.42619
   1342   2.86684  0.21437  2.96508  2.47083   5724 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1343   0.21441  2.90815  2.53976  2.82145   5725 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1344   0.76443  2.36324  1.10461  2.21690   5726 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1345   0.74015  1.71535  1.97267  1.58978   5727 - -
          1.37487  1.39013  1.39013  1.39013
          0.04764  3.69205  3.83508  1.29564  0.31982  1.09861  0.40547
   1346   2.37384  2.76952  0.24783  2.75364   5731 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1347   1.13259  2.05989  0.89498  1.95392   5732 - -
          1.38629  1.38629  1.38629  1.38629
          0.04492  3.83508  3.80187  1.46634  0.26236  1.09861  0.40547
   1348   2.69156  3.22956  0.16527  3.10140   5733 - -
          1.40645  1.38444  1.34896  1.40645
          0.06110  3.40177  3.65116  1.09586  0.40684  1.10981  0.39991
   1349   1.26954  1.34752  1.73419  1.26367   5842 - -
          1.38629  1.38629  1.38629  1.38629
          0.04551  3.83000  3.78171  1.46634  0.26236  1.17397  0.36981
   1350   1.14070  1.60240  1.75774  1.18235   5843 - -
          1.38551  1.38899  1.38899  1.38171
          0.04689  3.72649  3.82892  1.34166  0.30301  1.16080  0.37577
   1351   2.66056  3.14128  0.17643  3.02394   5845 - -
          1.38629  1.38629  1.38629  1.38629
          0.04441  3.82955  3.82955  1.46634  0.26236  1.12917  0.39053
   1352   3.01356  0.19499  3.06695  2.50746   5846 - -
          1.38629  1.38629  1.38629  1.38629
          0.04436  3.83069  3.83069  1.46634  0.26236  1.16409  0.37427
   1353   1.20805  1.72738  1.10227  1.65362   5847 - -
          1.38629  1.38629  1.38629  1.38629
          0.04470  3.83069  3.81582  1.46634  0.26236  1.16409  0.37427
   1354   0.22491  2.94683  2.41820  2.81635   5848 - -
          1.37534  1.38736  1.39128  1.39128
          0.04967  3.64803  3.79808  1.25275  0.33648  1.15389  0.37893
   1355   1.03644  1.71435  1.52282  1.39792   5851 - -
          1.38629  1.38629  1.38629  1.38629
          0.04439  3.82998  3.82998  1.46634  0.26236  1.14200  0.38446
   1356   1.20515  1.40686  1.29936  1.69972   5852 - -
          1.38629  1.38629  1.38629  1.38629
          0.04436  3.83069  3.83069  1.46634  0.26236  1.16409  0.37427
   1357   1.90193  0.78300  1.78707  1.48618   5853 - -
          1.38629  1.38629  1.38629  1.38629
          0.04467  3.83069  3.81708  1.46634  0.26236  1.16409  0.37427
   1358   1.75578  0.95053  1.49272  1.53280   5855 - -
          1.38728  1.38333  1.38728  1.38728
          0.04527  3.79158  3.83039  1.41756  0.27747  1.15475  0.37853
   1359   2.68524  3.20651  0.16759  3.08787   5858 - -
          1.38629  1.38629  1.38629  1.38629
          0.04436  3.83069  3.83069  1.46634  0.26236  1.16409  0.37427
   1360   2.23050  0.75697  2.31564  1.12474   5859 - -
          1.38629  1.38629  1.38629  1.38629
          0.04436  3.83069  3.83069  1.46634  0.26236  1.16409  0.37427
   1361   2.15554  2.90055  0.26630  2.76533   5860 - -
          1.38629  1.38629  1.38629  1.38629
          0.04436  3.83069  3.83069  1.46634  0.26236  1.16409  0.37427
   1362   0.19880  3.03131  2.56452  2.89895   5861 - -
          1.38304  1.38738  1.38738  1.38738
          0.04585  3.78808  3.80887  1.41290  0.27897  1.16409  0.37427
   1363   1.69670  1.54044  0.85839  1.72271   5863 - -
          1.38629  1.38629  1.38629  1.38629
          0.04438  3.83021  3.83021  1.46634  0.26236  1.14913  0.38113
   1364   1.70724  1.86788  0.66777  1.88826   5865 - -
          1.38629  1.38629  1.38629  1.38629
          0.04583  3.83069  3.76799  1.46634  0.26236  1.16409  0.37427
   1365   1.85123  1.66234  1.41698  0.88961   5866 - -
          1.38629  1.38629  1.38629  1.38629
          0.04442  3.82928  3.82928  1.46634  0.26236  1.12139  0.39427
   1366   1.84277  1.58613  0.81516  1.63816   5867 - -
          1.38729  1.38729  1.38729  1.38332
          0.04644  3.79166  3.78001  1.41730  0.27756  1.16409  0.37427
   1367   1.49759  2.21392  0.62609  2.02207   5869 - -
          1.38807  1.40291  1.40117  1.35381
          0.05974  3.31674  3.82956  0.94577  0.49164  1.12951  0.39037
   1368   0.29361  2.62669  2.33628  2.46010   5874 - -
          1.38629  1.38629  1.38629  1.38629
          0.04598  3.83069  3.76164  1.46634  0.26236  1.13088  0.38971
   1369   2.67934  3.20687  0.16958  3.06000   5875 - -
          1.38629  1.38629  1.38629  1.38629
          0.04440  3.82987  3.82987  1.46634  0.26236  0.97693  0.47235
   1370   2.99822  0.19822  3.05548  2.49090   5876 - -
          1.38970  1.38970  1.37614  1.38970
          0.04936  3.70665  3.74640  1.31249  0.31355  1.08499  0.41234
   1371   1.50080  1.56773  1.23348  1.28282   5881 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83309  3.83309  1.46634  0.26236  1.04066  0.43575
   1372   0.28948  2.79440  2.11754  2.66113   5882 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1373   0.20305  2.99584  2.55958  2.87467   5883 - -
          1.38629  1.38629  1.38629  1.38629
          0.04653  3.83508  3.73526  1.46634  0.26236  1.09861  0.40547
   1374   2.02376  2.06673  2.37855  0.43300   5884 - -
          1.38629  1.38629  1.38629  1.38629
          0.04480  3.83281  3.80946  1.46634  0.26236  1.03318  0.43986
   1375   3.03360  0.19143  3.09756  2.51431   5891 - -
          1.38629  1.38629  1.38629  1.38629
          0.04418  3.83457  3.83457  1.46634  0.26236  1.08310  0.41331
   1376   2.02601  1.15110  2.03818  0.86373   5892 - -
          1.38629  1.38629  1.38629  1.38629
          0.04784  3.83508  3.68431  1.46634  0.26236  1.09861  0.40547
   1377   2.20715  0.49128  2.26006  1.74984   5893 - -
          1.35912  1.40375  1.40611  1.37696
          0.10826  3.24351  2.75552  0.88710  0.53077  1.00066  0.45829
   1378   0.87264  1.86153  1.86192  1.30436   5900 - -
          1.38629  1.38629  1.38629  1.38629
          0.04613  3.79243  3.79243  1.46634  0.26236  0.51991  0.90281
   1379   1.02555  1.73821  1.68254  1.27416   5901 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1380   0.19991  3.03127  2.55242  2.89960   5902 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1381   0.20118  2.99765  2.56586  2.89178   5903 - -
          1.38629  1.38629  1.38629  1.38629
          0.07610  3.83508  2.96281  1.46634  0.26236  1.09861  0.40547
   1382   0.20958  2.97010  2.53043  2.84475   5904 - -
          1.38629  1.38629  1.38629  1.38629
          0.12301  3.80455  2.37005  1.46634  0.26236  0.60759  0.78672
   1383   1.36107  1.89305  0.82799  1.85743   5905 - -
          1.38629  1.38629  1.38629  1.38629
          0.04816  3.76352  3.73718  1.46634  0.26236  0.38965  1.13101
   1384   1.94660  0.70606  1.73970  1.67088   5906 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83451  3.83451  1.46634  0.26236  1.08113  0.41432
   1385   1.70700  0.80071  1.90051  1.51373   5907 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1386   1.42992  1.47074  1.17661  1.50241   5908 - -
          1.38629  1.38629  1.38629  1.38629
          0.04520  3.83508  3.78993  1.46634  0.26236  1.09861  0.40547
   1387   1.38122  1.81149  0.92246  1.67250   5910 - -
          1.38629  1.38629  1.38629  1.38629
          0.04421  3.83409  3.83409  1.46634  0.26236  1.11389  0.39791
   1388   2.50738  2.06512  2.51884  0.34085   5911 - -
          1.38629  1.38629  1.38629  1.38629
          0.04421  3.83409  3.83409  1.46634  0.26236  1.06874  0.42074
   1389   2.98391  0.19942  3.05607  2.48735   5913 - -
          1.38629  1.38629  1.38629  1.38629
          0.04495  3.83508  3.80053  1.46634  0.26236  1.09861  0.40547
   1390   2.00975  1.69455  1.83251  0.64954   5914 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83432  3.83432  1.46634  0.26236  1.07571  0.41712
   1391   2.15328  0.49694  2.38991  1.69353   5916 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1392   0.20574  3.01293  2.51348  2.88554   5918 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1393   2.63949  3.20844  0.17168  3.08065   5919 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1394   2.73831  2.37598  2.78676  0.24747   5920 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1395   2.36605  1.78681  2.42939  0.42991   5922 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1396   3.01907  0.19350  3.06469  2.52058   5923 - -
          1.38970  1.38970  1.37614  1.38970
          0.04725  3.70710  3.83508  1.31249  0.31355  1.09861  0.40547
   1397   2.37784  3.05997  0.21454  2.92900   5932 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1398   2.68960  3.23487  0.16488  3.10709   5933 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1399   0.19933  3.02854  2.56906  2.88735   5934 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1400   2.70366  2.26792  2.76449  0.26592   5936 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1401   2.37922  1.73361  2.48392  0.43492   5938 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1402   2.66956  3.19718  0.16960  3.08270   5939 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1403   1.64562  1.31533  1.36760  1.25877   5940 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1404   0.44855  2.41417  1.83013  2.19272   5942 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1405   2.22656  2.05240  0.40960  2.30499   5943 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1406   2.01616  1.97738  1.40796  0.72616   5944 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1407   3.00327  0.19689  3.03883  2.51085   5945 - -
          1.38714  1.38714  1.38714  1.38376
          0.04492  3.80184  3.83508  1.42445  0.27528  1.09861  0.40547
   1408   2.72718  2.37689  2.80524  0.24684   5993 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1409   2.69173  3.21384  0.16624  3.09689   5994 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1410   2.33172  0.31718  2.66222  2.25493   5997 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1411   0.19523  3.04731  2.57794  2.91992   5998 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1412   0.19523  3.04731  2.57794  2.91992   5999 - -
          1.38629  1.38629  1.38629  1.38629
          0.04557  3.83508  3.77461  1.46634  0.26236  1.09861  0.40547
   1413   2.95564  0.21465  3.01738  2.38380   6000 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83374  3.83374  1.46634  0.26236  1.05870  0.42603
   1414   2.66057  2.15382  2.72259  0.28989   6001 - -
          1.38694  1.38694  1.38694  1.38437
          0.04474  3.80971  3.83508  1.43423  0.27220  1.09861  0.40547
   1415   3.04741  0.18754  3.11122  2.53858   6004 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1416   2.69891  3.23970  0.16366  3.11187   6005 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1417   0.74136  1.45298  1.95230  1.91246   6007 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1418   2.30140  0.45232  1.96908  2.08632   6008 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1419   2.16613  1.75203  2.31539  0.48901   6009 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1420   1.35742  1.37910  1.26123  1.57232   6010 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1421   2.97197  0.20638  3.00862  2.45438   6011 - -
          1.38581  1.38423  1.38757  1.38757
          0.04531  3.78526  3.83508  1.40408  0.28182  1.09861  0.40547
   1422   0.39447  2.59485  1.81780  2.41999   6013 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1423   2.70099  2.26794  2.74891  0.26744   6014 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1424   2.68421  3.23207  0.16559  3.10430   6020 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1425   0.19523  3.04731  2.57794  2.91992   6021 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1426   0.19523  3.04731  2.57794  2.91992   6022 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1427   2.62689  3.16350  0.17643  3.05410   6023 - -
          1.38629  1.38629  1.38629  1.38629
          0.04474  3.83508  3.80957  1.46634  0.26236  1.09861  0.40547
   1428   2.08337  1.52842  1.92668  0.66752   6025 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.10719  0.40120
   1429   2.07777  0.88436  2.22054  1.04055   6026 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.10719  0.40120
   1430   2.69802  3.23850  0.16386  3.11058   6027 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.10719  0.40120
   1431   2.69802  3.23850  0.16386  3.11058   6028 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.10719  0.40120
   1432   0.19657  3.04267  2.56972  2.91523   6030 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.10719  0.40120
   1433   0.39767  2.59379  1.80290  2.42406   6031 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83453  3.83453  1.46634  0.26236  1.08167  0.41404
   1434   2.75286  2.35893  2.81280  0.24629   6032 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1435   2.77571  0.28253  2.84375  2.07452   6033 - -
          1.38970  1.38970  1.37614  1.38970
          0.04725  3.70710  3.83508  1.31249  0.31355  1.09861  0.40547
   1436   2.49144  3.12626  0.19432  2.99713   6035 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1437   2.98802  0.20046  3.02053  2.49514   6036 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1438   2.75404  2.37705  2.80648  0.24451   6037 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1439   0.19523  3.04731  2.57794  2.91992   6038 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1440   2.66412  3.21524  0.16875  3.09056   6039 - -
          1.38970  1.38970  1.37614  1.38970
          0.04725  3.70710  3.83508  1.31249  0.31355  1.09861  0.40547
   1441   2.76372  2.38461  2.82350  0.24154   6041 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1442   0.19523  3.04731  2.57794  2.91992   6042 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1443   0.19523  3.04731  2.57794  2.91992   6043 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1444   2.74348  2.33712  2.80358  0.25044   6044 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1445   2.85301  0.23240  2.84256  2.39222   6047 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1446   2.63252  3.08334  0.18249  3.01373   6048 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1447   2.49611  0.41067  2.50706  1.75516   6053 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1448   1.37513  2.28631  0.62528  2.20324   6054 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1449   1.67234  2.23169  0.55851  2.01904   6056 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1450   0.30158  2.77612  2.06475  2.64193   6057 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1451   2.66445  2.36206  2.76514  0.25726   6059 - -
          1.39004  1.37943  1.39004  1.38569
          0.04756  3.69508  3.83508  1.29901  0.31856  1.09861  0.40547
   1452   2.99219  0.19423  3.07955  2.52109   6063 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1453   0.19523  3.04731  2.57794  2.91992   6064 - -
          1.38629  1.38629  1.38629  1.38629
          0.04505  3.83508  3.79633  1.46634  0.26236  1.09861  0.40547
   1454   2.67620  3.17302  0.17142  3.06112   6065 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83423  3.83423  1.46634  0.26236  1.07295  0.41855
   1455   1.93365  0.44410  2.40025  2.09328   6066 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1456   0.46679  2.02320  2.16868  2.06809   6067 - -
          1.04491  1.56508  1.54819  1.48468
          0.24314  1.64261  3.80016  0.21612  1.63804  1.09861  0.40547
   1457   2.28523  1.60893  2.39650  0.49904   6072 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83432  3.83432  1.46634  0.26236  1.07547  0.41724
   1458   2.12067  2.90389  0.27124  2.76777   6074 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1459   2.01498  0.66225  2.12961  1.46058   6075 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1460   2.20798  0.69755  2.21588  1.26155   6076 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1461   1.91723  2.62007  0.35460  2.54164   6078 - -
          1.38629  1.38629  1.38629  1.38629
          0.04416  3.83508  3.83508  1.46634  0.26236  1.09861  0.40547
   1462   2.90976  0.22077  2.90832  2.41860   6079 - -
          1.38629  1.38629  1.38629  1.38629
          0.04500  3.83508  3.79865  1.46634  0.26236  1.09861  0.40547
   1463   2.58510  2.98963  0.19604  2.95031   6080 - -
          1.38629  1.38629  1.38629  1.38629
          0.04496  3.83428  3.80109  1.46634  0.26236  1.07447  0.41776
   1464   2.69774  3.23814  0.16392  3.11019   6081 - -
          1.38784  1.38784  1.38167  1.38784
          0.04559  3.77431  3.83435  1.39170  0.28589  1.10980  0.39992
   1465   2.75923  2.37629  2.81910  0.24321   6083 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1466   2.69774  3.23814  0.16392  3.11019   6085 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1467   0.20019  3.02381  2.55995  2.89143   6086 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1468   0.19739  3.03754  2.57310  2.90259   6087 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1469   2.75606  2.38055  2.81597  0.24320   6088 - -
          1.38629  1.38629  1.38629  1.38629
          0.04484  3.83435  3.80624  1.46634  0.26236  1.10980  0.39992
   1470   0.29814  2.69289  2.22456  2.50103   6089 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83374  3.83374  1.46634  0.26236  1.09104  0.40927
   1471   2.93756  0.21153  3.02332  2.41887   6090 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1472   2.69774  3.23814  0.16392  3.11019   6092 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1473   2.74700  2.35688  2.80249  0.24781   6093 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1474   2.68302  2.32371  2.76117  0.26069   6094 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1475   3.04018  0.18946  3.10409  2.52697   6096 - -
          1.38629  1.38629  1.38629  1.38629
          0.04419  3.83435  3.83435  1.46634  0.26236  1.10980  0.39992
   1476   2.21335  0.43804  2.46190  1.83200   6097 - -
          1.38629  1.38629  1.38629  1.38629
          0.04515  3.83435  3.79284  1.46634  0.26236  1.10980  0.39992
   1477   2.99716  0.20204  3.06159  2.45117   6098 - -
          1.38703  1.38703  1.38408  1.38703
          0.04490  3.80428  3.83344  1.42952  0.27368  1.12368  0.39316
   1478   2.61716  3.19428  0.17508  3.06614   6100 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1479   2.61845  3.19203  0.17520  3.06379   6101 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1480   2.65665  3.20046  0.17075  3.07829   6102 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1481   2.31035  0.54768  2.30354  1.50246   6103 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1482   2.87888  0.23176  2.94265  2.32343   6104 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1483   2.75733  2.38090  2.81725  0.24296   6105 - -
          1.38629  1.38629  1.38629  1.38629
          0.04470  3.83344  3.81297  1.46634  0.26236  1.12368  0.39316
   1484   2.75977  2.38198  2.81968  0.24245   6107 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83299  3.83299  1.46634  0.26236  1.10991  0.39986
   1485   2.69628  3.23617  0.16424  3.10806   6108 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1486   2.74536  2.34662  2.80548  0.24897   6109 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1487   0.19587  3.04402  2.57564  2.91638   6110 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1488   3.04361  0.18824  3.10754  2.53562   6112 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1489   0.29224  2.70902  2.40855  2.33448   6113 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1490   3.02885  0.19074  3.09297  2.52681   6114 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1491   0.20326  2.99939  2.54641  2.88681   6115 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1492   2.97596  0.19653  3.06862  2.51408   6116 - -
          1.38629  1.38629  1.38629  1.38629
          0.04475  3.83344  3.81096  1.46634  0.26236  1.12368  0.39316
   1493   2.99090  0.20383  3.05543  2.44119   6117 - -
          1.38806  1.38103  1.38806  1.38806
          0.04585  3.76477  3.83295  1.38193  0.28914  1.10856  0.40053
   1494   2.67386  3.19362  0.17207  3.03500   6119 - -
          1.38761  1.38545  1.38452  1.38761
          0.04542  3.78221  3.83344  1.40238  0.28238  1.12368  0.39316
   1495   3.02256  0.19226  3.08674  2.51846   6122 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1496   3.01558  0.19302  3.07987  2.51886   6123 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1497   3.03832  0.18913  3.10232  2.53247   6124 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1498   2.67655  3.21967  0.16748  3.09136   6125 - -
          1.38783  1.38783  1.38783  1.38170
          0.04563  3.77377  3.83344  1.39216  0.28574  1.12368  0.39316
   1499   2.74357  2.37504  2.81110  0.24525   6127 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1500   3.03896  0.18903  3.10294  2.53285   6128 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1501   0.20237  3.01570  2.56254  2.86311   6129 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1502   1.95111  0.49486  2.33486  1.88782   6133 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1503   0.42439  2.56640  1.70800  2.43281   6134 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1504   2.58906  0.37508  2.66006  1.78539   6137 - -
          1.38629  1.38629  1.38629  1.38629
          0.04561  3.83344  3.77429  1.46634  0.26236  1.12368  0.39316
   1505   3.01115  0.19748  3.07546  2.47933   6138 - -
          1.38629  1.38629  1.38629  1.38629
          0.04429  3.83212  3.83212  1.46634  0.26236  1.08414  0.41278
   1506   0.20441  2.97385  2.55841  2.87644   6140 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1507   2.23880  1.24971  2.31989  0.67621   6141 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1508   2.53679  2.75531  0.22854  2.78720   6144 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1509   0.98924  2.08100  0.98783  2.03293   6146 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1510   1.46296  2.51139  0.52318  2.35745   6147 - -
          1.38629  1.38629  1.38629  1.38629
          0.04463  3.83344  3.81611  1.46634  0.26236  1.12368  0.39316
   1511   0.19712  3.03980  2.56779  2.91214   6148 - -
          1.38022  1.38833  1.38833  1.38833
          0.04610  3.75478  3.83306  1.36992  0.29320  1.12934  0.39045
   1512   2.62885  3.20010  0.17346  3.07195   6151 - -
          1.38474  1.38785  1.38474  1.38785
          0.04634  3.74494  3.83306  1.36984  0.29323  1.12934  0.39045
   1513   2.47513  1.89697  2.56093  0.37310   6155 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83306  3.83306  1.46634  0.26236  1.12934  0.39045
   1514   1.97816  1.44062  1.73926  0.80018   6156 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83306  3.83306  1.46634  0.26236  1.12934  0.39045
   1515   1.99049  2.22835  0.58365  1.62045   6157 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83306  3.83306  1.46634  0.26236  1.12934  0.39045
   1516   1.86606  2.44906  0.44710  2.12516   6158 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83306  3.83306  1.46634  0.26236  1.11201  0.39883
   1517   1.72527  1.48477  1.76617  0.85723   6159 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.12368  0.39316
   1518   1.05779  1.83421  1.74131  1.14649   6160 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83344  3.83344  1.46634  0.26236  1.09048  0.40956
   1519   0.99960  1.73397  1.49304  1.46663   6161 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1520   1.88126  0.80360  2.00940  1.32493   6162 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1521   0.39748  2.56521  1.85676  2.35486   6164 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1522   2.68228  0.25296  2.85367  2.32832   6165 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1523   2.63859  0.27025  2.79855  2.25906   6166 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1524   1.69611  0.83371  2.04627  1.37454   6169 - -
          1.38629  1.38629  1.38629  1.38629
          0.04487  3.83417  3.80501  1.46634  0.26236  1.11264  0.39852
   1525   1.91176  2.26858  0.52864  1.83688   6170 - -
          1.38629  1.38629  1.38629  1.38629
          0.04423  3.83353  3.83353  1.46634  0.26236  1.09316  0.40820
   1526   0.20329  3.01203  2.56118  2.85510   6171 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1527   0.21714  2.89273  2.52773  2.81479   6178 - -
          1.38629  1.38629  1.38629  1.38629
          0.04420  3.83417  3.83417  1.46634  0.26236  1.11264  0.39852
   1528   2.33790  3.00463  0.22614  2.87697   6179 - -
          1.38629  1.38629  1.38629  1.38629
          0.04673  3.83417  3.72826  1.46634  0.26236  1.11264  0.39852
   1529   1.80045  1.24641  1.73744  0.99082   6180 - -
          1.38629  1.38629  1.38629  1.38629
          0.04502  3.83175  3.80077  1.46634  0.26236  1.07309  0.41848
   1530   1.79393  0.64807  2.01059  1.73312   6182 - -
          1.38629  1.38629  1.38629  1.38629
          0.04426  3.83277  3.83277  1.46634  0.26236  1.10269  0.40343
   1531   1.95780  2.20019  0.44198  2.25110   6183 - -
          1.38629  1.38629  1.38629  1.38629
          0.04458  3.83345  3.81818  1.46634  0.26236  1.12349  0.39326
   1532   1.90068  1.95488  0.60249  1.82322   6184 - -
          1.38778  1.38184  1.38778  1.38778
          0.04750  3.77526  3.75248  1.39434  0.28501  1.11320  0.39825
   1533   2.13642  1.94605  2.09310  0.48486   6186 - -
          1.38629  1.38629  1.38629  1.38629
          0.05007  3.83163  3.60592  1.46634  0.26236  1.15043  0.38053
   1534   1.41161  2.15400  0.70532  1.92223   6187 - -
          1.38804  1.39215  1.37524  1.38983
          0.06078  3.49687  3.55153  1.10537  0.40210  1.19654  0.35988
   1535   1.15240  1.75522  1.18523  1.58194   6189 - -
          1.38629  1.38629  1.38629  1.38629
          0.04766  3.81991  3.70455  1.46634  0.26236  1.18454  0.36512
   1536   1.69091  1.19130  1.17081  1.60094   6190 - -
          1.38629  1.38629  1.38629  1.38629
          0.04685  3.82010  3.73642  1.46634  0.26236  1.27427  0.32800
   1537   2.01479  0.69139  1.76765  1.63457   6191 - -
          1.38768  1.38216  1.38768  1.38768
          0.06134  3.76504  3.31509  1.39921  0.28341  1.32027  0.31070
   1538   2.28908  1.63179  2.32110  0.50270   6194 - -
          1.38629  1.38629  1.38629  1.38629
          0.04650  3.80439  3.76532  1.46634  0.26236  1.46892  0.26159
   1539   0.22358  2.91486  2.46168  2.79935   6195 - -
          1.38629  1.38629  1.38629  1.38629
          0.08175  3.80379  2.87860  1.46634  0.26236  1.48764  0.25606
   1540   0.23797  2.82959  2.45201  2.70885   6196 - -
          1.38684  1.38465  1.38684  1.38684
          0.05008  3.74752  3.67816  1.43877  0.27079  1.78321  0.18404
   1541   2.86037  0.22562  2.92721  2.39485   6198 - -
          1.38629  1.38629  1.38629  1.38629
          0.06621  3.76707  3.19541  1.46634  0.26236  1.70037  0.20165
   1542   2.65024  0.29731  2.69437  2.12892   6199 - -
          1.43642  1.32018  1.36512  1.42801
          0.32399  1.37466  3.73732  1.52198  0.24626  0.39223  1.12563
   1543   1.67442  1.68667  1.07660  1.24933   6242 - -
          1.38629  1.38629  1.38629  1.38629
          0.04516  3.83093  3.79570  1.46634  0.26236  1.14643  0.38239
   1544   1.48605  1.43436  1.93259  0.93983   6243 - -
          1.38629  1.38629  1.38629  1.38629
          0.04437  3.83046  3.83046  1.46634  0.26236  1.14756  0.38186
   1545   1.08517  1.62707  1.90180  1.15090   6244 - -
          1.38629  1.38629  1.38629  1.38629
          0.07684  3.83090  2.95134  1.46634  0.26236  1.16111  0.37562
   1546   0.82930  1.99164  1.38059  1.73872   6245 - -
          1.24082  1.51420  1.25840  1.57621
          0.33284  1.53546  2.69184  1.69907  0.20194  1.50944  0.24979
   1547   2.28770  2.82721  0.26041  2.67968   6328 - -
          1.38629  1.38629  1.38629  1.38629
          0.05054  3.75380  3.65506  1.46634  0.26236  1.38376  0.28853
   1548   2.53669  3.04366  0.20026  2.90596   6329 - -
          1.38629  1.38629  1.38629  1.38629
          0.05023  3.76670  3.65516  1.46634  0.26236  0.91753  0.51000
   1549   0.60636  2.22253  1.61140  1.91919   6330 - -
          1.37909  1.38871  1.38871  1.38871
          0.04822  3.70411  3.79639  1.35345  0.29887  1.25623  0.33509
   1550   1.91083  2.60797  0.36487  2.47606   6332 - -
          1.38629  1.38629  1.38629  1.38629
          0.04704  3.80432  3.74338  1.46634  0.26236  0.95551  0.48551
   1551   2.02037  1.93401  0.50185  2.14203   6333 - -
          1.38629  1.38629  1.38629  1.38629
          0.04493  3.81827  3.81827  1.46634  0.26236  1.19057  0.36248
   1552   1.68228  1.23060  1.16194  1.56516   6334 - -
          1.38629  1.38629  1.38629  1.38629
          0.04643  3.82149  3.75174  1.46634  0.26236  1.10266  0.40345
   1553   0.71157  1.71040  1.85782  1.75841   6335 - -
          1.37193  1.39268  1.38803  1.39268
          0.05052  3.59610  3.82436  1.20458  0.35642  1.02954  0.44187
   1554   1.99246  2.57824  0.36445  2.37350   6339 - -
          1.38718  1.38364  1.38718  1.38718
          0.04521  3.79490  3.82976  1.42245  0.27592  1.12624  0.39193
   1555   1.87566  0.69155  1.79755  1.71346   6341 - -
          1.38629  1.38629  1.38629  1.38629
          0.04435  3.83090  3.83090  1.46634  0.26236  1.16111  0.37562
   1556   2.01230  0.84653  1.89620  1.24729   6342 - -
          1.38629  1.38629  1.38629  1.38629
          0.04466  3.83090  3.81726  1.46634  0.26236  1.16111  0.37562
   1557   1.90862  2.16461  0.56444  1.78236   6343 - -
          1.38629  1.38629  1.38629  1.38629
          0.04502  3.83060  3.80221  1.46634  0.26236  1.16540  0.37367
   1558   1.44716  1.27078  1.86001  1.11329   6345 - -
          1.38629  1.38629  1.38629  1.38629
          0.04439  3.82997  3.82997  1.46634  0.26236  1.13269  0.38885
   1559   2.85851  0.24538  2.92507  2.23888   6346 - -
          1.38629  1.38629  1.38629  1.38629
          0.04435  3.83090  3.83090  1.46634  0.26236  1.16111  0.37562
   1560   1.82843  1.29428  1.32866  1.20262   6347 - -
          1.38722  1.38722  1.38351  1.38722
          0.04519  3.79440  3.83090  1.42043  0.27656  1.16111  0.37562
   1561   0.19777  3.03610  2.56604  2.90809   6350 - -
          1.38629  1.38629  1.38629  1.38629
          0.04435  3.83090  3.83090  1.46634  0.26236  1.16111  0.37562
   1562   0.84341  1.39574  1.82364  1.82837   6351 - -
          1.38629  1.38629  1.38629  1.38629
          0.04724  3.83090  3.71096  1.46634  0.26236  1.16111  0.37562
   1563   2.48152  2.94251  0.22736  2.70283   6352 - -
          1.38629  1.38629  1.38629  1.38629
          0.04784  3.82813  3.69021  1.46634  0.26236  1.09605  0.40675
   1564   2.57036  3.01878  0.20850  2.76730   6353 - -
          1.38629  1.38629  1.38629  1.38629
          0.04491  3.82730  3.81017  1.46634  0.26236  1.07372  0.41815
   1565   2.10018  1.76340  2.24816  0.50997   6362 - -
          1.38629  1.38629  1.38629  1.38629
          0.04438  3.83014  3.83014  1.46634  0.26236  1.15485  0.37849
   1566   1.47226  2.29044  0.58101  2.20692   6363 - -
          1.38629  1.38629  1.38629  1.38629
          0.04437  3.83051  3.83051  1.46634  0.26236  1.16661  0.37312
   1567   1.81821  2.22347  0.58046  1.77308   6364 - -
          1.38685  1.38685  1.38464  1.38685
          0.04597  3.80861  3.78303  1.43857  0.27085  1.16661  0.37312
   1568   1.99737  2.76588  0.31550  2.63160   6366 - -
          1.38629  1.38629  1.38629  1.38629
          0.04441  3.82946  3.82946  1.46634  0.26236  1.18164  0.36640
   1569   1.09625  1.91791  1.09117  1.69750   6367 - -
          1.38629  1.38629  1.38629  1.38629
          0.04441  3.82946  3.82946  1.46634  0.26236  1.18164  0.36640
   1570   2.01707  1.16175  1.95198  0.88667   6368 - -
          1.38629  1.38629  1.38629  1.38629
          0.04507  3.82946  3.80110  1.46634  0.26236  1.18164  0.36640
   1571   1.54034  1.24812  1.96585  1.02552   6370 - -
          1.38629  1.38629  1.38629  1.38629
          0.04634  3.82883  3.74865  1.46634  0.26236  1.14022  0.38529
   1572   1.28177  1.75453  0.92715  1.87218   6371 - -
          1.38629  1.38629  1.38629  1.38629
          0.04447  3.82814  3.82814  1.46634  0.26236  1.20011  0.35834
   1573   0.95755  2.32949  0.90713  2.16161   6372 - -
          1.38629  1.38629  1.38629  1.38629
          0.04704  3.82814  3.72124  1.46634  0.26236  1.20011  0.35834
   1574   2.30055  1.41293  2.37207  0.57433   6373 - -
          1.38629  1.38629  1.38629  1.38629
          0.04459  3.82568  3.82568  1.46634  0.26236  1.16209  0.37518
   1575   2.21300  2.88995  0.26214  2.72345   6374 - -
          1.38629  1.38629  1.38629  1.38629
          0.04687  3.82729  3.72887  1.46634  0.26236  1.21172  0.35337
   1576   0.20811  2.98088  2.53945  2.84338   6377 - -
          1.38629  1.38629  1.38629  1.38629
          0.04628  3.82504  3.75463  1.46634  0.26236  1.18134  0.36654
   1577   2.07844  1.02376  2.06406  0.94496   6378 - -
          1.38629  1.38629  1.38629  1.38629
          0.04885  3.82481  3.65537  1.46634  0.26236  1.24503  0.33958
   1578   2.46122  2.22411  2.41977  0.33189   6379 - -
          1.38629  1.38629  1.38629  1.38629
          0.04579  3.82078  3.77887  1.46634  0.26236  1.15659  0.37769
   1579   2.36191  3.00111  0.22488  2.85749   6380 - -
          1.38629  1.38629  1.38629  1.38629
          0.04868  3.82313  3.66298  1.46634  0.26236  1.26693  0.33086
   1580   2.66145  3.19144  0.17225  3.05184   6381 - -
          1.38629  1.38629  1.38629  1.38629
          0.04546  3.81933  3.79423  1.46634  0.26236  1.29609  0.31965
   1581   2.57676  3.08559  0.19403  2.90697   6382 - -
          1.38629  1.38629  1.38629  1.38629
          0.04591  3.81918  3.77549  1.46634  0.26236  1.31648  0.31208
   1582   1.89731  2.70092  0.34721  2.57407   6383 - -
          1.38629  1.38629  1.38629  1.38629
          0.09236  3.81820  2.71417  1.46634  0.26236  1.28835  0.32258
   1583   2.25103  1.61896  2.30433  0.51621   6385 - -
          1.38629  1.38629  1.38629  1.38629
          0.05173  3.77384  3.59539  1.46634  0.26236  0.95662  0.48481
   1584   1.95595  2.32619  0.49725  1.87929   6386 - -
          1.38629  1.38629  1.38629  1.38629
          0.04872  3.79685  3.68444  1.46634  0.26236  1.49423  0.25415
   1585   0.21567  2.94725  2.51058  2.80850   6388 - -
          1.38629  1.38629  1.38629  1.38629
          0.04895  3.79560  3.67704  1.46634  0.26236  1.49013  0.25533
   1586   0.22358  2.89063  2.48852  2.78419   6389 - -
          1.38629  1.38629  1.38629  1.38629
          0.04646  3.79456  3.77649  1.46634  0.26236  1.45804  0.26487
   1587   2.56537  3.07927  0.19222  2.95669   6391 - -
          1.38716  1.38716  1.38371  1.38716
          0.04673  3.76299  3.79698  1.42352  0.27557  1.53602  0.24237
   1588   2.55357  2.28239  2.63889  0.28939   6393 - -
          1.38629  1.38629  1.38629  1.38629
          0.04641  3.79739  3.77580  1.46634  0.26236  1.55023  0.23851
   1589   2.80359  0.23791  2.85866  2.36672   6394 - -
          1.38629  1.38629  1.38629  1.38629
          0.04592  3.79690  3.79690  1.46634  0.26236  0.59782  0.79853
   1590   2.67930  3.18330  0.16992  3.07453   6395 - -
          1.38629  1.38629  1.38629  1.38629
          0.04429  3.83226  3.83226  1.46634  0.26236  1.14117  0.38485
   1591   2.69374  2.35410  2.75704  0.25629   6396 - -
          1.38629  1.38629  1.38629  1.38629
          0.04429  3.83226  3.83226  1.46634  0.26236  1.10634  0.40162
   1592   0.19771  3.03577  2.57164  2.90140   6398 - -
          1.38629  1.38629  1.38629  1.38629
          0.04425  3.83303  3.83303  1.46634  0.26236  1.09072  0.40944
   1593   0.19762  3.03616  2.56731  2.90846   6399 - -
          1.38629  1.38629  1.38629  1.38629
          0.04421  3.83389  3.83389  1.46634  0.26236  1.11683  0.39648
   1594   2.96936  0.19802  3.05578  2.51054   6400 - -
          1.38936  1.37987  1.38661  1.38936
          0.04758  3.71793  3.80833  1.32613  0.30857  1.11683  0.39648
   1595   0.20173  3.00733  2.55337  2.89243   6402 - -
          1.38629  1.38629  1.38629  1.38629
          0.04424  3.83333  3.83333  1.46634  0.26236  1.12527  0.39240
   1596   0.20221  3.01303  2.56018  2.87099   6403 - -
          1.38701  1.38701  1.38701  1.38414
          0.04573  3.80501  3.79684  1.43055  0.27335  1.12527  0.39240
   1597   2.68185  3.19280  0.16924  3.07470   6405 - -
          1.38629  1.38629  1.38629  1.38629
          0.08074  3.83253  2.88406  1.46634  0.26236  1.13726  0.38669
   1598   2.62096  3.10646  0.18359  2.99111   6406 - -
          1.38629  1.38629  1.38629  1.38629
          0.04974  3.79767  3.64585  1.46634  0.26236  1.54755  0.23923
   1599   2.64275  2.30749  2.71805  0.27008   6407 - -
          1.38629  1.38629  1.38629  1.38629
          0.04719  3.79399  3.74696  1.46634  0.26236  1.58184  0.23016
   1600   0.22232  2.90614  2.49891  2.77296   6408 - -
          1.38629  1.38629  1.38629  1.38629
          0.04800  3.79291  3.71570  1.46634  0.26236  1.56613  0.23427
   1601   1.58300  2.17373  0.63093  1.90521   6409 - -
          1.42968  1.42041  1.27434  1.42968
          0.09325  2.77148  3.63191  0.61115  0.78247  1.52550  0.24528
   1602   2.76616  0.24357  2.81933  2.36843   6411 - -
          1.38629  1.38629  1.38629  1.38629
          0.04880  3.78958  3.68802  1.46634  0.26236  1.54100  0.24101
   1603   2.73097  0.26171  2.81045  2.25444   6412 - -
          1.38629  1.38629  1.38629  1.38629
          0.04629  3.78905  3.78905  1.46634  0.26236  1.15593  0.37799
   1604   2.35636  2.39746  0.30995  2.51575   6413 - -
          1.38629  1.38629  1.38629  1.38629
          0.04854  3.80253  3.68611  1.46634  0.26236  1.43760  0.27115
   1605   2.66728  2.31619  2.73535  0.26522   6414 - -
          1.38629  1.38629  1.38629  1.38629
          0.04572  3.80122  3.80122  1.46634  0.26236  1.46627  0.26239
   1606   0.22859  2.89819  2.44857  2.76771   6416 - -
          1.38629  1.38629  1.38629  1.38629
          0.04567  3.80229  3.80229  1.46634  0.26236  1.48517  0.25678
   1607   1.80367  1.29353  1.26278  1.27963   6417 - -
          1.38629  1.38629  1.38629  1.38629
          0.04884  3.80269  3.67493  1.46634  0.26236  1.49871  0.25285
   1608   1.83886  1.06504  1.11267  1.78613   6418 - -
          1.38629  1.38629  1.38629  1.38629
          0.07595  3.79964  2.98059  1.46634  0.26236  1.34332  0.30243
   1609   2.04101  2.59806  0.35025  2.39501   6419 - -
          1.38629  1.38629  1.38629  1.38629
          0.04926  3.77553  3.68319  1.46634  0.26236  0.65483  0.73299
   1610   2.53585  2.92343  0.21721  2.77581   6420 - -
          1.38629  1.38629  1.38629  1.38629
          0.04498  3.81712  3.81712  1.46634  0.26236  1.21075  0.35378
   1611   0.23576  2.78952  2.47714  2.73960   6421 - -
          1.38629  1.38629  1.38629  1.38629
          0.04737  3.82018  3.71556  1.46634  0.26236  1.30420  0.31662
   1612   0.22157  2.91974  2.50837  2.75846   6422 - -
          1.37883  1.38880  1.38880  1.38880
          0.05694  3.72229  3.46835  1.34974  0.30017  1.22907  0.34611
   1613   1.83745  1.18255  1.01347  1.76421   6424 - -
          1.38629  1.38629  1.38629  1.38629
          0.06954  3.81097  3.09997  1.46634  0.26236  1.17743  0.36827
   1614   1.88224  1.26325  0.89992  1.84254   6425 - -
          1.38629  1.38629  1.38629  1.38629
          0.04998  3.79374  3.64062  1.46634  0.26236  1.53292  0.24322
   1615   2.54591  2.27628  2.61874  0.29298   6426 - -
          1.38718  1.38363  1.38718  1.38718
          0.04781  3.75627  3.75874  1.42237  0.27594  1.50865  0.25001
   1616   2.56494  3.05088  0.19792  2.89455   6428 - -
          1.38629  1.38629  1.38629  1.38629
          0.05563  3.79278  3.45528  1.46634  0.26236  1.54532  0.23984
   1617   2.28326  0.44042  2.18579  1.95268   6429 - -
          1.38629  1.38629  1.38629  1.38629
          0.04920  3.78480  3.67710  1.46634  0.26236  1.66210  0.21040
   1618   2.48237  2.84713  0.22961  2.75518   6430 - -
          1.38758  1.38758  1.38245  1.38758
          0.05131  3.73201  3.64676  1.40362  0.28197  1.55921  0.23611
   1619   2.42569  2.78188  0.24858  2.66274   6432 - -
          1.38629  1.38629  1.38629  1.38629
          0.04813  3.78192  3.72092  1.46634  0.26236  1.55153  0.23816
   1620   1.95844  0.52969  2.20749  1.83160   6433 - -
          1.38629  1.38629  1.38629  1.38629
          0.04733  3.78376  3.75131  1.46634  0.26236  1.60972  0.22307
   1621   2.52817  2.24845  2.52724  0.30822   6434 - -
          1.38629  1.38629  1.38629  1.38629
          0.04651  3.78444  3.78444  1.46634  0.26236  1.44536  0.26874
   1622   2.54359  2.93555  0.21340  2.80545   6435 - -
          1.38629  1.38629  1.38629  1.38629
          0.04624  3.79001  3.79001  1.46634  0.26236  0.54569  0.86618
   1623   2.57197  3.00451  0.19761  2.93070   6436 - -
          1.38629  1.38629  1.38629  1.38629
          0.04428  3.83249  3.83249  1.46634  0.26236  1.10126  0.40414
   1624   0.23857  2.83211  2.45258  2.69882   6437 - -
          1.38629  1.38629  1.38629  1.38629
          0.04424  3.83330  3.83330  1.46634  0.26236  1.10288  0.40334
   1625   2.30866  2.22739  2.53738  0.33726   6438 - -
          1.38629  1.38629  1.38629  1.38629
          0.04422  3.83380  3.83380  1.46634  0.26236  1.11823  0.39580
   1626   2.80022  0.24402  2.89051  2.30076   6439 - -
          1.38629  1.38629  1.38629  1.38629
          0.04429  3.83226  3.83226  1.46634  0.26236  1.06049  0.42509
   1627   0.23296  2.81982  2.49576  2.72171   6440 - -
          1.38629  1.38629  1.38629  1.38629
          0.04438  3.83025  3.83025  1.46634  0.26236  1.09861  0.40547
   1628   2.95198  0.20812  3.03071  2.43760   6441 - -
          1.38629  1.38629  1.38629  1.38629
          0.04448  3.82811  3.82811  1.46634  0.26236  1.09861  0.40547
   1629   2.95781  0.20804  3.02342  2.43892   6442 - -
          1.38629  1.38629  1.38629  1.38629
          0.04478  3.82150  3.82150  1.46634  0.26236  1.09861  0.40547
   1630   2.66180  2.27635  2.72384  0.27194   6443 - -
          1.38629  1.38629  1.38629  1.38629
          0.04494  3.81804  3.81804  1.46634  0.26236  1.09861  0.40547
   1631   2.92794  0.21524  3.00408  2.40173   6444 - -
          1.38629  1.38629  1.38629  1.38629
          0.04515  3.81342  3.81342  1.46634  0.26236  1.09861  0.40547
   1632   2.82805  0.22662  2.92979  2.40530   6445 - -
          1.38629  1.38629  1.38629  1.38629
          0.04624  3.79006  3.79006  1.46634  0.26236  1.09861  0.40547
   1633   2.58828  2.24900  2.64321  0.29007   6446 - -
          1.38629  1.38629  1.38629  1.38629
          0.04665  3.78147  3.78147  1.46634  0.26236  1.09861  0.40547
   1634   2.46312  2.22662  2.56715  0.31446   6447 - -
          1.38629  1.38629  1.38629  1.38629
          0.05450  3.62990  3.62990  1.46634  0.26236  1.09861  0.40547
   1635   1.69302  1.88443  1.99454  0.63857   6448 - -
          1.38629  1.38629  1.38629  1.38629
          0.06302  3.48879  3.48879  1.46634  0.26236  1.09861  0.40547
   1636   1.68578  0.78109  1.90179  1.57267   6449 - -
          1.38629  1.38629  1.38629  1.38629
          0.06470  3.46334  3.46334  1.46634  0.26236  1.09861  0.40547
   1637   1.84301  1.71744  1.85352  0.68231   6450 - -
          1.38629  1.38629  1.38629  1.38629
          0.08426  3.20880  3.20880  1.46634  0.26236  1.09861  0.40547
   1638   1.16047  1.59213  1.31608  1.53719   6451 - -
          1.38629  1.38629  1.38629  1.38629
          0.08737  3.17407  3.17407  1.46634  0.26236  1.09861  0.40547
   1639   1.25124  1.55578  1.34720  1.41528   6452 - -
          1.38629  1.38629  1.38629  1.38629
          0.08762  3.17141  3.17141  1.46634  0.26236  1.09861  0.40547
   1640   1.38496  1.48670  1.28596  1.39771   6453 - -
          1.38629  1.38629  1.38629  1.38629
          0.08826  3.16445  3.16445  1.46634  0.26236  1.09861  0.40547
   1641   1.35706  1.55278  1.20626  1.46269   6454 - -
          1.38629  1.38629  1.38629  1.38629
          0.08841  3.16283  3.16283  1.46634  0.26236  1.09861  0.40547
   1642   1.22549  1.58953  1.30621  1.46309   6455 - -
          1.38629  1.38629  1.38629  1.38629
          0.08887  3.15789  3.15789  1.46634  0.26236  1.09861  0.40547
   1643   1.27836  1.61958  1.20444  1.49760   6456 - -
          1.38629  1.38629  1.38629  1.38629
          0.08915  3.15485  3.15485  1.46634  0.26236  1.09861  0.40547
   1644   1.36354  1.35698  1.44884  1.37846   6457 - -
          1.38629  1.38629  1.38629  1.38629
          0.08915  3.15485  3.15485  1.46634  0.26236  1.09861  0.40547
   1645   1.19102  1.52583  1.39888  1.46199   6458 - -
          1.38629  1.38629  1.38629  1.38629
          0.08940  3.15219  3.15219  1.46634  0.26236  1.09861  0.40547
   1646   1.41155  1.43953  1.25302  1.45434   6459 - -
          1.38629  1.38629  1.38629  1.38629
          0.08981  3.14775  3.14775  1.46634  0.26236  1.09861  0.40547
   1647   1.27603  1.55148  1.25050  1.50256   6460 - -
          1.38629  1.38629  1.38629  1.38629
          0.08981  3.14775  3.14775  1.46634  0.26236  1.09861  0.40547
   1648   1.38541  1.40384  1.38992  1.36637   6461 - -
          1.38629  1.38629  1.38629  1.38629
          0.08981  3.14775  3.14775  1.46634  0.26236  1.09861  0.40547
   1649   1.30323  1.55291  1.30144  1.40823   6462 - -
          1.38629  1.38629  1.38629  1.38629
          0.08981  3.14775  3.14775  1.46634  0.26236  1.09861  0.40547
   1650   1.26037  1.58288  1.28236  1.45378   6463 - -
          1.38629  1.38629  1.38629  1.38629
          0.09047  3.14081  3.14081  1.46634  0.26236  1.09861  0.40547
   1651   1.26005  1.52641  1.29986  1.48511   6464 - -
          1.38629  1.38629  1.38629  1.38629
          0.09047  3.14081  3.14081  1.46634  0.26236  1.09861  0.40547
   1652   1.41260  1.38313  1.37217  1.37777   6465 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1653   1.32709  1.50694  1.26632  1.46405   6466 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1654   1.25607  1.54824  1.37586  1.38635   6467 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1655   1.43859  1.36838  1.33568  1.40552   6468 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1656   1.40398  1.44893  1.37827  1.31847   6469 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1657   1.35560  1.46246  1.33507  1.39675   6470 - -
          1.38629  1.38629  1.38629  1.38629
          0.09057  3.13974  3.13974  1.46634  0.26236  1.09861  0.40547
   1658   1.45537  1.41579  1.39168  1.28991   6471 - -
          1.38629  1.38629  1.38629  1.38629
          0.09076  3.13774  3.13774  1.46634  0.26236  1.09861  0.40547
   1659   1.22770  1.53449  1.38705  1.42023   6472 - -
          1.38629  1.38629  1.38629  1.38629
          0.09076  3.13774  3.13774  1.46634  0.26236  1.09861  0.40547
   1660   1.39567  1.48061  1.28474  1.39388   6473 - -
          1.38629  1.38629  1.38629  1.38629
          0.09076  3.13774  3.13774  1.46634  0.26236  1.09861  0.40547
   1661   1.42858  1.38236  1.38414  1.35159   6474 - -
          1.38629  1.38629  1.38629  1.38629
          0.09076  3.13774  3.13774  1.46634  0.26236  1.09861  0.40547
   1662   1.43489  1.36016  1.40274  1.34971   6475 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1663   1.28043  1.53156  1.33342  1.41753   6476 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1664   1.25054  1.46873  1.38707  1.45404   6477 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1665   1.38620  1.48025  1.43532  1.25752   6478 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1666   1.29913  1.52453  1.37877  1.35628   6479 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1667   1.33206  1.53951  1.26419  1.43081   6480 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1668   1.39361  1.48432  1.41393  1.26591   6481 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1669   1.41097  1.43252  1.26812  1.44381   6482 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1670   1.31118  1.44039  1.40939  1.38881   6483 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1671   1.41591  1.51600  1.29273  1.33490   6484 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1672   1.34586  1.53040  1.31691  1.36541   6485 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1673   1.36684  1.42148  1.32203  1.43912   6486 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1674   1.19205  1.60238  1.29352  1.51102   6487 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1675   1.44480  1.38215  1.37983  1.34114   6488 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1676   1.36480  1.49634  1.34862  1.34315   6489 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1677   1.26675  1.56152  1.31215  1.43047   6490 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1678   1.38400  1.46347  1.43561  1.27288   6491 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1679   1.33243  1.45282  1.38281  1.38078   6492 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1680   1.31121  1.55834  1.24809  1.45685   6493 - -
          1.38629  1.38629  1.38629  1.38629
          0.09109  3.13426  3.13426  1.46634  0.26236  1.09861  0.40547
   1681   1.31998  1.47878  1.29886  1.46059   6494 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1682   1.34763  1.51721  1.34024  1.35078   6495 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1683   1.45697  1.35270  1.42794  1.31411   6496 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1684   1.36146  1.47862  1.37086  1.33990   6497 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1685   1.40761  1.48347  1.38770  1.27735   6498 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1686   1.39582  1.54097  1.23288  1.39940   6499 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1687   1.36036  1.56004  1.21874  1.43674   6500 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1688   1.39994  1.44432  1.35679  1.34709   6501 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1689   1.41059  1.47274  1.28474  1.38637   6502 - -
          1.38629  1.38629  1.38629  1.38629
          0.09139  3.13112  3.13112  1.46634  0.26236  1.09861  0.40547
   1690   1.40869  1.47595  1.27788  1.39292   6503 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1691   1.27926  1.55228  1.29844  1.43954   6504 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1692   1.24158  1.54002  1.36670  1.41986   6505 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1693   1.35051  1.46053  1.35708  1.38084   6506 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1694   1.46104  1.30440  1.45513  1.33446   6507 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1695   1.34423  1.51853  1.32256  1.37131   6508 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1696   1.43112  1.43867  1.37554  1.30559   6509 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1697   1.37398  1.45795  1.34193  1.37496   6510 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1698   1.38495  1.54566  1.21693  1.42565   6511 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1699   1.34330  1.51310  1.33846  1.36046   6512 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1700   1.46081  1.33644  1.45530  1.30253   6513 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1701   1.28943  1.53452  1.33285  1.40532   6514 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1702   1.34829  1.50572  1.35473  1.34537   6515 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1703   1.29032  1.48100  1.33357  1.45297   6516 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1704   1.37169  1.50334  1.33942  1.33965   6517 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1705   1.43894  1.36081  1.39439  1.35331   6518 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1706   1.36957  1.50646  1.33239  1.34613   6519 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1707   1.38570  1.50282  1.21740  1.46382   6520 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1708   1.46035  1.35282  1.45492  1.28766   6521 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1709   1.34829  1.50572  1.35473  1.34537   6522 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1710   1.43218  1.41709  1.37670  1.32283   6523 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1711   1.42594  1.35646  1.35646  1.40823   6524 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1712   1.40376  1.46224  1.28429  1.40338   6525 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1713   1.43112  1.43867  1.37554  1.30559   6526 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1714   1.40584  1.45479  1.29135  1.40044   6527 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1715   1.42850  1.47551  1.37240  1.27951   6528 - -
          1.38629  1.38629  1.38629  1.38629
          0.09182  3.12665  3.12665  1.46634  0.26236  1.09861  0.40547
   1716   1.35673  1.51030  1.33358  1.35432   6529 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1717   1.44221  1.38709  1.43248  1.29069   6530 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1718   1.40879  1.48207  1.33957  1.32261   6531 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1719   1.28936  1.51194  1.36895  1.38751   6532 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1720   1.32690  1.52421  1.30046  1.40852   6533 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1721   1.24947  1.56072  1.28826  1.48013   6534 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1722   1.43798  1.44692  1.42773  1.24671   6535 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1723   1.33749  1.51869  1.30457  1.39752   6536 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1724   1.36471  1.56325  1.17694  1.48337   6537 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1725   1.32593  1.51825  1.31666  1.39707   6538 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1726   1.41245  1.47710  1.35129  1.31212   6539 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1727   1.33356  1.46042  1.32004  1.43885   6540 - -
          1.38629  1.38629  1.38629  1.38629
          0.09245  3.12014  3.12014  1.46634  0.26236  1.09861  0.40547
   1728   1.35230  1.43727  1.39433  1.36344   6541 - -
          1.38629  1.38629  1.38629  1.38629
          0.09340  3.11037  3.11037  1.46634  0.26236  1.09861  0.40547
   1729   1.41594  1.38892  1.39938  1.34243   6542 - -
          1.38629  1.38629  1.38629  1.38629
          0.09340  3.11037  3.11037  1.46634  0.26236  1.09861  0.40547
   1730   1.38706  1.48219  1.31782  1.36520   6543 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1731   1.29749  1.49805  1.32891  1.43358   6544 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1732   1.35734  1.50044  1.26668  1.43607   6545 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1733   1.38966  1.45096  1.36692  1.34092   6546 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1734   1.29749  1.49805  1.32891  1.43358   6547 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1735   1.39129  1.39362  1.36832  1.39217   6548 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1736   1.38966  1.45096  1.36692  1.34092   6549 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1737   1.35734  1.50044  1.26668  1.43607   6550 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1738   1.39129  1.39362  1.36832  1.39217   6551 - -
          1.38629  1.38629  1.38629  1.38629
          0.09424  3.10184  3.10184  1.46634  0.26236  1.09861  0.40547
   1739   1.38966  1.45096  1.36692  1.34092   6552 - -
          1.38629  1.38629  1.38629  1.38629
          0.04879  3.04452        *  1.46634  0.26236  0.00000        *
//

"""

if __name__ == '__main__':
    main()