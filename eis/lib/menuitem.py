# -*- coding: utf-8 -*-
"""Menüü ühe menüüpunkti klass koos infoga selle kohta, 
millise õigusega kasutajatele menüüpunkt kuvatakse.
"""

import logging
log = logging.getLogger(__name__)

class MenuItem(object):
    "Valik menüüs"

    @classmethod
    def get_id(cls):
        "Menüüvalikute nummerdamine õiguste maski jaoks"
        cls.id = cls.id + 1
        return cls.id - 1
    
    @classmethod
    def initmenu(cls, url_prefix=''):
        """Menüü koostamise eeltegevus.
        Nullitakse menüüpunktide numeratsioon (kasutusel maskis).
        Omistatakse URLi prefiks.
        """
        cls.id = 0
        cls.mask = ''
        cls.url_prefix = url_prefix

    @classmethod
    def set_allowed_in_mask(cls, id, isAllowed):
        """
        Jätame maskis meelde, kas antud id-ga menüüvaliku jaoks on õigus olemas.
        Muudetakse maskis kohal nr id oleva sümboli väärtust:
        kui on õigus, siis pannakse 1, muidu pannakse 0.
        """
        if len(cls.mask) <= id:
            cls.mask = cls.mask + '0' * (id - len(cls.mask) + 1)
        cls.mask = cls.mask[:id] + str(int(isAllowed)) + cls.mask[id+1:]

    is_authorization = True
    
    def __init__(self, title=None, url=None, hint=None, subitems=[], image=None, is_authorization=True, permission=None, koht=False, kohatu=False, fn_check=None, maakond=None):
        self.id = MenuItem.get_id()
        self.title = title
        self.url = url
        self.hint = hint or title
        self.subitems = subitems
        self.image = image or 'px.gif'
        self.is_group = len(subitems) > 0
        self.width = "16"
        self.is_authorization = is_authorization # kas autoriseerimine on vajalik
        self.permission = permission or url # õigus, mis peab selle menüü kasutamiseks olemas olema
        self.fn_check = fn_check # funktsioon, mille argumendiks on koht ja mis kontrollib õiguse puudumist
        self.koht = koht # True/False, kas koht on vajalik
        self.kohatu = kohatu # True - kui menyy esineb (avalikus vaates) ainult siis, kui kasutajal pole seotud yhegi kooliga, mille all seda menyyd näidata
        self.maakond = maakond # True/False/None, kas kasutaja peab/ei tohi esindama maakonnavalitsust
        if url is None and not subitems:
            # pole veel valmis
            self.title = '<s>%s</s>' % (self.title or '...')

    def set_level(self, nLevel):
        "Menüü sügavuse parameetri väärtustamine"
        
        self.nLevel = nLevel
        if nLevel <= 1:
            self.width = "1"
        for subitem in self.subitems:
            subitem.set_level(nLevel + 1)

    def is_permitted(self, permissions, koht_id, kohatu, valitsus_tasekood):
        """
        Kontrollitakse, kas kasutajal on õigus antud menüüvalikut kasutada.
        Kasutaja õiguste loetelu on permissions
        """
        rc = False
        #if not self.url:
        #    rc = False
        if self.url.startswith('javascript'): # logout
            rc = True
        elif self.koht and not koht_id:
            # vajalik on, et oleks määratud koht
            rc = False
        elif self.fn_check and not self.fn_check(koht_id):
            rc = False
        elif self.maakond and (not valitsus_tasekood or valitsus_tasekood[0] != '1'):
            # peab olema maakonnavalitsus
            rc = False
        elif self.maakond == False and valitsus_tasekood:
            # ei tohi olla maakonnavalitsus
            rc = False
        elif self.kohatu and not kohatu:
            # lubatud ainult neile, kes pole seotud yhegi kooliga
            rc = False
        else:
            # kui mõni õigus on olemas, siis kuvatakse menyy
            for p in self.permission.split(','):
                rc = p in list(permissions.keys())
                if rc:
                    break

        if rc:
            MenuItem.set_allowed_in_mask(self.id, True)
        return rc

    def is_empty_group(self):
        """
        Peale lubamata alammenüüde eemaldamist kontrollitakse selle funktsiooniga,
        kas menüüvaliku all on kasutajal üldse võimalik midagi teha.
        Kui ei ole, siis tagastatakse True.
        """
        if self.is_group:
            # menyyvalikut saab kasutada juhul, kui sisaldab alamvalikuid
            rc = True
            for item in self.subitems:
                if type(item) == type(self):
                    # on olemas alamvalik
                    rc = False
                    break
        else:
            # menyyvalik on ise link
            rc = False

        return rc

    def remove_not_permitted(self, permissions, koht_id, kohatu, valitsus_tasekood=None):
        """
        Eemaldatakse alamvalikud, millele ei ole kasutajal õigust
        Kasutaja õiguste loetelu on permissions        
        Tagastab maski
        """
        removables = []
        for item in self.subitems:
            if isinstance(item, MenuItem):
                if item.subitems:
                    item.remove_not_permitted(permissions, koht_id, kohatu, valitsus_tasekood)
                    if item.is_empty_group():
                        removables.append(item)
                elif not item.is_permitted(permissions, koht_id, kohatu, valitsus_tasekood):
                    removables.append(item)

        for item in removables:
            MenuItem.set_allowed_in_mask(item.id, False)
            self.subitems.remove(item)
        return MenuItem.mask
        
    def remove_not_in_mask(self, mask):
        """
        Eemaldatakse alamvalikud, millele ei ole kasutajal õigust
        Kasutaja õiguste mask on parameetris mask 
        """
        removables = []
        for item in self.subitems:
            if isinstance(item, MenuItem):
                if item.subitems:
                    item.remove_not_in_mask(mask)
                    if item.is_empty_group():
                        removables.append(item)
                elif not mask or len(mask) <= item.id or mask[item.id] != '1':
                    removables.append(item)

        for item in removables:
            self.subitems.remove(item)

    def get_debug_info(self, mask):
        buf = ''
        for item in self.subitems:
            if type(item) == type(self):
                cMask = len(mask) <= item.id and '-' or mask[item.id]
                buf = buf + 'id=%d, maskis=%s, %s<br>\n' % (item.id, cMask, item.title)
                buf = buf + item.get_debug_info(mask)
        return buf

    def _indentation(self):
        return '  ' * self.nLevel

    def __repr__(self):
        return '<MenuItem %s>' % (self.url)

    def get_url(self):
        if self.url:
            return MenuItem.url_prefix + self.url
        else:
            return ''

if __name__=='__main__':
    MenuItem.initmenu('prefix')
    # menüü ehk kõigi menüüpunktide loetelu
    menu = MenuItem(subitems=
        [
        MenuItem('Avalikud ülesanded', 'lahendamine'),
        MenuItem('Testide sooritamine', None, subitems=
                 [MenuItem('Minu andmed', None, permission='minu'),
                  MenuItem('Registreerimine', None, permission='sooritamine'),
                  MenuItem('Sooritamine', 'sooritamised', permission='sooritamine'),
                  MenuItem('Sooritatud testid ja tulemused', 'tulemused', permission='minu'),
                  ]),
        ])
    menu.set_level(0)    

    # konkreetse kasutaja õiguste loetelu
    permissions = ['lahendamine',
                   'sooritamine',
                   ]

    # leitakse, millised menüüpunktid on antud kasutajale lubatud.
    # tagastatakse mask, milleks on string, kus n-ndal kohal 
    # asub 0 siis, kui menüüpunkt n pole kasutajale lubatud,
    # ja 1 siis, kui menüüpunkt n on kasutajale lubatud.
    mask = menu.remove_not_permitted(permissions, None, False)
    assert mask == '10010'
    print(mask)
