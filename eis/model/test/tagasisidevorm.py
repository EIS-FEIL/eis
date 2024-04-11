"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.usersession import _

class Tagasisidevorm(EntityHelper, Base):
    """Testi tagasisidevormi mall
    """
    LIIK_KIRJELDUS = 0 # testi kirjeldus
    LIIK_OPILANE = 1 # õpilase tulemused õpilasele
    LIIK_GRUPPIDETULEMUSED = 4 # gruppide tulemused
    LIIK_OPETAJA = 3 # õpilase tulemused õpetajale
    LIIK_OSALEJATETULEMUSED = 2 # osalejate tulemused
    LIIK_VALIM = 5 # valimi koondtulemus
    LIIK_RIIKLIK = 6 # riiklik tagasiside (kuvamiseks avalikus testide tulemuste statistikas)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100)) # vormi nimi
    test_id = Column(Integer, ForeignKey('test.id'), index=True) # viide testile (puudub malli alamosa korral)
    test = relationship('Test', foreign_keys=test_id, back_populates='tagasisidevormid')
    liik = Column(Integer) # vormi liik: NULL - vormi alamosa; 0 - testi kirjeldus; 1 - õpilase tagasisidevorm; 2 - grupi tagasisidevorm klasside tulemuste sakil; 3 - õpetaja/läbiviija tagasisidevorm ühe õpilase kohta; 4 - grupi tagasisidevorm õpilaste tulemuse sakil
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS
    ylem_id = Column(Integer, ForeignKey('tagasisidevorm.id'), index=True) # viide ülemale väärtusele (alamosa korral)
    ylem = relationship('Tagasisidevorm', foreign_keys=ylem_id, remote_side=id, back_populates='alamosad')
    alamosad = relationship('Tagasisidevorm', back_populates='ylem', order_by='Tagasisidevorm.seq') # alamosad
    sisu = Column(Text) # tagasisidevormi sisu
    sisu_jatk = Column(Text) # tagasisidevormi täiendatud sisu, mis ilmub klikkides "Näita rohkem" (kasutusel testi kirjelduse korral)
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # vormi olek: 0=const.B_STAATUS_KEHTETU - ei ole kasutusel; 1=const.B_STAATUS_KEHTIV - kehtiv käsitsi koostatud vorm; 4=const.B_STAATUS_AUTO - automaatselt loodud vorm
    lang = Column(String(2)) # keel (kui puudub, siis ei sõltu soorituskeelest)
    seq = Column(Integer) # vormi alamosa korral alamosa jrk nr
    nahtav_opetajale = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas õpetaja võib näha (õpilase tagasiside korral)
    
    @classmethod
    def is_individual(cls, liik):
        "Kas tagasiside liik käib ühe õpilase kohta või rühma kohta"
        return liik in (cls.LIIK_OPILANE, cls.LIIK_OPETAJA)

    @classmethod
    def can_dgm(cls, liik, dname):
        "Kas antud liiki tagasisidevormil saab kasutada antud liiki diagrammi"
        rc = False
        if cls.is_individual(liik):
            rc = dname in (const.DGM_TUNNUSED1,
                           const.DGM_BARNP,
                           const.DGM_OPYLTBL)
        elif liik in (cls.LIIK_VALIM, cls.LIIK_RIIKLIK):
            rc = dname in (const.DGM_TUNNUSED2,
                           const.DGM_HINNANG)
            
        else:
            rc = dname in (const.DGM_TUNNUSED2,
                           const.DGM_HINNANG,
                           const.DGM_KLASSYL,
                           const.DGM_GTBL,
                           const.DGM_KTBL)
        return rc

    @property 
    def lang_nimi(self):
        return Klrida.get_lang_nimi(self.lang)

    @classmethod
    def add_auto(cls, test_id, liik, sisu, kursus, lang):
        "Salvestatakse vaikimisi loodud tagasisidevorm"
        tv = Tagasisidevorm(test_id=test_id,
                            liik=liik,
                            kursus_kood=kursus,
                            sisu=sisu,
                            staatus=const.B_STAATUS_AUTO,
                            lang=lang)
        tv.nimi = tv.liik_nimi
        try:
            Session.commit()
            return tv
        except:
            pass

    def get_root(self):
        "Leitakse põhivorm"
        rcd = self
        while rcd.ylem_id:
            rcd = Tagasisidevorm.get(rcd.ylem_id)
        return rcd

    def get_full_template(self):
        data = self.get_part_template()
        for osa in self.alamosad:
            data += osa.get_part_template()
        return data

    def get_part_template(self):
        data = self.sisu or ''
        buf = f'<div class="fbrpart" id="fbrpart_{self.id}">\n' + data
        sisu_jatk = self.sisu_jatk
        if sisu_jatk:
            buf += '<div class="fbrtextless">\n' +\
                   '<div class="fbrtextmore">' + sisu_jatk + '</div>\n' +\
                   '</div>'
        buf += '</div>\n'
        return buf

    def get_seq(self):
        "Luuakse alamosa jrk nr (kui on alamosavorm)"
        if self.ylem_id:
            return self.get_seq_parent('ylem_id', self.ylem_id)

    @classmethod
    def get_vorm(cls, test_id, liik, lang=None, kursus=None):
        "Leitakse testis praegu kasutusel olev vorm, mis on soovitud liigiga"
        q = (cls.queryR
             .filter_by(test_id=test_id)
             .filter_by(liik=liik)
             .filter_by(ylem_id=None)
             .filter(cls.staatus>=const.B_STAATUS_KEHTIV))
        if kursus:
            q = q.filter(sa.or_(cls.kursus_kood==kursus,
                                cls.kursus_kood==None))
        if lang:
            q = q.filter(sa.or_(cls.lang==lang,
                                cls.lang==None))
        else:
            # keel pole teada - vaatame, kasutame eesti keele või kõigile keeltele tehtud vormi
            q1 = (q.filter(sa.or_(cls.lang==const.LANG_ET,
                                  cls.lang==None))
                  .order_by(cls.staatus, cls.kursus_kood))
            r = q1.first()
            if r:
                return r
        q = q.order_by(cls.staatus, cls.lang, cls.kursus_kood)
        return q.first()
    
    @property
    def liik_nimi(self):
        values = {key: val for (key, val) in self.opt_liik()}
        return values.get(self.liik)

    @classmethod
    def opt_liik(self):
        return [(Tagasisidevorm.LIIK_KIRJELDUS, _("Testi kirjeldus")),
                (Tagasisidevorm.LIIK_GRUPPIDETULEMUSED, _("Gruppide tulemused")),
                (Tagasisidevorm.LIIK_OSALEJATETULEMUSED, _("Osalejate tulemused")),
                (Tagasisidevorm.LIIK_OPETAJA, _("Õpetaja tagasiside õpilase kohta")),
                (Tagasisidevorm.LIIK_OPILANE, _("Õpilase tagasiside")),
                (Tagasisidevorm.LIIK_VALIM, _("Valimi koondtulemus")),
                (Tagasisidevorm.LIIK_RIIKLIK, _("Riiklik tagasiside")),
                ]

    @classmethod
    def get_list_f(cls, test, c):
        """Leitakse testi tagasisidevormide list, sõltuvalt liigist lisatakse
        sisseehitatud vormid F1 ja F2 ja F3 ja F4
        """
        liigid = {key: value for (key, value) in cls.opt_liik()}
        items = list(test.tagasisidevormid)
        # lisame sisseehitatud vormid
        if test.tagasiside_mall == const.TSMALL_DIAG:
            liik = Tagasisidevorm.LIIK_OSALEJATETULEMUSED
            item = c.new_item(id='F2',
                              nimi=_("Süsteemisisene vorm"),
                              liik=liik,
                              liik_nimi=liigid.get(liik))
            item.staatus = len([r for r in items if r.liik==item.liik and r.staatus]) == 0
            items.insert(0, item)

            liik = Tagasisidevorm.LIIK_VALIM
            item = c.new_item(id='F3',
                              nimi=_("Süsteemisisene vorm"),
                              liik=liik,
                              liik_nimi=liigid.get(liik))
            item.staatus = len([r for r in items if r.liik==item.liik and r.staatus]) == 0
            items.insert(0, item)

            if test.testiliik_kood == const.TESTILIIK_TASEMETOO:
                liik = Tagasisidevorm.LIIK_RIIKLIK
                item = c.new_item(id='F4',
                                nimi=_("Süsteemisisene vorm"),
                                liik=liik,
                                liik_nimi=liigid.get(liik))
                item.staatus = len([r for r in items if r.liik==item.liik and r.staatus]) == 0
                items.insert(0, item)
            
        if test.tagasiside_mall in (const.TSMALL_DIAG, const.TSMALL_OPIP):
            liik = Tagasisidevorm.LIIK_OPILANE
            item = c.new_item(id='F1',
                              nimi=_("Süsteemisisene vorm"),
                              liik=liik,
                              liik_nimi=liigid.get(liik))
            item.staatus = len([r for r in items if r.liik==item.liik and r.staatus]) == 0
            items.insert(0, item)

        if test.tagasiside_mall in (const.TSMALL_PSYH, ):
            liik = Tagasisidevorm.LIIK_OPETAJA
            item = c.new_item(id='F1',
                              nimi=_("Süsteemisisene vorm"),
                              liik=liik,
                              liik_nimi=liigid.get(liik))
            item.staatus = len([r for r in items if r.liik==item.liik and r.staatus]) == 0
            items.insert(0, item)
        return items

    def copy(self, ignore=[], staatus=None):
        cp = EntityHelper.copy(self, ignore=ignore)
        if staatus is not None:
            cp.staatus = staatus
        for rcd in self.alamosad:
            rcd_cp = rcd.copy(staatus=staatus)
            rcd_cp.ylem = cp
            cp.alamosad.append(rcd_cp)
        return cp

    def delete_subitems(self):    
        self.delete_subrecords(['alamosad'])

