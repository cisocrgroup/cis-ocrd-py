![build status](https://travis-ci.org/cisocrgroup/cis-ocrd-py.svg?branch=dev)
# cis-ocrd-py

[CIS](http://www.cis.lmu.de) [OCR-D](http://ocr-d.de) command line tools

## General usage

### Essential system packages

```sh
sudo apt-get install \
  git \
  build-essential \
  python3 python3-pip \
  libxml2-dev \
  default-jdk
```



### Virtualenv

Use `virtualenv` to install dependencies:
* `virtualenv -p python3.6 env`
* `source env/bin/activate`
* `pip install -e path/to/dir/containing/setup.py`

Use `deactivate` to deactivate the virtualenv again.

### OCR-D workspace

* Create a new (empty) workspace: `ocrd workspace init workspace-dir`
* cd into `workspace-dir`
* Add new file to workspace: `ocrd workspace add file -G group -i id
  -m mimetype`

### Tests

Issue `make test` to run the automated test suite. The tests depend on
the following tools:

* [wget](https://www.gnu.org/software/wget/)
* [envsubst](https://linux.die.net/man/1/envsubst)

You can run individual testcases using the `run_*_test.bash` scripts in
the tests directory. Use the `--persistent` or `-p` flag to keep
temporary directories.

You can override the temporary directory by setting the `TMP_DIR` environment
variable.

## Tools

### ocrd-cis-align

The alignment tool line-aligns multiple file groups. It can be used to
align the results of multiple OCRs with their respective ground-truth.

The tool expects a comma-separated list of input file groups, the
according output file group and the url of the configuration file:

```sh
ocrd-cis-align \
  --input-file-grp 'ocr1,ocr2,gt' \
  --output-file-grp 'ocr1+ocr2+gt' \
  --mets mets.xml \
  --parameter file:///path/to/config.json
```


### ocrd-cis-ocropy-train
The ocropy-train tool can be used to train LSTM models.
It takes ground truth from the workspace and saves (image+text) snippets from the corresponding pages.
Then a model is trained on all snippets for 1 million (or the given number of) randomized iterations from the parameter file.
```sh
ocrd-cis-ocropy-train \
  --input-file-grp OCR-D-GT-SEG-LINE \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-clip
The ocropy-clip tool can be used to remove intrusions of neighbouring segments in regions / lines of a workspace.
It runs a (ad-hoc binarization and) connected component analysis on every text region / line of every PAGE in the input file group, as well as its overlapping neighbours, and for each binary object of conflict, determines whether it belongs to the neighbour, and can therefore be clipped to white. It references the resulting segment image files in the output PAGE (as AlternativeImage).
```sh
ocrd-cis-ocropy-clip \
  --input-file-grp OCR-D-SEG-LINE \
  --output-file-grp OCR-D-SEG-LINE-CLIP \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-resegment
The ocropy-resegment tool can be used to remove overlap between lines of a workspace.
It runs a (ad-hoc binarization and) line segmentation on every text region of every PAGE in the input file group, and for each line already annotated, determines the label of largest extent within the original coordinates (polygon outline) in that line, and annotates the resulting coordinates in the output PAGE.
```sh
ocrd-cis-ocropy-resegment \
  --input-file-grp OCR-D-SEG-LINE \
  --output-file-grp OCR-D-SEG-LINE-RES \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-segment
The ocropy-segment tool can be used to segment regions into lines.
It runs a (ad-hoc binarization and) line segmentation on every text region of every PAGE in the input file group, and adds a TextLine element with the resulting polygon outline to the annotation of the output PAGE.
```sh
ocrd-cis-ocropy-segment \
  --input-file-grp OCR-D-SEG-BLOCK \
  --output-file-grp OCR-D-SEG-LINE \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-deskew
The ocropy-deskew tool can be used to deskew pages / regions of a workspace.
It runs the Ocropy thresholding and deskewing estimation on every segment of every PAGE in the input file group and annotates the orientation angle in the output PAGE.
```sh
ocrd-cis-ocropy-deskew \
  --input-file-grp OCR-D-SEG-LINE \
  --output-file-grp OCR-D-SEG-LINE-DES \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-denoise
The ocropy-denoise tool can be used to despeckle pages / regions / lines of a workspace.
It runs the Ocropy "nlbin" denoising on every segment of every PAGE in the input file group and references the resulting segment image files in the output PAGE (as AlternativeImage). 
```sh
ocrd-cis-ocropy-denoise \
  --input-file-grp OCR-D-SEG-LINE-DES \
  --output-file-grp OCR-D-SEG-LINE-DEN \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-binarize
The ocropy-binarize tool can be used to binarize, denoise and deskew pages / regions / lines of a workspace.
It runs the Ocropy "nlbin" adaptive thresholding, deskewing estimation and denoising on every segment of every PAGE in the input file group and references the resulting segment image files in the output PAGE (as AlternativeImage). (If a deskewing angle has already been annotated in a region, the tool respects that and rotates accordingly.) Images can also be produced grayscale-normalized.
```sh
ocrd-cis-ocropy-binarize \
  --input-file-grp OCR-D-SEG-LINE-DES \
  --output-file-grp OCR-D-SEG-LINE-BIN \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-dewarp
The ocropy-dewarp tool can be used to dewarp text lines of a workspace.
It runs the Ocropy baseline estimation and dewarping on every line in every text region of every PAGE in the input file group and references the resulting line image files in the output PAGE (as AlternativeImage).
```sh
ocrd-cis-ocropy-dewarp \
  --input-file-grp OCR-D-SEG-LINE-BIN \
  --output-file-grp OCR-D-SEG-LINE-DEW \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

### ocrd-cis-ocropy-recognize
The ocropy-recognize tool can be used to recognize lines / words / glyphs from pages of a workspace.
It runs the Ocropy optical character recognition on every line in every text region of every PAGE in the input file group and adds the resulting text annotation in the output PAGE.
```sh
ocrd-cis-ocropy-recognize \
  --input-file-grp OCR-D-SEG-LINE-DEW \
  --output-file-grp OCR-D-OCR-OCRO \
  --mets mets.xml
  --parameter file:///path/to/config.json
```

## All in One Tool
For the all in One Tool install all above tools and Tesserocr as explained below.
Then use it like:
```sh
ocrd-cis-aio --parameter file:///path/to/config.json
```


### Tesserocr
Install essential system packages for Tesserocr
```sh
sudo apt-get install python3-tk \
  tesseract-ocr libtesseract-dev libleptonica-dev \
  libimage-exiftool-perl libxml2-utils
```

Then install Tesserocr from: https://github.com/OCR-D/ocrd_tesserocr
```sh
pip install -r requirements.txt
pip install .
```

Download and move tesseract models from:
https://github.com/tesseract-ocr/tesseract/wiki/Data-Files
or use your own models
place them into: /usr/share/tesseract-ocr/4.00/tessdata

Tesserocr v2.4.0 seems broken for tesseract 4.0.0-beta. Install
Version v2.3.1 instead: `pip install tesseract==2.3.1`.

## Workflow configuration

A decent pipeline might look like this:

1. page-level cropping
2. page-level binarization
3. page-level deskewing
4. page-level dewarping
5. region segmentation
6. region-level clipping
7. region-level deskewing
8. line segmentation
9. line-level clipping or resegmentation
10. line-level dewarping
11. line-level recognition
12. line-level alignment

If GT is used, steps 1, 5 and 8 can be omitted. Else if a segmentation is used in 5 and 8 which does not produce overlapping sections, steps 6 and 9 can be omitted.

## OCR-D links

- [OCR-D](https://ocr-d.github.io)
- [Github](https://github.com/OCR-D)
- [Project-page](http://www.ocr-d.de/)
- [Ground-truth](http://www.ocr-d.de/sites/all/GTDaten/IndexGT.html)
