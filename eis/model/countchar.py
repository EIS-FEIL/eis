import re

class CountChar:
    "Tähemärkide loendamise abifunktsioonid"
    def __init__(self, orig_lang, lang):
        self.orig_lang = orig_lang
        self.lang = lang
        
    def _html2txt(self, s):
        "Kireva teksti teisendamine tavaliseks"
        return re.sub(r'<[^>]*>', '', s)

    def count(self, value, rtf):
        "Teksti sisu tähtede lugemine"
        if rtf and value:
            value = self._html2txt(value)
        if value:
            value = re.sub(r'\s+', ' ', value).strip()
        return value and len(value) or 0

    def tran(self, obj, add=False):
        if not self.lang or self.lang == self.orig_lang: 
            return obj
        elif add:
            return obj.give_tran(self.lang)
        else:
            return obj.tran(self.lang, False)

