from eis.tests.basetest import *

class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()

    def test_inmemoryzip(self):
        from eis.lib.inmemoryzip import InMemoryZip
        data = InMemoryZip().append('test.txt', 'proov').close().read()
        files = InMemoryZip(data).extract()
        print(files)

    def test_pdf(self):
        from eis.lib.pdf.pdfdoc import PdfDoc
        from eis.lib.pdf.pages.pdfutils import Paragraph
        from eis.lib.pdf.pages.stylesheet import N
        story = []
        story.append(Paragraph('Hello', N))
        data = PdfDoc().generate_from_story(story)
        assert len(data)

