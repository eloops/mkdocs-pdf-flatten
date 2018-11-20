## mkdocs-pdf-flatten

This is meant to be used in conjunction with shauser's [mkdocs-pdf-export-plugin](https://github.com/shauser/mkdocs-pdf-export-plugin), which already does a fantastic job of adding HTML > PDF documents for each generated mkdocs page (and custom download links on each page!).

I've used some of the best parts of jgrassler's [mkdocs-pandoc](https://github.com/jgrassler/mkdocs-pandoc), which actually works really, really well. However it didn't pull the full document together with bookmarks tree laid out properly for me.

This script will:

* Parse through the mkdocs.yml file (nav section only)

* Correctly identify root level documents and headers

* Nth level documents, headers, their parents *and* their child documents

* Stitch together all PDF files generated from those .md (.html) files, into one long coherent document

* Add bookmarks at all the right places

* Model the outline (bookmark) tree in the same manner as specified in the mkdocs.yml file.

### Requirements

  [mkdocs-pdf-export-plugin](https://github.com/shauser/mkdocs-pdf-export-plugin), installed, running and tested.

  PyPDF2 (`python -m pip install PyPDF2`)

### Usage

1. Place into your parent folder with mkdocs.yml.

2. Build your mkdocs site with `python -m mkdocs build`.

3. Run `python mkdocs_pdf_flatten.py -o output.pdf`

### Options

Not much there, I've ripped most of the stuff out of the original mkdocs-pandoc in favour of just stitching the PDF's together.

  **-f** --> Specify config file

  **-e** --> Specify encoding (doesn't actually do much)

  **-o** --> Output file. Should default to output.pdf.
