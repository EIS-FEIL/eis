# -*- coding: utf-8 -*- 

import logging
import io
import sys
import os
import re
from PyRTF.Renderer import *
from PyRTF.Elements import *

class RtfDoc(object):
    settings = None
    error = None # veateade

    def generate(self):
        "PDFi genereerimine ja selle sisu väljastamine"
        output = io.StringIO()
        self.generate_into(output)
        data = output.getvalue()
        output.close()
        return data
        
    def generate_into(self, output):
        rdoc = self.gen_story()
        DR = Renderer()
        DR.Write(rdoc, output)

    def gen_story(self):
        "RTFi sisu jaoks andmete pärimine ja RTFi sisu genereerimine"
        doc = Document()
        section = Section()
        doc.Sections.append(section)
        section.append('Hello')
        return doc

if __name__ == '__main__':
    fn = 'katsetus.rtf'
    output = file(fn, 'w')
    RtfDoc().generate_into(output)
    output.close()
