"Ülesande sisuplokk"

import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error
import random
import pickle
import json
import eis.lib.utils as utils
from eis.model.entityhelper import *
from eis.model.countchar import CountChar
from .t_ylesanne import T_Sisuobjekt
from .sisuobjekt import Sisuobjekt, Taustobjekt, Meediaobjekt, Piltobjekt
from .valik import Sisuvalik, Valikupiirkond
from .kysimus import Kysimus
from eis.recordwrapper.testwrapper import SisuplokkWrapper
_ = usersession._

class Sisuplokk(EntityHelper, Base, SisuplokkWrapper):
    """Ülesande sisuplokk. Ühel ülesandel on mitu sisuplokki. 
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(25)) # sisuploki tähis, sisuploki lipiku nimetus ülesande sisu koostamise lehel (kui puudub, siis kasutatakse järjekorranumbrit seq)
    seq = Column(Integer, nullable=False) # sisuploki järjekorranumber ülesande sees
    paan_seq = Column(Integer) # paani järjekorranumber, milles sisuplokk kuvatakse (0 või 1)
    fikseeritud = Column(Boolean) # kas sisuploki kuvamise järjekord on muutumatu (kui ylesanne.segamini=true)
    tyyp = Column(String(10), nullable=False) # sisuploki tüüp: 52 - alustekst; 50 - pilt; 51 - multimeedia; 54 - muu; 53 - mat tekst; 12 - valikvastusega küsimus; 15 - järjestamine; 5 - sobitamine; 18 - seostamine; 16 - lünkvastusega küsimus; 19 - avatud vastusega küsimus; 20 - lünktekst; 4 - pangaga lünktekst; 14 - tekstiosa valik; 90 - matemaatilise teksti sisestamine; 11 - liugur; 1 - kujundi lohistamine pildile; 6 - piltide lohistamine kujunditele; 7 - pildil oleva piirkonna valik; 8 - järjestamine pildil; 9 - koha märkimine pildil; 10 - sobitamine pildil; 3 - joonistamine; 91 - kõne salvestamine; 17 - faili üleslaadimine; 24 - GeoGebra; 25 - GoogleCharts; 26 - ristsõna; 27 - alade värvimine; 28 - pildi avamine
    alamtyyp = Column(String(20)) # tüübi alamtüüp: diagrammi liik (Google Charts korral); 1 - ühetaolised hindamise seaded kõigil küsimustel (mitme valikuga tabeli korral); N - igal küsimusel oma hindamise seaded (mitme valikuga tabeli korral)
    nimi = Column(String(2000)) # pealkiri või tööjuhend
    tehn_tookask = Column(String(512)) # tehniline töökäsk 
    tookask_kood = Column(String(10)) # tehnilise töökäsu klassifikaator
    naide = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas sisuplokk on vastuse näide (siis kuvatakse õige vastus alati lahendajale ja selle ploki eest palle ei anta)
    sisu = Column(Text) # toimetajale näidatav sisu
    sisuvaade = Column(Text) # lahendajale näidatav sisu
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='sisuplokid')
    sisuobjektid = relationship('Sisuobjekt', order_by='Sisuobjekt.seq', back_populates='sisuplokk')
    ymardamine = Column(Boolean) # kas sisuploki punktide summa ümardada
    min_pallid = Column(Float) # sisuploki minimaalne võimalik toorpunktide arv (kasutusel mitme küsimusega sisuplokis); kui puudub, siis ei ole piiri
    max_pallid = Column(Float) # sisuploki maksimaalne võimalik toorpunktide arv (kasutusel mitme küsimusega sisuplokis); kui puudub, siis ei ole sisuplokil oma piiri
    kysimused = relationship('Kysimus', order_by='Kysimus.seq', back_populates='sisuplokk')
    trans = relationship('T_Sisuplokk', cascade='all', back_populates='orig')
    plokimarkused = relationship('Plokimarkus', order_by='Plokimarkus.id', back_populates='sisuplokk')
    staatus = Column(Integer, nullable=False) # kasutusel ja nähtav või mitte: 1 - kuvatakse oma kohal nähtavalt; 0 - ei kuvata oma kohal (fail, millele viidatakse mujalt URLiga); 2=const.B_STAATUS_NAHTAMATU - kuvatakse oma kohal algselt nähtamatult
    reanr = Column(Boolean) # alusteksti korral: kas kuvada lahendajale teksti reanumbrid (1,6,11,...)
    kopikeeld = Column(Boolean) # alusteksti korral: kas takistada lahendajal teksti kopeerida
    kleepekeeld = Column(Boolean) # avatud teksti korral: kas takistada lahendajal teksti väljale kleepida
    kommenteeritav = Column(Boolean) # alusteksti korral: kas lahendaja saab lahendamise ajal enda jaoks kommentaare märkida
    wirismath = Column(Boolean) # kas tekst kasutab WIRIS matemaatikaredaktorit (alusteksti korral)
    laius = Column(Integer) # veergude arv (ristsõna korral)
    korgus = Column(Integer) # ridade arv (ristsõna korral)
    suurus = Column(Integer) # ristsõna ruudu suurus pikslites 
    kujundus = Column(Integer) # kujundus: 1=const.KUJUNDUS_TAUSTATA - tekstiosa valik ilma halli taustata (tekstiosa valiku korral)
    piiraeg = Column(Integer) # küsimuse vastamiseks lubatud aeg sekundites (heli salvestamise korral)
    hoiatusaeg = Column(Integer) # mitu sekundit enne piiraja täitumist kuvada loendur punasena (heli salvestamise korral)
    tahemargid = Column(Integer) # originaalkeeles sisuploki tähemärkide arv (originaalkeeles)
    nahtavuslogi = Column(Boolean) # kas salvestada sisuploki nähtavaks tegemiste ja peitmiste aeg
    varvimata = Column(Boolean) # kas jätta vastused rohelise/punase värviga värvimata (kasutusel siis, kui õige/vale ei saa kuvada)
    pausita = Column(Boolean) # kas pausile panek on keelatud (heli salvestamise korral)
    select_promptita = Column(Boolean) # kas peita valikvälja tühja valiku prompt "--Vali--" (valikvastusega lünga korral)
    autostart_opt = Column(String(10)) # automaatne algus (heli salvestamise korral): AUTOSTART_LOAD=L - ülesande avamisel; AUTOSTART_SEQ=S - eelmise salvestuse või multimeedia lõppemisel; AUTOSTART_MEDIASTART=H - mistahes eespool oleva multimeedia mängimisega koos; AUTOSTART_MEDIA=M - mistahes multimeedia lõppemisel
    _parent_key = 'ylesanne_id'
    read_only = False
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne
        if self.logging:
            ylesanne = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
            if ylesanne:
                ylesanne.logi('Sisuplokk (%s) %s %s' % (self.tyyp_nimi, self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    # autostardi võimalused (1-kohalised, et erineda)
    AUTOSTART_LOAD = 'L'
    AUTOSTART_SEQ = 'S'
    AUTOSTART_MEDIASTART = 'H'
    AUTOSTART_MEDIA = 'M'

    def default(self):
        if self.staatus is None:
            self.staatus = const.B_STAATUS_KEHTIV

    def parse_sisu(self, sisu=None, rootdiv=True):
        """Tekstülesandes teksti parsimine XMLi dokumendiks.
        Kui XML on vigane, siis visatakse siit XMLSyntaxError.
        Kui on vaja tõlkekeele sisu parsida, siis tuleb ette anda
        sisu=self.tran(lang)
        rootdiv - True - kui juurelementi pole, siis lisatakse div
                - False - kui juurelementi pole, siis lisatakse span
                - None - kui juurelementi pole, siis sisusse ei lisata
        """
        def has_displayblock(sisu1):
            for buf in ('<table', '<div', '<p>', '<p '):
                if sisu1.find(buf) > -1:
                    return True
            return False
        
        if not sisu:
            sisu = self.sisu
        if not sisu:
            return None, None
        sisu = sisu.replace('&nbsp;',' ').strip()
        add_root = False
        try:
            tree = etree.XML(sisu)
            if tree.tag not in ('span','div','table'):
                # ei soovi, et <input> oleks juur
                add_root = True
        except etree.XMLSyntaxError as e:
            add_root = True
        if add_root:
            if rootdiv:
                # alati paneme juurelemendiks <div>
                rootel = 'div'
            else:
                # pyyame panna juurelemendiks <span>
                rootel = 'span'
                # aga ei saa seda teha siis, kui sisus esineb plokke
                if has_displayblock(sisu):
                    rootel = 'div'

            tsisu = '<%s>%s</%s>' % (rootel, sisu, rootel)
            tree = etree.XML(tsisu)
            if rootdiv is not None:
                # kui tegelikult pole tegelikult root-elementi vaja, siis rootdiv==None
                sisu = tsisu
        return sisu, tree

    def set_json_sisu(self, value, lang=None):
        "GeoGebra, ristsõna, mitme valikuga tabeli, ipunkt korral: andmete hoidmine sisu sees"
        obj = lang and self.give_tran(lang) or self
        if value:
            obj.sisu = json.dumps(value)
        else:
            obj.sisu = None

    def delete_subitems(self):
        log.debug('Sisuplokk.delete_subitems...')
        li = [rcd for rcd in self.plokimarkused if rcd.ylem_id is None]
        for rcd in li:
            rcd.delete()
        log.debug('Sisuplokk.delete_subrecords...')
        self.delete_subrecords(['kysimused',
                                'sisuobjektid',
                                ])

    def gen_piltobjekt_kood(self, gentype='1'):
        """Genereeritakse kood võimalikule uuele piltobjektile.
        gentype - 'A' (genereeritakse tähti) või '1' (genereeritakse arve)
        """
        for n in range(1,1000):
            if gentype == 'A' and n < 27:
                kood = chr(n+64)
            else:
                kood = 'PILT%d' % n
            found = False
            for rcd in self.piltobjektid:
                if rcd.kood == kood:
                    found = True
                    break
            if not found:
                return kood
        return ''

            
    def copy(self, **di):
        map_k = {k.id: k.kood for k in self.kysimused}
        cp = EntityHelper.copy(self, **di)

        map_obj = {}
        for r in self.sisuobjektid:
            cp_r = r.copy()
            cp.sisuobjektid.append(cp_r)
            map_obj[r.id] = cp_r

        self.copy_subrecords(cp, ['kysimused',
                                  'trans',
                                  ])
        
        # kui sisuobjektil ja kysimusel on suhe
        for cp_k in cp.kysimused:
            if cp_k.sisuobjekt_id:
                cp_k.sisuobjekt = map_obj[cp_k.sisuobjekt_id]
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.sisuobjektid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.kysimused:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))

        if not delete:
            # kui on kohalikule serverile pakkimine, siis kaasata ka yhisfailid
            li.extend(self._pack_shared(modified))
            
        return li

    def _pack_shared(self, modified):
        """Lisatakse pakki ühisfailid, kui neid ülesandes on kasutatud.
        """
        from .yhisfail import Yhisfail
        li = []

        if self.sisu:
            for fn in re.findall('src="shared/([^"]+)"', self.sisu):
                t_obj = Yhisfail.get_by_name(fn)
                if t_obj is not None and t_obj not in li:
                    li.extend(t_obj.pack(False, modified))

        for k in self.kysimused:
            for v in k.valikud:
                if v.nimi:
                    for fn in re.findall('src="shared/([^"]+)"', v.nimi):
                        t_obj = Yhisfail.get_by_name(fn)
                        if t_obj is not None and t_obj not in li:
                            li.extend(t_obj.pack(False, modified))

        return li

    @property
    def has_solution(self):
        if self.tyyp == const.INTER_DRAW:
            if self.sisuvaade:
                # näidispilt on sisuvaate väljal
                return True
        for kysimus in self.kysimused:
            t = kysimus.tulemus
            if t and len(t.hindamismaatriksid) > 0:
                return True
        return False

    @property
    def on_sisestatav(self):
        """Kas sisuploki vastuseid on võimalik sisestada või mitte.
        Vastavalt Sirje kirjale 2011-05-13 vabavastusega väljalt vastuseid ei sisestata.
        (nendel juhtudel sisestatakse õige/vale),
        välja arvatud avatud vastusega lünk (JIRA EH-147)
        """
        return self.tyyp in (const.INTER_CHOICE, # Valikvastusega küsimus
                             const.INTER_MATCH2, # Sobitamine
                             const.INTER_MATCH3, # Sobitamine kolme hulgaga
                             const.INTER_MATCH3B, # Sobitamine kolme hulgaga
                             const.INTER_ORDER, # Järjestamine
                             const.INTER_ASSOCIATE, # Seostamine
                             const.INTER_INL_CHOICE, # Valikvastusega lünk
                             const.INTER_GAP, # Pangaga lünk 
                             const.INTER_HOTTEXT, # Tekstiosa valik 
                             const.INTER_GR_GAP, # Piltide lohistamine kujunditele
                             const.INTER_TXGAP, # Tekstide lohistamine kujunditele                             
                             const.INTER_TXASS, # Tekstide seostamine kujunditega  
                             const.INTER_HOTSPOT, # Pildil oleva kujundi valik
                             const.INTER_GR_ORDER, # Järjestamine pildil
                             const.INTER_GR_ASSOCIATE, # Seostamine pildil
                             const.INTER_INL_TEXT, # avatud vastusega lünk
                             const.INTER_MCHOICE, # mitme valikuga tabel
                             )
        
    @property
    def piltobjektid_opt(self):
        return [(v.kood, v.kood) for v in self.piltobjektid]    

    def replace_img_url(self, txt, lang=None):
        """Kui ülesandes on pildid ja nendele lingitakse kireva teksti seest
        kujul images/failinimi.jpg, siis tuleb asendada pildi URL niisuguse URLiga,
        kust saab ülesande ID kätte.
        """
        if txt:
            img_path = Sisuobjekt.get_img_path(self.ylesanne_id, lang=lang)
            # asendame absoluutse urli images/
            txt1 = re.sub(' (src|background)=" *images/', ' \\1="%s/' % img_path, txt)
            # asendame absoluutse urli images_*/
            txt2 = re.sub(r' (src|background)=" *[^"]*images_[^/"]*', ' \\1="%s' % img_path, txt1)
            return txt2

    @property
    def sisukysimused(self):
        """Kysimused, mis on sisu sees, aga mis on ka eraldi kirjetena olemas.
        Kasutatakse remove_unused sees, et leida, millised kysimuste kirjed on vajalikud
        ja mis tuleks kustutada.
        """
        return self.get_sisukysimused()

    def get_sisukysimused(self, pkood=None, lang=None):
        """Kysimused, mis on sisu sees, aga mis on ka eraldi kirjetena olemas.
        Kasutatakse remove_unused sees, et leida, millised kysimuste kirjed on vajalikud
        ja mis tuleks kustutada.
        """
        li = []
        if lang:
            sisu = self.tran(lang).sisu
        else:
            sisu = self.sisu
        if not sisu:
            return li

        if self.tyyp == const.INTER_GAP:
            try:
                sisu, tree = self.parse_sisu(sisu)
            except:
                pass
            else:
                for n, field in enumerate(tree.xpath('//input')):
                    if field.tag == 'input':
                        kood = field.get('value')
                    if pkood and pkood != kood:
                        continue

                    sk = Sisuvalik(id=n, kood=kood, sisuplokk=self)
                    li.append(sk)

        elif self.tyyp == const.INTER_INL_TEXT:
            try:
                sisu, tree = self.parse_sisu(sisu)
            except:
                pass
            else:
                for n, field in enumerate(tree.xpath('//input|//textarea')):
                    if field.tag == 'input':
                        kood = field.get('value')
                    else:
                        kood = field.text
                    if pkood and pkood != kood:
                        continue

                    sk = Sisuvalik(id=n, kood=kood, sisuplokk=self)
                    li.append(sk)

        elif self.tyyp == const.INTER_INL_CHOICE:
            try:
                sisu, tree = self.parse_sisu(sisu)
            except:
                pass
            else:
                for n, field in enumerate(tree.xpath('//select')):
                    kood = field.get('id') or field.get('name')
                    if not kood:
                        label = field.find('option')
                        kood = label is not None and label.text and label.text.strip()
                    if pkood and pkood != kood:
                        continue

                    sk = Sisuvalik(id=n, kood=kood, sisuplokk=self)
                    n = 0
                    for o in field.iterdescendants('option'):
                        if o.get('value'):
                            n += 1
                            sv = Sisuvalik(id=n, kood=o.get('value'), sisuplokk=self, nimi=o.text)
                            sk.valikud.append(sv)
                    li.append(sk)
        return li

    @property
    def tyyp_nimi(self):
        "Nimetus eesti keeles"
        opt = usersession.get_opt()
        return opt.get_name('interaction_block', self.tyyp) or \
               opt.get_name('interaction', self.tyyp) or \
               opt.get_name('interaction_output', self.tyyp)

    @property
    def type_name(self):
        """Koodnimi klasside nimetamisel.
        Kui self.is_qti_interaction == True, 
        siis on koodnimeks QTI elemendi nimi,
        välja arvatud positionTextInteraction, mille QTI nimi on positionObjectInteraction
        """
        return const.block_names.get(self.tyyp)

    @property
    def type_name_qti(self):
        """QTI tyybinimi (kui on interaction)
        """
        if self.tyyp == const.INTER_TXPOS:
            stype = 'positionObjectInteraction'
        elif self.is_qti_interaction:
            stype = self.type_name
        else:
            stype = 'customInteraction'
        return stype

    def get_prefix(self):
        "Sisuploki HTML elementides kasutatav prefiks"
        return 'b%s' % (self.id)

    def get_result(self):
        "Sisuploki vastuste välja ID (ei või olla suurtähti)"
        return '%s_result' % (self.get_prefix())

    #def get_lresult(self):
    #    return '%s_lresult' % (self.get_prefix())
    
    def post_create(self):
        if self.is_interaction_graphic:
            self.give_taustobjekt()
        elif self.tyyp == const.INTER_HOTTEXT:
            pass
        elif self.tyyp == const.INTER_COLORTEXT:
            pass
        elif self.tyyp == const.INTER_PUNKT:
            # teeme valikuhulga
            self.give_baaskysimus(seq=1)
        elif self.tyyp == const.INTER_GAP:
            bkysimus = self.give_kysimus(0, default_kood='X')
            bkysimus.selgitus = _("Määramata ala")
            bkysimus.max_vastus = 1
            bkysimus.kardinaalsus = const.CARDINALITY_MULTIPLE
        elif self.tyyp in (const.INTER_TEXT,
                           const.INTER_EXT_TEXT,
                           const.INTER_MATH,
                           const.INTER_WMATH,
                           const.INTER_SLIDER):
            self.give_kysimus()
        elif self.tyyp == const.BLOCK_MATH:
            obj = self.give_taustobjekt() # MathML jaoks
            obj.filename = None
            obj.mimetype = 'application/xhtml+xml'
        elif self.tyyp == const.INTER_TXPOS2:
            self.give_baaskysimus(1, True)
            self.give_baaskysimus(2, True)
        if self.tyyp == const.INTER_MATCH2:
            # teeme valikuhulgad
            self.give_baaskysimus(seq=1)
            self.give_baaskysimus(seq=2)
        elif self.tyyp == const.INTER_MATCH3:
            # teeme valikuhulgad
            self.give_kysimus(1)
            self.give_kysimus(2)
            self.give_kysimus(3)
        elif self.tyyp == const.INTER_MATCH3A:
            # teeme valikuhulgad
            self.give_baaskysimus(1, pseudo=True)
            self.give_baaskysimus(2, pseudo=True)
            self.give_baaskysimus(3, pseudo=True)
        elif self.tyyp == const.INTER_MATCH3B:
            # teeme valikuhulgad
            self.give_baaskysimus(1, pseudo=True)
            self.give_baaskysimus(2, pseudo=True)
            self.give_baaskysimus(3, pseudo=True)
        elif self.tyyp == const.INTER_MCHOICE:
            # teeme valikuhulga
            self.give_baaskysimus(seq=1)
        elif self.is_block:
            if self.tyyp == const.BLOCK_IMAGE:
                self.staatus = 0 # pilti algselt ei kuvata
            elif self.tyyp == const.BLOCK_CUSTOM:
                pass
            elif self.tyyp == const.BLOCK_MEDIA:
                pass
        elif self.tyyp == const.INTER_GEOGEBRA:
            self.give_meediaobjekt()
        elif self.tyyp == const.INTER_DESMOS:
            self.give_meediaobjekt()            
        elif self.tyyp == const.INTER_AUDIO:
            kysimus = self.kysimus
            kysimus.naita_play = True
        elif self.tyyp == const.BLOCK_GOOGLECHARTS:
            self.give_meediaobjekt()                        


    def louend_pos(self, lang, drag_images):
        """Arvutame lohistatavate piltide algsed asukohad lõuendil
        ja lõuendi suuruse
        """
        pos = {} # asukohad
        mo = self.taustobjekt
        dx = 5 # vahe piltide vahel
        dy = 3 # vahe piltide vahel 
        dx0 = 35 # vahe tausta ja piltide vahel, kui pildid on kõrval
        dy0 = 35 # vahe tausta ja piltide vahel, kui pildid on all
        taust_laius = mo.laius or 100
        taust_korgus = mo.korgus or 100
        taust_x = taust_y = 0

        if not drag_images:
            return pos, taust_laius, taust_korgus, taust_x, taust_y
    
        piltobjektid = list(self.piltobjektid)
        if mo.segamini:
            # ajame järjekorra sassi
            random.shuffle(piltobjektid)

        if mo.asend in (Sisuobjekt.ASEND_ALL, Sisuobjekt.ASEND_YLEVAL):
            # pildid kuvada tausta all või ylal
            x = 0
            if mo.asend == Sisuobjekt.ASEND_YLEVAL:
                y = 0
            else:
                y = taust_korgus + dy0
            max_korgus = 0

            for item in piltobjektid:
                item_korgus = item.tran(lang).korgus or item.korgus or 0
                item_laius = item.tran(lang).laius or item.laius or 0
                if x > 0 and x + item_laius > taust_laius:
                    # alustame uut rida
                    y += max_korgus + dy
                    x = 0
                    max_korgus = 0
                for seq in range(item.max_vastus or 1):
                    # lisame jooksvasse ritta
                    pos[item.id, seq] = x, y
                    max_korgus = max(max_korgus, item_korgus)
                x += item_laius + dx

            louend_laius = taust_laius
            if mo.asend == Sisuobjekt.ASEND_YLEVAL:
                taust_y = y + max_korgus + dy0
                louend_korgus = taust_y + taust_korgus
            else:
                louend_korgus = y + max_korgus
        else:
            # pildid kuvada taustast paremal või vasakul
            
            y = 0
            if mo.asend == Sisuobjekt.ASEND_VASAKUL:
                x = 0
            else:
                x = taust_laius + dx0
            max_laius = 0
            for item in piltobjektid:
                item_korgus = item.tran(lang).korgus or item.korgus or 0
                item_laius = item.tran(lang).laius or item.laius or 0
                cnt = item.max_vastus or 1
                for seq in range(cnt):
                    if seq == 0 or item.eraldi:
                        if y > 0 and y + item_korgus > taust_korgus:
                            # alustame uut tulpa
                            x += max_laius + dx
                            y = 0
                            max_laius = 0
                    # lisame jooksvasse tulpa
                    pos[item.id, seq] = x, y
                    if seq == cnt - 1 or item.eraldi:
                        max_laius = max(max_laius, item_laius)
                        y += item_korgus + dy

            louend_korgus = taust_korgus
            if mo.asend == Sisuobjekt.ASEND_VASAKUL:
                taust_x = x + max_laius + dx0
                louend_laius = taust_x + taust_laius
            else: 
                louend_laius = x + max_laius
            
        return pos, louend_laius, louend_korgus, taust_x, taust_y
    
    def give_taustobjekt(self):
        """Ploki põhiline objekt
        """
        if self.taustobjekt:
            return self.taustobjekt
        else:
            taustobjekt = Taustobjekt(seq=0, sisuplokk=self)
            self.sisuobjektid.append(taustobjekt)
            return taustobjekt

    def give_meediaobjekt(self):
        """Ploki põhiline objekt
        """
        if self.meediaobjekt:
            return self.meediaobjekt
        else:
            meediaobjekt = Meediaobjekt(seq=0, sisuplokk=self)
            self.sisuobjektid.append(meediaobjekt)
            return meediaobjekt
    
    def give_piltobjekt(self, seq, create=False, kood=None):
        for item in self.piltobjektid:
            if kood and item.kood == kood or not kood and item.seq == seq:
                return item
        if create:
            item = Piltobjekt(seq=seq, kood=kood, sisuplokk=self)
            self.sisuobjektid.append(item)
            return item

    @property
    def kysimus(self):
        return self.give_kysimus()

    @property
    def pariskysimused(self):
        return [k for k in self.kysimused if k.kood]

    def give_baaskysimus(self, seq=None, pseudo=False):
        """Leitakse valikuhulk (mis ei ole sisuliselt küsimus ega hinnatav)
        """
        kysimus = self.get_baaskysimus(seq)
        if not kysimus:
            # ei leitud
            kysimus = Kysimus(seq=seq or 0, kood=None, sisuplokk=self)
            self.kysimused.append(kysimus)
            if pseudo:
                kysimus.pseudo = True
        return kysimus       

    def get_baaskysimus(self, seq=0):
        for kysimus in self.kysimused:
            if kysimus.kood is None:
                if not seq or seq == kysimus.seq:
                    return kysimus
        
    def give_kysimus(self, seq=None, kood=None, default_kood=None):
        """Leitakse valikuhulk. Kui pole, siis soovi korral luuakse.
        """
        kysimus = None
        for tk in self.kysimused:
            if kood is not None:
                if kood == tk.kood:
                    kysimus = tk
                    break
                continue
            if seq is None or tk.seq == seq:
                # soovitakse esimest lahtrit
                # soovitakse antud seq-ga lahtrit
                kysimus = tk
                break

        if not kysimus:
            # ei leitud
            kysimus = Kysimus(seq=seq, kood=kood, sisuplokk=self)
            kysimus.gen_kood(default_kood)
        #log.debug('give_kysimus seq=%s kood=%s' % (kysimus.seq, kysimus.kood))
        return kysimus

    def get_kysimus(self, kood=None, seq=None):
        for kysimus in self.kysimused:
            if kood is None and seq is None:
                return kysimus
            elif seq is not None and kysimus.seq == seq:
                return kysimus
            elif seq == 0 and kysimus.seq is None:
                return kysimus                        
            elif kood and kysimus.kood == kood:
                return kysimus

    def correct_responses(self, yv, lang=None, responses=None, e_locals=None, hindaja=False, naidistega=True, as_tip=False):
        "Leiame õiged vastused"
        # lang - soorituskeel
        # responses - dict seniste vastustega, kuhu sisse vastused pannakse
        # e_locals - dict seniste vastustega, kuhu sisse vastused pannakse
        # hindaja - kas kasutaja on hindaja

        #from eis.model.eksam import TempKysimusevastus
        from eis.lib.blockresponse import MemKS, MemKV
        from .hindamismaatriks import fstr
        if responses is None:
            responses = dict()
        if e_locals is None:
            e_locals = dict()

        def set_numvalue(value, k, t, e_locals):
            if k.kood in e_locals:
                # ei kirjuta yle juba antud vastuseid, kui nende põhjal arvutatakse
                return
            if value is not None and value != '':
                if t.baastyyp == const.BASETYPE_FLOAT:
                    e_locals[k.kood] = float(value.replace(',','.'))
                else:
                    e_locals[k.kood] = int(value)                        
            else:
                e_locals[k.kood] = None

        def numvalue(entry, k, t, e_locals):
            if t.baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT):
                value, tip = entry.num_kood1(e_locals, lang=lang, valem=t.valem)
                if k.kood not in e_locals:
                    # ei kirjuta yle juba antud vastuseid, kui nende põhjal arvutatakse
                    e_locals[k.kood] = value
                if as_tip:
                    return tip
                if value is not None:
                    value = fstr(value)
            else:
                value = entry.tran(lang).kood1
            return value

        def numvalue_none(k, t, e_locals):
            """Seame None väärtuseks küsimusele, mille õiget vastust hindamismaatriksis ei ole,
            et küsimuse muutuja oleks olemas ja seda saaks valemites kasutada (K==None)
            """
            if k.kood in e_locals:
                return
            if t.baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT):
                e_locals[k.kood] = None
        
        if self.tyyp == const.INTER_CHOICE:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                entries = k.correct_entries()
                for seq, entry in enumerate(entries):
                    value = entry.tran(lang).kood1
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING, kood1=value,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_MCHOICE:
            for k in self.pariskysimused:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    for seq, entry in enumerate(k.correct_entries()):
                        value = entry.tran(lang).kood1
                        kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER, kood1=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_ORDER:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                jarjestus = [entry.kood1 for entry in k.correct_entries()]
                kv.set_kvsisu(1, const.RTYPE_ORDERED, jarjestus=jarjestus,
                              oige=True,
                              toorpunktid=t.max_pallid)

        elif self.tyyp == const.INTER_MATCH2:
            valikuhulk1 = self.get_baaskysimus(1)
            max_vastus = valikuhulk1.max_vastus
            kvsisud = []
            for k in self.pariskysimused:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    for seq, entry in enumerate(k.correct_entries()):
                        value = entry.tran(lang).kood1
                        kvs = kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER, kood1=value,
                                            oige=True,
                                            hindamismaatriks_id=entry.id,
                                            toorpunktid=entry.pallid)
                        kvsisud.append((kv, kvs, entry.pallid))
            if max_vastus:
                # kui on antud sisuploki max vastuste arv, siis vajadusel eemaldame mõned
                kvsisud.sort(key=lambda x: 0-x[2])
                while max_vastus < len(kvsisud):
                    kv, kvs, pallid = kvsisud.pop()
                    kv.kvsisud.remove(kvs)
                
        elif self.tyyp == const.INTER_MATCH3:
            entries = []
            # vana sobitamine
            k1 = self.get_kysimus(seq=1)
            k2 = self.get_kysimus(seq=2)
            k3 = self.get_kysimus(seq=3)
            t = k1.tulemus
            responses[k1.kood] = kv = MemKV.init_k(self, k1)
            kv._current_seq = -1
            for seq, entry in enumerate(k1.correct_entries()):
                entries.append((kv, entry))

            # kui on antud sisuploki max vastuste arv, siis vajadusel eemaldame mõned
            max_vastus = k1.max_vastus
            max_vastus2 = k2.max_vastus
            max_vastus3 = k3.max_vastus
            entries.sort(key=lambda x: 0-x[1].pallid)

            cnt = cnt2 = cnt3 = 0
            for kv, entry in entries:
                if max_vastus and max_vastus < cnt + 1:
                    break
                if entry.maatriks == 1 and max_vastus2 and max_vastus2 < cnt2 + 1:
                    continue
                if entry.maatriks == 2 and max_vastus3 and max_vastus3 < cnt3 + 1:
                    continue
                cnt += 1
                if entry.maatriks == 1:
                    cnt2 += 1
                else:
                    cnt3 += 1

                # vana
                kv._current_seq += 1
                kvs = kv.set_kvsisu(kv._current_seq,
                                    const.RTYPE_PAIR,
                                    kood1=entry.kood1,
                                    kood2=entry.kood2,
                                    maatriks=entry.maatriks,
                                    oige=True,
                                    hindamismaatriks_id=entry.id,
                                    toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_MATCH3A:
            entries = []
            # uus sobitamine
            for k in self.pariskysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                kv._current_seq = -1
                for seq, entry in enumerate(k.correct_entries()):
                    entries.append((kv, entry))

            # kui on antud sisuploki max vastuste arv, siis vajadusel eemaldame mõned
            k1 = self.get_kysimus(seq=1)
            k2 = self.get_kysimus(seq=2)
            k3 = self.get_kysimus(seq=3)
            max_vastus = k1.max_vastus
            max_vastus2 = k2.max_vastus
            max_vastus3 = k3.max_vastus
            entries.sort(key=lambda x: 0-x[1].pallid)

            cnt = cnt2 = cnt3 = 0
            for kv, entry in entries:
                if max_vastus and max_vastus < cnt + 1:
                    break
                if entry.maatriks == 1 and max_vastus2 and max_vastus2 < cnt2 + 1:
                    continue
                if entry.maatriks == 2 and max_vastus3 and max_vastus3 < cnt3 + 1:
                    continue
                cnt += 1
                if entry.maatriks == 1:
                    cnt2 += 1
                else:
                    cnt3 += 1
                # uus
                value = entry.tran(lang).kood1
                kv._current_seq += 1
                kvs = kv.set_kvsisu(kv._current_seq,
                                    const.RTYPE_IDENTIFIER,
                                    kood1=entry.kood1,
                                    oige=True,
                                    maatriks=entry.maatriks,
                                    hindamismaatriks_id=entry.id,
                                    toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_MATCH3B:
            entries = []
            for k in self.pariskysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                kv._current_seq = -1
                for seq, entry in enumerate(k.correct_entries()):
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq,
                                  const.RTYPE_PAIR,
                                  kood1=entry.kood1,
                                  kood2=entry.kood2,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)
                    break

        elif self.tyyp == const.INTER_ASSOCIATE:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                entries = k.correct_entries()
                for seq, entry in enumerate(entries):
                    kv.set_kvsisu(seq,
                                  const.RTYPE_PAIR,
                                  kood1=entry.kood1,
                                  kood2=entry.kood2,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_TEXT:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                entries = k.correct_entries()
                for seq, entry in enumerate(entries):
                    value = numvalue(entry, k, t, e_locals)
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING, sisu=value,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)
                if not entries:
                    numvalue_none(k, t, e_locals)

        elif self.tyyp == const.INTER_EXT_TEXT:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                naidisvastus = t.tran(lang).naidisvastus

                # bugzilla 770 - ei kuva näidisvastust hindajale
                if naidisvastus and t.naidis_naha and naidistega:                    
                    # kui näidisvastus on olemas ja olen hindaja või on lubatud näidata lahendajale,
                    # siis kuvame näidisvastuse, muidu hindamismaatriksi vastuse
                    if not k.rtf:
                        # näidata lihttekstina
                        naidisvastus = utils.html2plain(naidisvastus)
                    # näidisvastuseid on yksainus, kui ka vastuseid võib olla mitu
                    kv.set_kvsisu(1, const.RTYPE_STRING, sisu=naidisvastus,
                                  oige=True)
                else:
                    if t.baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT):
                        responded = []
                        for entry in k.correct_entries():
                            value, tip = entry.num_kood1(e_locals, valem=t.valem)
                            if as_tip:
                                responded.append(tip)
                            else:
                                responded.append(fstr(value))
                    else:
                        responded = [entry.tran(lang).kood1 for entry in k.correct_entries()]
                    entries = k.correct_entries()
                    for seq, entry in enumerate(entries):
                        value = numvalue(entry, k, t, e_locals)
                        kv.set_kvsisu(seq+1, const.RTYPE_STRING, sisu=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)
                    if not entries:
                        numvalue_none(k, t, e_locals)
                    
        elif self.tyyp == const.INTER_INL_TEXT:
            for k in self.kysimused:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    entries = k.correct_entries()
                    for seq, entry in enumerate(entries):
                        value = numvalue(entry, k, t, e_locals)
                        kv.set_kvsisu(seq+1, const.RTYPE_STRING, sisu=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)
                    if not entries:
                        numvalue_none(k, t, e_locals)
                    
        elif self.tyyp == const.INTER_INL_CHOICE:
            for k in self.kysimused:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    for seq, entry in enumerate(k.correct_entries()):
                        value = entry.tran(lang).kood1
                        kv.set_kvsisu(seq+1, const.RTYPE_STRING, kood1=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_GAP:
            bkysimus = self.give_kysimus(0)
            gap_lynkadeta = bkysimus.gap_lynkadeta
            for k in self.kysimused:
                if k != bkysimus:
                    t = k.tulemus
                    if t:
                        responses[k.kood] = kv = MemKV.init_k(self, k)
                        for seq, entry in enumerate(k.correct_entries()):
                            value = entry.tran(lang).kood1
                            sisu = gap_lynkadeta and k.seq or None
                            kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER, kood1=value, sisu=sisu,
                                          oige=True,
                                          hindamismaatriks_id=entry.id,
                                          toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_PUNKT:
            for k in self.pariskysimused:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    entries = k.correct_entries()
                    for seq, entry in enumerate(entries):
                        value = numvalue(entry, k, t, e_locals)
                        # lynga jrk
                        lseq = entry.koordinaadid
                        if not lseq:
                            # sisuploki vormil salvestamata, jrk juurde panemata
                            continue
                        kv.set_kvsisu(seq+1, const.RTYPE_POSSTRING,
                                      sisu=entry.kood1, # vastuse tekst
                                      koordinaat=lseq, # lynga jrk
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)
                    if not entries:
                        numvalue_none(k, t, e_locals)
                    
        elif self.tyyp == const.INTER_HOTTEXT:
            for k in self.kysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    value = entry.tran(lang).kood1
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING,
                                  kood1=value,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                  
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_COLORTEXT:
            for k in self.kysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kood1 = entry.tran(lang).kood1
                    kood2 = entry.tran(lang).kood2
                    kv.set_kvsisu(seq+1, const.RTYPE_PAIR,
                                  kood1=kood1,
                                  kood2=kood2,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                  
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_MATH:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    for seq, entry in enumerate(k.correct_entries()):
                        value = entry.tran(lang).kood1
                        kv.set_kvsisu(seq+1, const.RTYPE_STRING,
                                      sisu=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,                                      
                                      toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_WMATH:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                if t:
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                    for seq, entry in enumerate(k.correct_entries()):
                        value = entry.tran(lang).kood1
                        kv.set_kvsisu(seq+1, const.RTYPE_STRING,
                                      sisu=value,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,                                      
                                      toorpunktid=entry.pallid)
        
        elif self.tyyp == const.INTER_SLIDER:
            k = self.kysimus
            if k.kood:
                t = k.tulemus                
                responses[k.kood] = kv = MemKV.init_k(self, k)
                entries = k.correct_entries()
                for seq, entry in enumerate(entries):
                    value = numvalue(entry, k, t, e_locals)
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING, sisu=value,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)
                    break
                if not entries:
                    numvalue_none(k, t, e_locals)
                        
        elif self.tyyp == const.INTER_POS:
            for k in self.kysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_POINT,
                                  punkt=(entry.cx, entry.cy),
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                  
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_POS2:
            prkkysimus = self.get_baaskysimus(1)
            piirkonnad = {v.kood: v for v in prkkysimus.valikud}            
            for k in self.pariskysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    # leiame koodile vastava piirkonna
                    prk_kood = entry.kood1
                    prk = piirkonnad.get(prk_kood)
                    if prk:
                        cx, cy = prk.cx, prk.cy
                        kv.set_kvsisu(seq+1, const.RTYPE_POINT,
                                      punkt=(cx, cy),
                                      oige=True,
                                      hindamismaatriks_id=entry.id,
                                      toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_TXPOS:
            # leiame sisuploki kõigi kysimuste õiged vastused
            bkysimus = self.kysimus
            sp_res = []
            for k in self.pariskysimused:
                for seq, entry in enumerate(k.correct_entries()):
                    sp_res.append((k, entry))
            # järjestame kõigi kysimuste vastused nii, et oiged ja suuremad punktid eespool
            sp_res.sort(key=lambda r: (r[1].oige, r[1].pallid), reverse=True)
            # kui sisuploki vastuste arvul on piirang, siis jätame alles ainult lubatud arvu vastuseid
            if bkysimus.max_vastus:
                sp_res = sp_res[:bkysimus.max_vastus]
            for (k, entry) in sp_res:
                kv = responses.get(k.kood)
                if kv is None:
                    t = k.tulemus
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                seq = len(kv.kvsisud)
                kv.set_kvsisu(seq+1, const.RTYPE_POINT,
                              punkt=(entry.cx, entry.cy),
                              oige=True,
                              hindamismaatriks_id=entry.id,                                  
                              toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_TXPOS2:
            # leiame sisuploki kõigi kysimuste õiged vastused
            bkysimus = self.get_baaskysimus(1)
            prkkysimus = self.get_baaskysimus(2)
            piirkonnad = {v.kood: v for v in prkkysimus.valikud}
            sp_res = []
            for k in self.pariskysimused:
                for seq, entry in enumerate(k.correct_entries()):
                    sp_res.append((k, entry))
            # järjestame kõigi kysimuste vastused nii, et oiged ja suuremad punktid eespool
            sp_res.sort(key=lambda r: (r[1].oige, r[1].pallid), reverse=True)
            # kui sisuploki vastuste arvul on piirang, siis jätame alles ainult lubatud arvu vastuseid
            if bkysimus.max_vastus:
                sp_res = sp_res[:bkysimus.max_vastus]
            for (k, entry) in sp_res:
                kv = responses.get(k.kood)
                if kv is None:
                    t = k.tulemus
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                seq = len(kv.kvsisud)

                # leiame koodile vastava piirkonna
                prk_kood = entry.kood1
                prk = piirkonnad.get(prk_kood)
                if prk:
                   cx, cy = prk.cx, prk.cy
                   kv.set_kvsisu(seq+1, const.RTYPE_POINT,
                                 punkt=(cx, cy),
                                 oige=True,
                                 hindamismaatriks_id=entry.id,                                  
                                 toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_TXGAP:
            bkysimus = self.get_baaskysimus(1)
            prkkysimus = self.get_baaskysimus(2)
            sp_res = []
            for k in self.pariskysimused:
                for seq, entry in enumerate(k.correct_entries()):
                    sp_res.append((k, entry))
            # järjestame kõigi kysimuste vastused nii, et oiged ja suuremad punktid eespool
            sp_res.sort(key=lambda r: (r[1].oige, r[1].pallid), reverse=True)
            # kui sisuploki vastuste arvul on piirang, siis jätame alles ainult lubatud arvu vastuseid
            if bkysimus.max_vastus:
                sp_res = sp_res[:bkysimus.max_vastus]
            for (k, entry) in sp_res:
                kv = responses.get(k.kood)
                if kv is None:
                    t = k.tulemus
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                seq = len(kv.kvsisud)

                # leiame koodile vastava piirkonna
                prk_kood = entry.kood1
                hotspot = prkkysimus.get_valik(prk_kood)                 
                kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER,
                              kood1=prk_kood,
                              oige=True,
                              punkt=(hotspot.cx, hotspot.cy),
                              hindamismaatriks_id=entry.id,
                              toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_TXASS:
            bkysimus = self.get_baaskysimus(1)
            prkkysimus = self.get_baaskysimus(2)
            sp_res = []
            for k in self.pariskysimused:
                for seq, entry in enumerate(k.correct_entries()):
                    sp_res.append((k, entry))
            # järjestame kõigi kysimuste vastused nii, et oiged ja suuremad punktid eespool
            sp_res.sort(key=lambda r: (r[1].oige, r[1].pallid), reverse=True)
            # kui sisuploki vastuste arvul on piirang, siis jätame alles ainult lubatud arvu vastuseid
            if bkysimus.max_vastus:
                sp_res = sp_res[:bkysimus.max_vastus]
            for (k, entry) in sp_res:
                kv = responses.get(k.kood)
                if kv is None:
                    t = k.tulemus
                    responses[k.kood] = kv = MemKV.init_k(self, k)
                seq = len(kv.kvsisud)

                # leiame koodile vastava piirkonna
                prk_kood = entry.kood1
                hotspot = prkkysimus.get_valik(prk_kood)                 
                kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER,
                              kood1=prk_kood,
                              oige=True,
                              punkt=(hotspot.cx, hotspot.cy),
                              hindamismaatriks_id=entry.id,
                              toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_GR_GAP:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    hotspot = k.get_valik(entry.kood2) 
                    kv.set_kvsisu(seq+1, const.RTYPE_PAIR,
                                  kood1=entry.kood1,
                                  kood2=entry.kood2,
                                  punkt=(hotspot.cx, hotspot.cy),
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                  
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_HOTSPOT:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER,
                                  kood1=entry.kood1,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                  
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_GR_ORDER:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                jarjestus = [entry.kood1 for entry in k.correct_entries()]
                kv.set_kvsisu(1, const.RTYPE_ORDERED, jarjestus=jarjestus,
                              oige=True,
                              toorpunktid=t and t.max_pallid)                

        elif self.tyyp == const.INTER_GR_ORDASS:
            # võrguylesanne
            # valevastuste loenduriga pildil seostamine
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                jarjestus = [entry.kood1 for entry in k.correct_entries()]
                kv.set_kvsisu(1, const.RTYPE_ORDERED, jarjestus=jarjestus,
                              oige=True,
                              toorpunktid=t.max_pallid)

        elif self.tyyp == const.INTER_SELECT:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_COORDS,
                                  punkt=(entry.cx, entry.cy),
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                              
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_SELECT2:
            prkkysimus = self.get_baaskysimus(1)
            piirkonnad = {v.kood: v for v in prkkysimus.valikud}
            k = self.get_kysimus(seq=2)
            t = k.tulemus
            responses[k.kood] = kv = MemKV.init_k(self, k)
            for seq, entry in enumerate(k.correct_entries()):
                # leiame koodile vastava piirkonna
                prk_kood = entry.kood1
                prk = piirkonnad.get(prk_kood)
                if prk:
                   cx, cy = prk.cx, prk.cy
                   kv.set_kvsisu(seq+1, const.RTYPE_COORDS,
                                 punkt=(cx, cy),
                                 oige=True,
                                 hindamismaatriks_id=entry.id,                                  
                                 toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_GR_ASSOCIATE:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_PAIR,
                                  kood1=entry.kood1,
                                  kood2=entry.kood2,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                              
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_COLORAREA:
            #k0 = self.get_baaskysimus()
            for k in self.pariskysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_IDENTIFIER,
                                  kood1=entry.kood1,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,                                                                
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_UNCOVER:
            for k in self.pariskysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING,
                                  sisu=entry.kood1,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_DRAW:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                if k.tulemus:
                    # arvutihinnatav õige vastus
                    for seq, entry in enumerate(k.correct_entries()):
                        koordinaadid = entry.koordinaadid
                        try:
                            koordinaadid = json.loads(koordinaadid)
                        except Exception as ex:
                            log.error(ex)
                            koordinaadid = []
                        kv.set_kvsisu(seq+1, const.RTYPE_COORDS,
                                      koordinaadid=koordinaadid,
                                      kujund=entry.kujund,
                                      oige=True,
                                      hindamismaatriks_id=entry.id,                                      
                                      toorpunktid=entry.pallid)
                else:
                    # mittehinnatav näidisvastus skriptina
                    kv.set_kvsisu(1, const.RTYPE_STRING,
                                  sisu=self.sisuvaade,
                                  oige=True)

        elif self.tyyp == const.INTER_TRAIL:
            k = self.kysimus
            if k.kood:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING,
                                  sisu=entry.kood1,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.INTER_CROSSWORD:
            for k in self.kysimused:
                t = k.tulemus
                responses[k.kood] = kv = MemKV.init_k(self, k)
                for seq, entry in enumerate(k.correct_entries()):
                    value = entry.tran(lang).kood1
                    kv.set_kvsisu(seq+1, const.RTYPE_STRING, sisu=value,
                                  oige=True,
                                  hindamismaatriks_id=entry.id,
                                  toorpunktid=entry.pallid)

        elif self.tyyp == const.BLOCK_RANDOM:
            for k in self.kysimused:
                kv = yv and yv.get_responses().get(k.kood) 
                if kv:
                    responses[k.kood] = kv
                    t = k.tulemus
                    for ks in kv.kvsisud:
                        value = ks.sisu
                        set_numvalue(value, k, t, e_locals)
                
        elif self.tyyp == const.INTER_AUDIO:
            pass
        elif self.tyyp == const.INTER_UPLOAD:
            pass
                
        return responses, e_locals

    def count_tahemargid(self, lang):
        """Loetakse kokku sisuplokis olevad tähemärgid suurematelt tekstiväljadelt
        (küsimus või tööjuhend, tehniline töökäsk, alusteksti ja lünkteksti sisu,
        valikvastuste sisu, hindamismaatriksis oleva vastuse tekst),
        et selle põhjal saaks arvestada toimetajate ja tõlkijate töötasu.
        """
        cch = CountChar(self.ylesanne.lang, lang)
        
        def _len_hm():
            "Sisuploki kysimuste hindamismaatriksite tähtede lugemine"
            total = 0
            for kysimus in self.kysimused:
                tulemus = kysimus.tulemus
                if tulemus:
                    tr1 = tulemus.tran(lang, False)
                    if tr1:
                        total += cch.count(tr1.naidisvastus, kysimus.rtf)
                    for hm in tulemus.hindamismaatriksid:
                        tr1 = hm.tran(lang, False)
                        if tr1:
                            total += cch.count(tr1.kood1, kysimus.rtf)
            return total

        def _len_v():
            "Sisuploki kysimuste valikute tähtede lugemine"
            total = 0
            for kysimus in self.kysimused:
                for valik in kysimus.valikud:
                    tr1 = valik.tran(lang, False)
                    if tr1:
                        if not isinstance(valik, Valikupiirkond):
                            # valikupiirkonna puhul on nimi asemel koordinaadid, mille tähti ei loeta
                            total += cch.count(tr1.nimi, kysimus.rtf)
            return total
        
        total = 0
        tr = self.tran(lang, False)
        if tr:
            if tr.nimi:
                total += cch.count(tr.nimi, False)
            if tr.tehn_tookask:
                total += cch.count(tr.tehn_tookask, False)

            if self.tyyp == const.BLOCK_RUBRIC:
                total += cch.count(tr.sisu, True)
            elif self.tyyp == const.BLOCK_HEADER:
                total += cch.count(tr.sisu, False)
            elif self.tyyp == const.BLOCK_IMAGE:
                pass
            elif self.tyyp == const.BLOCK_MEDIA:
                pass
            elif self.tyyp == const.BLOCK_CUSTOM:
                pass
            elif self.tyyp == const.BLOCK_MATH:
                total += cch.count(tr.sisu, False)
            elif self.tyyp == const.BLOCK_WMATH:
                total += cch.count(tr.sisu, False)

            elif self.tyyp in (const.INTER_CHOICE,
                               const.INTER_MCHOICE,
                               const.INTER_ORDER,
                               const.INTER_MATCH2,
                               const.INTER_MATCH3,
                               const.INTER_MATCH3B,
                               const.INTER_ASSOCIATE):
                total += _len_v()

            elif self.tyyp in (const.INTER_TEXT,
                               const.INTER_EXT_TEXT):
                total += _len_hm()

            elif self.tyyp == const.INTER_INL_TEXT:
                total += cch.count(tr.sisu, True)
                total += _len_hm()

            elif self.tyyp == const.INTER_INL_CHOICE:
                # kireva teksti valikvälja tõttu on vaja lugeda sisuvaade
                total += cch.count(tr.sisuvaade, True)
                total += _len_v()
                
            elif self.tyyp == const.INTER_GAP:
                total += cch.count(tr.sisu, True)
                total += _len_v()
            
            elif self.tyyp == const.INTER_PUNKT:
                total += _len_v()
                
            elif self.tyyp == const.INTER_HOTTEXT:
                total += cch.count(tr.sisu, True)

            elif self.tyyp == const.INTER_COLORTEXT:
                total += cch.count(tr.sisu, True)

            # elif self.tyyp == const.INTER_MATH:
            #     pass
            
            # elif self.tyyp == const.INTER_SLIDER:
            #     pass

            # elif self.tyyp == const.INTER_POS:
            #     pass
            
            elif self.tyyp == const.INTER_TXPOS:
                total += _len_v()
                
            elif self.tyyp == const.INTER_TXPOS2:
                total += _len_v()                

            elif self.tyyp == const.INTER_TXGAP:
                total += _len_v()
                
            elif self.tyyp == const.INTER_TXASS:
                total += _len_v()                                
                
            # elif self.tyyp == const.INTER_GR_GAP:
            #     pass
            
            # elif self.tyyp == const.INTER_TRAIL:
            #     pass
            
            # elif self.tyyp == const.INTER_HOTSPOT:
            #     pass

            # elif self.tyyp == const.INTER_GR_ORDER:
            #     pass
            
            # elif self.tyyp == const.INTER_SELECT:
            #     pass
            
            # elif self.tyyp == const.INTER_GR_ASSOCIATE:
            #     pass
            
            # elif self.tyyp == const.INTER_GR_ORDASS:
            #     pass
            
            # elif self.tyyp == const.INTER_DRAW:
            #     pass
            
            # elif self.tyyp == const.INTER_AUDIO:
            #     pass
            
            # elif self.tyyp == const.INTER_UPLOAD:
            #     pass
            
            # elif self.tyyp == const.INTER_GEOGEBRA:
            #     pass
            
            # elif self.tyyp == const.BLOCK_GOOGLECHARTS:
            #     pass
            
            elif self.tyyp == const.INTER_CROSSWORD:
                total += _len_hm()
                
            elif self.tyyp == const.INTER_COLORAREA:
                total += _len_v()
                
            elif self.tyyp == const.INTER_UNCOVER:
                # sisus pickle: etteantud osad ja vastuse osa
                pass
            
            elif self.tyyp == const.BLOCK_FORMULA:
                # arvutatud väärtuse valemi tähti ei loe
                pass
                
            tr.tahemargid = total

        return total
