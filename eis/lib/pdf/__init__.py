# -*- coding: utf-8 -*- 
import os
import re
import io
from . import pages_loader

def hello(txt):
    output = io.BytesIO()

    cnv = canvas.Canvas(output, bottomup=0)
    cnv.setAuthor('EIS')
    cnv.setSubject('väljund')
    cnv.setTitle('AAA')
    cnv.drawString(100,100,txt)
    cnv.showPage()
    cnv.save()

    data = output.getvalue()
    output.close()
    return data

