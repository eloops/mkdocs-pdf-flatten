import yaml, os, codecs
from pdf_flatten.exceptions import FatalError
from PyPDF2 import PdfFileWriter, PdfFileReader

class PdfTreeFlatten:
    """Top level converter class. Instatiate separately for each mkdocs.yml."""

    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config_file', 'mkdocs.yml')
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.outfile = kwargs.get('outfile', 'output.pdf')
        self.max_level = 0

        try:
            cfg = codecs.open(self.config_file, 'r', self.encoding)
        except IOError as e:
            raise FatalError("Couldn't open %s for reading: %s" % (self.config_file,
                e.strerror), 1)

        self.config = yaml.load(cfg)

        if not 'docs_dir' in self.config:
            self.config['docs_dir'] = 'docs'

        if not 'site_dir' in  self.config:
            self.config['site_dir'] = 'site'

        cfg.close()

    def flatten_pages(self, pages, level=1, parent=None):
        """Recursively flattens pages data structure into a one-dimensional data structure"""
        flattened = []
        if self.max_level < level:
            self.max_level = level
        for page in pages:
            if type(page) is list:
                flattened.append(
                             {
                                'file': page[0],
                                'title': page[1],
                                'level': level,
                                'parent': parent,
                                'children': [],
                             })
            if type(page) is dict:
                if type(list(page.values())[0]) is str:
                    flattened.append(
                            {
                                'file': list(page.values())[0],
                                'title': list(page.keys())[0],
                                'level': level,
                                'parent': parent,
                                'children': [],
                             })
                if type(list(page.values())[0]) is list:
                    flattened.append(
                            {
                                'file': None,
                                'title': list(page.keys())[0],
                                'level': level,
                                'parent': parent,
                                'children': [],
                            })
                    flattened.extend(
                            self.flatten_pages(
                                list(page.values())[0],
                                level + 1, list(page.keys())[0])
                            )

        child_list = {None: ['Home']}
        for page in flattened:
            try:
                if (page['title'] not in child_list[page['parent']]):
                    child_list[page['parent']].append(page['title'])
            except KeyError as inst:
                child_list[page['parent']] = [page['title']]
            
        for page in flattened:
            if (page['title'] in child_list):
                page['children'] = child_list[page['title']]

        return flattened

    def convert(self):
        """
        User-facing conversion method. Converts to PDF Document and returns dict of values
        """

        pages = self.flatten_pages(self.config['nav'])
        
        pdf_writer = PdfFileWriter()
        pdf_writer.setPageMode('/UseOutlines')

        num_pages = 0
        bookmarks = {'Home': [1]}

        for page in pages:
            if (page['file'] == 'index.md'):
                fname = os.path.join(self.config['site_dir'], page['file'].split('/')[-1][:-3] + ".pdf")
                pdf_reader = PdfFileReader(fname)
            
                for pdf_page in range(pdf_reader.getNumPages()):
                    pdf_writer.addPage(pdf_reader.getPage(pdf_page))

                num_pages = pdf_writer.getNumPages()
                continue
            if (page['file'] is None and page['parent'] is None):
                bookmarks[page['title']] = [num_pages + 1]
                continue
            if (page['file'] is None and page['parent'] is not None):
                bookmarks[page['title']] = [num_pages + 1]
                continue
            if (page['file'] is not None and page['parent'] is not None):
                fname = os.path.join(self.config['site_dir'], page['file'][:-3], page['file'].split('/')[-1][:-3] + ".pdf")
                pdf_reader = PdfFileReader(fname)
                bookmarks[page['title']] = [num_pages + 1]

                for pdf_page in range(pdf_reader.getNumPages()):
                    pdf_writer.addPage(pdf_reader.getPage(pdf_page))

                num_pages = pdf_writer.getNumPages()
                continue
            if (page['file'] is not None and page['parent'] is None):
                fname = os.path.join(self.config['site_dir'], page['file'][:-3], page['file'].split('/')[-1][:-3] + ".pdf")
                pdf_reader = PdfFileReader(fname)
                bookmarks[page['title']] = [num_pages + 1]

                for pdf_page in range(pdf_reader.getNumPages()):
                    pdf_writer.addPage(pdf_reader.getPage(pdf_page))

                num_pages = pdf_writer.getNumPages()
                continue

        for page in pages:
            if (page['level'] == 1):
                bookmarks[page['title']].append(pdf_writer.addBookmark(page['title'], bookmarks[page['title']][0] - 1))

        for level in range(2, self.max_level):
            for page in pages:
                if (page['level'] == level):
                    bookmarks[page['title']].append(pdf_writer.addBookmark(page['title'], bookmarks[page['title']][0] - 1, bookmarks[page['parent']][1]))

        print("Total pages for output: {0}".format(pdf_writer.getNumPages()))
        # print(bookmarks)

        with open(self.outfile, 'wb') as out_pdffile:
            pdf_writer.write(out_pdffile)  
        
        return(pages)
