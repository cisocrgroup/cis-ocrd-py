from __future__ import absolute_import
import json
from ocrd import Processor
from ocrd import MIMETYPE_PAGE
from ocrd.utils import getLogger
from ocrd.model.ocrd_page import from_file
from ocrd.model.ocrd_page import to_xml
from ocrd.model.ocrd_page_generateds import TextEquivType
from ocrd_cis import JavaProcess
from ocrd_cis import get_ocrd_tool


class Aligner(Processor):
    def __init__(self, *args, **kwargs):
        ocrd_tool = get_ocrd_tool()
        kwargs['ocrd_tool'] = ocrd_tool['tools']['ocrd-cis-align']
        kwargs['version'] = ocrd_tool['version']
        super(Aligner, self).__init__(*args, **kwargs)
        self.log = getLogger('cis.Processor.Aligner')

    def process(self):
        ifgs = self.input_file_grp.split(",")  # input file groups
        if len(ifgs) < 2:
            raise Exception("need at least two input file groups to align")
        ifts = self.zip_input_files(ifgs)  # input file tuples
        page_alignments = list()
        for ift in ifts:
            output = self.run_java_aligner(ift)
            page_alignments.append(PageAlignment(ifgs, ift, output))
        for pa in page_alignments:
            for la in pa.line_alignments:
                self.log.info("%s", la)
            self.write_alignment_to_xml(pa)
        self.workspace.save_mets()

    def zip_input_files(self, ifgs):
        """Zip files of the given input file groups"""
        files = list()
        for ifg in ifgs:
            self.log.info("input file group: %s", ifg)
            ifiles = sorted(
                self.workspace.mets.find_files(fileGrp=ifg),
                key=lambda ifile: ifile.ID)
            for i in ifiles:
                self.log.info("sorted file: %s %s", i.url, i.ID)
            self.log.info("input files: %s", ifiles)
            files.append(ifiles)
        return zip(*files)

    def write_alignment_to_xml(self, pa):
        """
        Write the alignments into new output-file-group.
        The alignment is done by the master file (first index).
        """
        self.log.info("writing alignment to %s", self.output_file_grp)
        master = pa.ifs[0]  # master input file group
        pcgts = from_file(self.workspace.download_file(master))
        ilist = iter(pa.line_alignments)
        for region in pcgts.get_Page().get_TextRegion():
            for line in region.get_TextLine():
                line.get_TextEquiv()[0].Unicode.strip()
                self.log.debug("line: %s", line.get_TextEquiv()[0].Unicode)
                current = next(ilist)
                pa.add_line_alignments(line, current)
                pa.add_word_alignments(line, current)
        self.log.debug("master basename: %s", master.basename)
        self.add_output_file(
            ID="{}_{}".format(master.ID, self.output_file_grp),
            mimetype=MIMETYPE_PAGE,
            content=to_xml(pcgts),
            file_grp=self.output_file_grp,
            basename=master.basename,
        )

    def read_lines_from_input_file(self, ifile):
        self.log.info("reading input file: %s", ifile.url)
        lines = list()
        pcgts = from_file(self.workspace.download_file(ifile))
        for region in pcgts.get_Page().get_TextRegion():
            for line in region.get_TextLine():
                lines.append(line.get_TextEquiv()[0].Unicode)
        return lines

    def run_java_aligner(self, ifs):
        lines = list()
        for ifile in ifs:
            lines.append(self.read_lines_from_input_file(ifile))
        lines = zip(*lines)
        _input = [x.strip() for t in lines for x in t]
        for i in _input:
            self.log.debug("input line: %s", i)
        n = len(ifs)
        p = JavaProcess.aligner(
            jar=self.parameter['cisOcrdJar'],
            args=[str(n)]
        )
        return p.run("\n".join(_input))


class PageAlignment:
    """PageAlignment holds a list of LineAlignments."""
    def __init__(self, ifgs, ifs, process_output):
        """
        Create a page alignment from java-aligner's output.

        It reads blocks of len(ifs) lines. Each block is assumed to be a
        valid input for the LineAlignment constructor.
        """
        self.ifgs = ifgs
        self.ifs = ifs
        self.log = getLogger('cis.PageAlignment')
        self.line_alignments = list()
        lines = process_output.split("\n")
        n = len(self.ifs)
        for i in range(0, len(lines), n):
            self.line_alignments.append(LineAlignment(lines[i:i+n]))

    def add_word_alignments(self, page_xml_line, alignment_line):
        """
        Add word alignments to the words of the given page XML line.
        We iterate over the master-OCR words, so the first word of the
        tuple must be contained in the given page XML word.
        """
        k = 0
        for word in page_xml_line.get_Word():
            word.get_TextEquiv()[0].set_dataType(self.ifgs[0])
            page_xml_word = word.get_TextEquiv()[0].Unicode
            if (k < len(alignment_line.tokens) and
                    alignment_line.tokens[k][0] in page_xml_word):
                self.log.debug("word: %s", page_xml_word)
                for (i, w) in enumerate(alignment_line.tokens[k]):
                    self.log.debug(" - word: %s (%s)", w, self.ifgs[i])
                    eq = TextEquivType(
                        index=i+1,
                        dataType='alignment-token-{}'.format(self.ifgs[i]),
                        Unicode=w,
                    )
                    word.add_TextEquiv(eq)
                k += 1

    def add_line_alignments(self, page_xml_line, alignment_line):
        """
        Add alignment TextEquivs to the given page XML line.
        """
        self.log.debug("line %s", page_xml_line.get_TextEquiv()[0].Unicode)
        self.log.debug(" - line: %s (%s)",
                       alignment_line.pairwise[0][0], self.ifgs[0])
        page_xml_line.get_TextEquiv()[0].set_dataType(self.ifgs[0])
        eq = TextEquivType(
            dataType="alignment-line-{}".format(self.ifgs[0]),
            Unicode=alignment_line.pairwise[0][0],
        )
        page_xml_line.add_TextEquiv(eq)
        for i in range(0, len(alignment_line.pairwise)):
            self.log.debug(" - line: %s (%s)",
                           alignment_line.pairwise[i][1], self.ifgs[i+1])
            eq = TextEquivType(
                dataType="alignment-line-{}".format(self.ifgs[i+1]),
                Unicode=alignment_line.pairwise[i][1],
            )
            page_xml_line.add_TextEquiv(eq)


class LineAlignment:
    """
    LineAlignment holds a line alignment.
    A line alignment of n lines holds n-1 pairwise alignments
    and a list of token alignments of n-tuples.

    Each pairwise alignment represents the alignment of the
    master line with another. Pairwise aligned lines have always
    the same length. Underscores ('_') mark deletions or insertions.
    """
    def __init__(self, lines):
        """
        Create a LineAlignment from n-1 pairwise
        alignments an one token alignment at pos n-1.
        """
        self.n = len(lines)
        self.pairwise = list()
        for i in range(0, self.n-1):
            self.pairwise.append(tuple(lines[i].split(",")))
        self.tokens = list()
        for ts in lines[self.n-1].split(","):
            self.tokens.append(tuple(ts.split(":")))

    def __str__(self):
        data = {}
        data['pairwise'] = self.pairwise
        data['tokens'] = self.tokens
        return json.dumps(data)
