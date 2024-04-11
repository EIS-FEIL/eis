"Klassifikaatorid"

import mimetypes
from webhelpers2.html.tags import OptGroup, Option
from .entityhelper import *
from .klassifikaator import Klrida, cache, cache_kood, cache_id
from .kasutaja import Kasutaja, Kasutajagrupp, Kasutajaoigus
import eiscore.i18n as i18n
_ = i18n._

class Opt(object):   
    """Kasutajaliidese valiklahtrite valikud
    Atribuudid on kujul KLASSIFIKAATOR[_id][_empty], kus
    KLASSIFIKAATOR - klassifikaator.kood
    id - tähendab, et tagastatakse [(id,nimi),...]
         muidu tagastatakse [(kood, nimi),...]
    empty - tähendab, et lisatakse tühi valik
    """

    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        
    @property
    def interactions(self):
        return {
            const.BLOCK_RUBRIC: _("Alustekst"),
            const.BLOCK_IMAGE: _("Pilt"),
            const.BLOCK_MEDIA: _("Multimeedia"),
            const.BLOCK_CUSTOM: _("Muu fail"),
            const.BLOCK_MATH: _("Matemaatiline tekst"),
            const.BLOCK_WMATH: _("Matemaatiline tekst (MathType)"),
            const.BLOCK_HEADER: _("HTML päis"),
            const.INTER_CHOICE: _("Valikvastusega küsimus"),
            const.INTER_MCHOICE: _("Mitme valikuga tabel"),
            const.INTER_MATCH2: _("Sobitamine"),
            const.INTER_MATCH3: _("Sobitamine kolme hulgaga (ühe küsimusega)"),            
            const.INTER_MATCH3A: _("Sobitamine kolme hulgaga"),
            const.INTER_MATCH3B: _("Sobitamine kolme hulgaga kolmikute hindamisega"),
            const.INTER_ORDER: _("Järjestamine"),
            const.INTER_ASSOCIATE: _("Seostamine"),
            const.INTER_TEXT: _("Lühivastusega küsimus"), # const.TextEntry
            const.INTER_EXT_TEXT: _("Avatud vastusega küsimus"),		
            const.INTER_INL_TEXT: _("Avatud vastusega lünk"), # mitu TextEntry
            const.INTER_INL_CHOICE: _("Valikvastusega lünk"), # mitu InlineChoice
            const.INTER_GAP: _("Pangaga lünk"), # GapMatch
            const.INTER_PUNKT: _("Kirjavahemärkide lisamine"),
            const.INTER_MATH: _("Matemaatilise teksti sisestamine"),
            const.INTER_WMATH: _("Matemaatilise teksti sisestamine (MathType)"),            
            const.INTER_HOTTEXT: _("Tekstiosa valik"), # Hottext
            const.INTER_COLORTEXT: _("Tekstiosa värvimine"), 
            const.INTER_SLIDER: _("Liugur"),
            const.INTER_POS: _("Piltide lohistamine"),
            const.INTER_POS2: _("Piltide lohistamine II"),
            const.INTER_GR_GAP: _("Piltide lohistamine kujunditele"),
            const.INTER_TRAIL: _("Teekonna märkimine"),
            const.INTER_TXPOS: _("Tekstide lohistamine"),
            const.INTER_TXPOS2: _("Tekstide lohistamine II"),
            const.INTER_TXGAP: _("Tekstide lohistamine kujunditele"),            
            const.INTER_TXASS: _("Tekstide seostamine kujunditega"),            
            const.INTER_HOTSPOT: _("Pildil oleva kujundi valik"),
            const.INTER_GR_ORDER: _("Järjestamine pildil"),
            const.INTER_GR_ORDASS: _("Võrguülesanne"),            
            const.INTER_SELECT: _("Märkimine pildil"),
            const.INTER_SELECT2: _("Märkimine pildil II"),
            const.INTER_GR_ASSOCIATE: _("Seostamine pildil"),
            const.INTER_COLORAREA: _("Alade värvimine"),
            const.INTER_UNCOVER: _("Pildi avamine"),
            const.INTER_DRAW: _("Joonistamine"),
            const.INTER_AUDIO: _("Kõne salvestamine"),
            const.INTER_UPLOAD: _("Faili salvestamine"),
            const.INTER_GEOGEBRA: _("GeoGebra"),
            const.INTER_KRATT: _("Kratt"),
            const.INTER_DESMOS: _("Desmos"),
            const.INTER_CROSSWORD: _("Ristsõna"),
            const.BLOCK_GOOGLECHARTS: _("Google Charts"),
            const.BLOCK_FORMULA: _("Arvutatud väärtus"),
            const.BLOCK_RANDOM: _("Juhuarv"),
            }

    @property
    def STR_KEHTIV(self):
        return _("Kehtiv")

    @property
    def STR_KEHTETU(self):
        return _("Kehtetu")

    @property
    def LOG_TYPES(self):
        return {const.LOG_USER: _("Kasutamine"), 
                const.LOG_ERROR: _("Vealogi"),
                const.LOG_LOGIN: _("Sisselogimine"),
                const.LOG_PERM: _("Kasutajaõiguste muutmine"),
                const.LOG_XTEE: _("X-tee klient"),
                const.LOG_TRACE: _("Muu info"),
                const.LOG_JSON: _("JSON sõnum"),
                const.LOG_KOHT: _("Koolivalik"),
                const.LOG_WEBHOOK: _("Veriff webhook"),
                }

    @property
    def VASTVORM(self):
        return {const.VASTVORM_KE: _("Kirjalik (e-test)"),
                const.VASTVORM_SE: _("Suuline (e-test)"),
                const.VASTVORM_I: _("Suuline (intervjuu)"),
                const.VASTVORM_SH: _("Suuline (hindajaga)"),
                const.VASTVORM_KP: _("Kirjalik (p-test)"),
                const.VASTVORM_SP: _("Suuline (p-test)"),
                const.VASTVORM_KONS: _("Konsultatsioon")
                }
    
    @property
    def MAARAJA(self):
        return {const.MAARAJA_POLE: _("Ei"),
                const.MAARAJA_KOHT: _("Soorituskoht"),
                const.MAARAJA_MUUKOHT: _("Soorituskoht (teiste soorituskohtade tööd)"),                
                const.MAARAJA_EKK: _("Eksamikeskus"),
                }

    @property
    def RASKUS(self):
        return {const.RASKUS_KERGE: _("Kerge"),
                const.RASKUS_KESKMINE: _("Keskmine"),
                const.RASKUS_RASKE: _("Raske"),
                }

    @property
    def opt_raskus(self):
        return [(value, self.RASKUS.get(value)) for value in \
                (const.RASKUS_KERGE,
                 const.RASKUS_KESKMINE,
                 const.RASKUS_RASKE)]

    @property
    def AVALIK(self):
        return {
            const.AVALIK_POLE: _("Ei saa kasutada"),
            const.AVALIK_EKSAM: _("Testimiskorraga test"),
            const.AVALIK_MAARATUD: _("Määratud pedagoogidele"),
            const.AVALIK_OPETAJAD: _("Kõigile pedagoogidele"),
            const.AVALIK_SOORITAJAD: _("Kõigile lahendamiseks"),
            const.AVALIK_LITSENTS: _("Litsentsitud läbiviijatele"),            
            }

    @property
    def opt_avalik(self):
        return [(const.AVALIK_POLE, self.AVALIK.get(const.AVALIK_POLE)),
                (const.AVALIK_EKSAM, self.AVALIK.get(const.AVALIK_EKSAM)),
                (const.AVALIK_MAARATUD, self.AVALIK.get(const.AVALIK_MAARATUD)),
                (const.AVALIK_OPETAJAD, self.AVALIK.get(const.AVALIK_OPETAJAD)),
                (const.AVALIK_SOORITAJAD, self.AVALIK.get(const.AVALIK_SOORITAJAD)),
                (const.AVALIK_LITSENTS, self.AVALIK.get(const.AVALIK_LITSENTS)),                
                ]

    @property
    def S_STAATUS(self):
        return {const.S_STAATUS_TYHISTATUD: _("Tühistatud"), # tyhistatud
                const.S_STAATUS_REGAMATA: _("Registreerimata"), # registreerimine pooleli
                const.S_STAATUS_TASUMATA: _("Tasumata"), # tasu maksmata
                const.S_STAATUS_REGATUD: _("Registreeritud"), # sooviavaldus
                const.S_STAATUS_ALUSTAMATA: _("Alustamata"), # antud luba alustada
                const.S_STAATUS_POOLELI: _("Pooleli"),
                const.S_STAATUS_KATKESTATUD: _("Katkestas"),
                const.S_STAATUS_TEHTUD: _("Tehtud"),
                const.S_STAATUS_EEMALDATUD: _("Sooritamiselt eemaldatud"), # Eemaldatud või tühistatud
                const.S_STAATUS_PUUDUS: _("Puudus"),
                const.S_STAATUS_VABASTATUD: _("Vabastatud"),
                const.S_STAATUS_PUUDUS_VANEM: _("Lapsevanema keeldumine"),
                const.S_STAATUS_PUUDUS_HEV: _("Eritingimused"),
                const.S_STAATUS_KATKESPROT: _("Katkestas"),
                }
    @property
    def opt_s_staatus_test(self):
        # kogu testi sooritamise võimalikud olekud
        return [(const.S_STAATUS_TYHISTATUD, _("Tühistatud")),
                (const.S_STAATUS_REGAMATA, _("Registreerimata")),
                (const.S_STAATUS_TASUMATA, _("Tasumata")),
                (const.S_STAATUS_REGATUD, _("Registreeritud")),
                (const.S_STAATUS_ALUSTAMATA, _("Alustamata")),
                (const.S_STAATUS_POOLELI, _("Pooleli")),
                (const.S_STAATUS_KATKESTATUD, _("Katkestas")),
                (const.S_STAATUS_TEHTUD, _("Tehtud")),
                (const.S_STAATUS_EEMALDATUD, _("Eemaldatud või tühistatud")),
                (const.S_STAATUS_PUUDUS, _("Puudus")),
                (const.S_STAATUS_KATKESPROT, _("Katkestas (protokollil)")), 
                ]
    
    @property
    def L_STAATUS(self):
        return {const.L_STAATUS_KEHTETU: _("Kehtetu"),
                const.L_STAATUS_MAARATUD: _("Kehtiv"),
                const.L_STAATUS_OSALENUD: _("Osales"),
                const.L_STAATUS_PUUDUNUD: _("Puudus"),
                }
    
    @property
    def H_STAATUS(self):
        return {const.H_STAATUS_HINDAMATA: _("Alustamata"),
                const.H_STAATUS_POOLELI: _("Pooleli"),
                const.H_STAATUS_SUUNATUD: _("Ümber suunatud"),
                const.H_STAATUS_LYKATUD: _("Tagasi lükatud"),
                const.H_STAATUS_HINNATUD: _("Hinnatud"),
                const.H_STAATUS_LABIVAADATUD: _("Läbi vaadatud"),
                const.H_STAATUS_TOOPUUDU: _("Hindamata"), 
                }
    @property
    def H_PROBLEEM(self):
        return {const.H_PROBLEEM_POLE:'',
                const.H_PROBLEEM_SISESTAMATA: _("Sisestamata"),
                const.H_PROBLEEM_SISESTUSERINEVUS: _("Sisestusvead"),
                const.H_PROBLEEM_HINDAMISERINEVUS: _("Hindamiserinevused"),
                const.H_PROBLEEM_TOOPUUDU: _("Töö puudu"),
                const.H_PROBLEEM_VAIE: _("Vaideotsuse eelnõu"),
                }
    @property
    def HPR_STAATUS(self):
        return {const.H_STAATUS_HINDAMATA: _("Alustamata"),
                const.H_STAATUS_POOLELI: _("Pooleli"),
                const.H_STAATUS_LYKATUD: _("Loobutud"),
                const.H_STAATUS_HINNATUD: _("Sisestatud"),
                }
    @property
    def M_STAATUS(self):
        return {const.M_STAATUS_KEHTETU: _("Kehtetu"),
                const.M_STAATUS_LOODUD: _("Loodud"),
                const.M_STAATUS_VALJASTATUD: _("Väljastatud soorituskohale"),
                const.M_STAATUS_TAGASTAMISEL: _("Tagastamisel soorituskohast"),
                const.M_STAATUS_TAGASTATUD: _("Tagastatud soorituskohast"),
                const.M_STAATUS_HINDAJA: _("Väljastatud hindajale"),
                const.M_STAATUS_HINNATUD: _("Tagastatud hindajalt"),
                }
    @property
    def V_STAATUS(self):
        return {const.V_STAATUS_ESITAMATA: _("Esitamata"),
                const.V_STAATUS_ESITATUD: _("Esitatud"),
                const.V_STAATUS_MENETLEMISEL: _("Menetlemisel"),
                const.V_STAATUS_ETTEPANDUD: _("Menetlemisel (ettepanek edastatud)"),
                const.V_STAATUS_OTSUSTAMISEL: _("Otsustamisel"),
                const.V_STAATUS_OTSUSTATUD: _("Otsustatud"),                
                const.V_STAATUS_TAGASIVOETUD: _("Tagasi võetud"),                
                }
    @property
    def V_STAATUS_OPT(self):
        return [(const.V_STAATUS_ESITAMATA, _("Esitamata")),
                (const.V_STAATUS_ESITATUD, _("Esitatud")),
                (const.V_STAATUS_MENETLEMISEL, _("Menetlemisel")),
                (const.V_STAATUS_OTSUSTAMISEL, _("Otsustamisel")),                
                (const.V_STAATUS_OTSUSTATUD, _("Otsustatud")),
                (const.V_STAATUS_TAGASIVOETUD, _("Tagasi võetud")),
                ]
    @property
    def U_STAATUS(self):
        return {const.U_STAATUS_UUENDADA: _("Uuendada"),
                const.U_STAATUS_VALJASTADA: _("Väljastada"),
                const.U_STAATUS_TYHISTADA: _("Tühistada"),
                }
    @property
    def N_STAATUS(self):
        return {const.N_STAATUS_KEHTETU: _("Kehtetu"),
                const.N_STAATUS_KEHTIV: _("Kehtiv"),
                const.N_STAATUS_SALVESTATUD: _("Kehtiv, salvestatud"),
                const.N_STAATUS_AVALDATUD: _("Avaldatud"),
                }
    @property
    def YK_STAATUS(self):
        return {const.YK_STAATUS_MITTEAVALIK: _("Mitteavalik"),
                const.YK_STAATUS_TESTIMISEL: _("Testimisel"),
                const.YK_STAATUS_AVALIK: _("Avalik"),
                const.YK_STAATUS_ARHIIV: _("Arhiveeritud"),
                }
       
    @property
    def HINDAJA(self):
        return {const.HINDAJA1: _("I hindaja"),
                const.HINDAJA2: _("II hindaja"),
                const.HINDAJA3: _("III hindaja"),
                const.HINDAJA4: _("Eksperthindaja (IV)"),
                const.HINDAJA5: _("Eksperthindaja (vaie)"),
                const.HINDAJA6: _("VI hindaja"),
                const.GRUPP_HINDAJA_S: _("I hindaja (suuline)"),
                const.GRUPP_HINDAJA_S2: _("II hindaja (suuline)"),
                }
    @property
    def TEATEKANAL(self):
        return {const.TEATEKANAL_EPOST: _("E-post"),
                const.TEATEKANAL_POST: _("Post"),
                const.TEATEKANAL_KALENDER: _("Riigiportaal"),
                const.TEATEKANAL_STATEOS: _("StateOS"),
                const.TEATEKANAL_EIS: _("Süsteemisisene"),
                }

    @property
    def C_CORRECT(self):
        return {
            const.C_VALE: _("Vale"),
            const.C_OIGE: _("Õige"),
            const.C_OSAOIGE: _("Osaliselt õige"),
            const.C_LOETAMATU: _("Loetamatu"),
            const.C_VASTAMATA: _("Vastamata"),
            }

    @property
    def AUTENTIMINE(self):
        return {const.AUTH_TYPE_PW: _("parool"),
                const.AUTH_TYPE_TESTPW: _("testiparool"),
                const.AUTH_TYPE_ID: _("ID-kaart"),
                const.AUTH_TYPE_ID2: _("digi-ID"),
                const.AUTH_TYPE_C: _("Keskserver"),
                const.AUTH_TYPE_L: _("x-tee"),
                const.AUTH_TYPE_M: _("mobiil-ID"),
                const.AUTH_TYPE_TARA: _("TARA"),
                const.AUTH_TYPE_HARID: _("HarID"),
                const.AUTH_TYPE_SMARTID: _("smart-ID"),
                const.AUTH_TYPE_SEB: _("SEB"),
                }

    @property
    def KLASS_A(self):
        return [('1', '1. klass', const.ASTE_I),
                ('2', '2. klass', const.ASTE_I),
                ('3', '3. klass', const.ASTE_I),
                ('4', '4. klass', const.ASTE_II),
                ('5', '5. klass', const.ASTE_II),
                ('6', '6. klass', const.ASTE_II),
                ('7', '7. klass', const.ASTE_III),
                ('8', '8. klass', const.ASTE_III),
                ('9', '9. klass', const.ASTE_III),
                ('10', '10. klass', const.ASTE_G),
                ('11', '11. klass', const.ASTE_G),
                ('G1', 'G1', const.ASTE_G),
                ('G2', 'G2', const.ASTE_G),
                ('G3', 'G3', const.ASTE_G), 
                ('G10', 'G10', const.ASTE_G),
                ('G11', 'G11', const.ASTE_G),
                ('G12', 'G12', const.ASTE_G),
                ('NA', 'määramata', None),
                ('91', 'pikendatud 1. aasta', const.ASTE_G),
                ('92', 'pikendatud 2. aasta', const.ASTE_G),
                ('93', 'pikendatud 3. aasta', const.ASTE_G),
                ]
    
    def klread(self, klassifikaator_kood, ylem_kood=None, ylem_id=None, ylem_required=False, ylem_none=False, lang=None, avalik=None, kinnituseta=None):
        """Leitakse klassifikaatoriread antud parameetritega.
        """
        if ylem_required and not (ylem_kood or ylem_id):
            return []            
        q = Klrida.get_q_by_kood(klassifikaator_kood, None, ylem_kood=ylem_kood, ylem_id=ylem_id, ylem_none=ylem_none, lang=lang)
        if avalik:
            q = q.filter(Klrida.avalik==avalik)
        if kinnituseta:
            q = q.filter(Klrida.kinnituseta==True)
        if klassifikaator_kood == 'TOOKASK':
            q = q.order_by(Klrida.jrk, Klrida.kirjeldus)
        else:
            q = q.order_by(Klrida.jrk, Klrida.nimi)
        return q.all()

    def klread_id(self, klassifikaator_kood, ylem_kood=None, ylem_id=None, bit=None, empty=False):
        """Leitakse klassifikaatoriread ja väljastatakse select-valikutena (id,nimi)
        """
        lang = usersession.get_lang()
        _cache_key = (klassifikaator_kood, ylem_kood, ylem_id, bit, lang)
        li = cache_id.get(_cache_key)
        if not li:
            li = []
            for r in self.klread(klassifikaator_kood, ylem_kood, ylem_id, lang=lang):
                bitimask = r[4] or 0
                if not bit or bitimask & bit:
                    li.append((r[0], r[2]))
            cache_id[_cache_key] = li

        if empty:
            return [('', _("-- Vali --"))] + li
        else:
            return li
        
    def klread_kood(self, 
                    klassifikaator_kood, 
                    ylem_kood=None, 
                    ylem_id=None, 
                    bit=None, 
                    empty=False, 
                    ylem_required=False,
                    vaikimisi=None,
                    ylem_none=False,
                    lang=None,
                    avalik=None,
                    kinnituseta=None):
        """Leitakse klassifikaatoriread ja väljastatakse select-valikutena (kood,nimi)
        """
        lang = lang or usersession.get_lang()
        _cache_key = (klassifikaator_kood, ylem_kood, ylem_id, bit, ylem_required, lang, avalik, kinnituseta)
        li = cache_kood.get(_cache_key)
        if not li:
            li = []
            for r in self.klread(klassifikaator_kood, ylem_kood, ylem_id, ylem_required, ylem_none, lang, avalik, kinnituseta):
                r_bitimask = r[4]
                if not bit or r_bitimask and r_bitimask & bit:
                    r_kood = r[1]
                    r_nimi = r[2]
                    r_id = r[0]
                    if klassifikaator_kood == 'ERIVAJADUS':
                        r_kirjeldus = r[5]
                        li.append((r_kood, r_nimi, r_id, r_kirjeldus))
                    else:
                        li.append((r_kood, r_nimi, r_id))
            cache_kood[_cache_key] = li
        if vaikimisi:
            # vaikimisi väärtus ei pruugi enam kehtiv klassifikaatoriväärtus olla
            if vaikimisi not in [r[0] for r in li]:
                li = [r for r in li] # teeme listist koopia
                nimi = Klrida.get_str(klassifikaator_kood, vaikimisi, ylem_kood, ylem_id)
                li.append((vaikimisi, nimi or vaikimisi))

        if empty:
            return [('', _("-- Vali --"))] + li
        else:
            return li

    def teemad2(self, aine_kood, aste):
        "Select2 option teema/alateema kohta"
        li = []
        if aine_kood:
            for r_teema in self.klread_kood('TEEMA', ylem_kood=aine_kood, bit=self.aste_bit(aste)):
                alateema_kood, alateema_nimi, alateema_id = r_teema[:3]
                li.append({'id': alateema_kood,
                           'text': alateema_nimi,
                           'level': 0
                           })
                for r_alateema in self.klread_kood('ALATEEMA', ylem_id=alateema_id):
                    ala_kood, ala_nimi = r_alateema[:2]
                    li.append({'id': alateema_kood + '.' + ala_kood,
                               'text': ala_nimi,
                               'p_text': alateema_nimi,
                               #'p_text': alateema_nimi + ' | ',
                               'level': 1
                               })
        return li

    def oigused(self):
        q = SessionR.query(Kasutajaoigus).order_by(Kasutajaoigus.kirjeldus)
        li = [(o.id,'%s (%s)' % (o.kirjeldus, o.nimi)) for o in q.all()]
        return li
    
    def opitulemused(self, aine, for_select2=True):
        "Õpitulemuste leidmine EISi aine koodi järgi"
        li = []
        for row in self.klread_id('OPITULEMUS', ylem_kood=aine):
            r_id, nimi = row[:2]
            if for_select2:
                # select2 otsingu valik
                li.append({'id': r_id,
                           'text': nimi,
                           })
            else:
                # tavalise select-välja valik
                li.append((r_id, nimi))
        return li

    def astmed(self, aine_kood=None):
        "Leiame antud aines kehtivad kooliastmed/erialad"
        li = self.klread_kood('ASTE', ylem_none=True)
        return li

    @property
    def aine_keeletasemed(self):
        "Tagastab listi [[keeletase, [ained]]]"
        _cache_key = ('KEELETASE', 'aineti',)
        li = cache_kood.get(_cache_key)
        if not li:
            tasemed = {}
            Aine = sa.orm.aliased(Klrida)
            q = (SessionR.query(Klrida.kood, Aine.kood)
                 .filter(Klrida.klassifikaator_kood=='KEELETASE')
                 .filter(Klrida.kehtib==True)
                 .join((Aine, Aine.id==Klrida.ylem_id))
                 .filter(Aine.klassifikaator_kood=='AINE')
                 .filter(Aine.kehtib==True))
            for tase, aine in q.all():
                if tase not in tasemed:
                    tasemed[tase] = []
                tasemed[tase].append(aine)
            li = list(tasemed.items())
            cache_kood[_cache_key] = li
        return li

    @property
    def nullipained(self):
        """Tagastab listi nende ainete koodidest, mille korral
        kasutatakse e-testide hindamisel null punkti põhjust
        """
        _cache_key = ('NULLIPAINE',)
        li = cache_kood.get(_cache_key)
        if not li:
            q = (SessionR.query(Klrida.kood)
                 .filter(Klrida.klassifikaator_kood=='AINE')
                 .filter(Klrida.nullipohjus==True)
                 )
            li = [kood for kood, in q.all()]
            cache_kood[_cache_key] = li
        return li
    
    def kasutaja_nimi(self, ik):
        """Tagastab kasutaja nime
        """
        _cache_key = ('KASUTAJA', ik)
        value = cache_kood.get(_cache_key)
        if not value:
            q = (SessionR.query(Kasutaja.nimi)
                 .filter_by(isikukood=ik)
                 )
            for value, in q.all():
                cache_kood[_cache_key] = value
        return value
    
    @classmethod
    def aste_bit(cls, aste_kood, aine_kood=None):
        "Leiame antud astme bitimaski"

        if not aste_kood:
            return 0
        # vaikimisi kooliastmete bitid
        vaikimisi_astmed = (const.ASTE_I,
                            const.ASTE_II,
                            const.ASTE_III, 
                            const.ASTE_G,
                            const.ASTE_Y)
        try:
            # kui on vaikimisi aine astmed
            astendaja = vaikimisi_astmed.index(aste_kood)
        except ValueError:
            # kui on ainega seotud astmed, siis peab aste_kood olema astendaja
            try:
                astendaja = int(aste_kood)
                if astendaja > 15:
                    # mõttetult suur (andmebaasi & operaator ei pea seda taluma)
                    return 0
            except ValueError:
                return 0
        mask = 2**astendaja
        return mask

    def __getattr__(self, kood):
        """Kui mallis esmakordselt küsitakse valikvälja valikuid c.opt.NIMI,
        siis täidetakse siin muutuja c.opt.NIMI.
        """
        if kood.endswith('_empty'):
            kood1 = kood[:-6]
            try:
                # kui atribuut on olemas
                li = self.__getattribute__(kood1)
            except AttributeError:
                # kui ei ole, siis pöördume selle sama funktsiooni poole
                li = self.__getattr__(kood1)
            return [('', _("-- Vali --"))] + li
        else:
            # klassifikaatoriridade päring
            li = self.klread_kood(kood)
            try:
                self.__setattr__(kood, li)
            except AttributeError:
                pass
            return li

    # def oppekava_ehis(self, kood):
    #     # üldhariduse õppekavad EHISes:
    #     map_k = {'1010101': 'riiklik õppekava (RÕK)',
    #              '1010102': 'lihtsustatud õpe',
    #              '1010103': 'IB',
    #              '1010104': 'European Baccalaureate',
    #              '1010107': 'hooldusõpe',
    #              '1010109': 'toimetulekuõpe',
    #              '2010101': 'riiklik õppekava, pk',
    #              '3010101': 'riiklik õppekava, gümn'
    #              }
    #     return map_k.get(kood)
        
    def get_name(self, klassifikaator_kood, kood):
        if not kood:
            return
        li = self.__getattribute__(klassifikaator_kood)
        if li:
            for o in li:
                if o[0] == kood:
                    return o[1]

    def rveksamid(self, aine_kood=None):
        """Leitakse rahvusvaheliste eksamite loetelu ja väljastatakse select-valikutena (id,nimi)
        """
        from .rveksam import Rveksam

        #_cache_key = ('RVEKSAM', None, None, None)
        _cache_key = 'Rveksam'
        if aine_kood:
            _cache_key += ':' + aine_kood
        li = cache_id.get(_cache_key)
        if not li:
            q = SessionR.query(Rveksam.id, Rveksam.nimi)
            if aine_kood:
                q = q.filter_by(aine_kood=aine_kood)
            q = q.order_by(Rveksam.nimi)
            li = [(r_id, r_nimi) for (r_id, r_nimi) in q.all()]
            cache_id[_cache_key] = li

        return li

    def ylkogud(self, aine_kood=None, avalik_y=None, pedagoog=None):
        """Leitakse ülesandekogude loetelu ja väljastatakse select-valikutena (id,nimi)
        """
        from .kogu.ylesandekogu import Ylesandekogu
        if avalik_y and pedagoog:
            # kuvada ainult need kogud, milles on avalikke või pedagoogile lubatud ylesandeid/teste
            _cache_key = ('YLKOGUyp', aine_kood)
        elif avalik_y:
            # kuvada ainult need kogud, milles on avalikke ylesandeid
            _cache_key = ('YLKOGUya', aine_kood)
        else:
            # kuvada kõik ylesandekogud
            _cache_key = ('YLKOGU', aine_kood)
            
        li = cache_id.get(_cache_key)
        if not li:
            li = Ylesandekogu.opt_kogud(aine_kood, avalik_y, pedagoog)
            cache_id[_cache_key] = li
        return li

    @property
    def noutav(self):
        return [(const.MAARAJA_EKK, _("Eksamikeskus")),
                (const.MAARAJA_KOHT, _("Soorituskoht")),
                (const.MAARAJA_POLE, _("Pole nõutav")),
                ]

    @property
    def noutavmuu(self):
        return [(const.MAARAJA_EKK, _("Eksamikeskus")),
                (const.MAARAJA_KOHT, _("Soorituskoht")),
                (const.MAARAJA_MUUKOHT, _("Soorituskoht (teiste soorituskohtade tööd)")),                
                (const.MAARAJA_POLE, _("Pole nõutav")),
                ]

    @property
    def logityyp(self):
        return [(const.LOG_LOGIN, _("Sisselogimine")),
                (const.LOG_KOHT, _("Kooli valik")),
                (const.LOG_USER, _("Kasutamine")),
                (const.LOG_ERROR, _("Vealogi")),
                (const.LOG_PERM, _("Kasutajaõiguste muutmine")),
                (const.LOG_XTEE, _("X-tee klient")),
                (const.LOG_JSON, _("JSON sõnum")),
                (const.LOG_TRACE, _("Muu info")),
                ]

    @property
    def interaction_block(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_block]
    @property
    def interaction_choice(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_choice]
    @property
    def interaction_text(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_text]
    @property
    def interaction_graphic(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_graphic]
    @property
    def interaction_file(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_file]
    @property
    def interaction_output(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_output]    
    @property
    def interaction_integrated(self):
        return [(k, self.interactions.get(k)) for k in const.interaction_integrated]    

    @property
    def interaction(self):
        "Vastusega sisuplokitüüpide loetelu"
        li = self.interaction_choice + self.interaction_text + self.interaction_graphic + self.interaction_file + self.interaction_integrated 
        return sorted(li, key=lambda r: r[1])

    @property
    def blocktype(self):
        "Sisuplokitüüpide loetelu"
        return self.interaction_block + self.interaction

    @property
    def interaction_opt(self):
        "Vastusega sisuplokitüüpide loetelu"
        #return self.interaction_choice + self.interaction_text + self.interaction_graphic + self.interaction_file
        return [OptGroup(_("Vastuseta"), self.block),
                OptGroup(_("Valikud"), self.interaction_choice),
                OptGroup(_("Tekstküsimused"), self.interaction_text),
                OptGroup(_("Piltküsimused"), self.interaction_graphic),
                OptGroup(_("Failiküsimused"), self.interaction_file),
                OptGroup(_("Integreeritud"), self.interaction_integrated),                
                ]

    def grupp_dict(self):
        return {
            const.GRUPP_ADMIN: _("Administraator"),
            const.GRUPP_SYSADMIN: _("Süsteemiadministraator"),
            const.GRUPP_AINESPETS: _("Ainespetsialist"),
            const.GRUPP_AINETOORYHM: _("Ainetöörühma liige"),
            const.GRUPP_OSASPETS: _("Osaoskuse spetsialist"),
            const.GRUPP_VALJAVOTE: _("Vastuste väljavõtte allalaadija"),
            const.GRUPP_Y_KOOSTAJA: _("Ülesande koostaja"),
            const.GRUPP_Y_VAATAJA: _("Ülesande vaataja"),
            const.GRUPP_Y_TOIMETAJA: _("Ülesande toimetaja"),
            const.GRUPP_Y_TOLKIJA: _("Ülesande tõlkija"),
            const.GRUPP_Y_KUJUNDAJA: _("Ülesande kujundaja"),
            const.GRUPP_T_KOOSTAJA: _("Testi koostaja"),
            const.GRUPP_T_VAATAJA: _("Testi vaataja"),
            const.GRUPP_T_TOIMETAJA: _("Testi toimetaja"),
            const.GRUPP_T_TOLKIJA: _("Testi tõlkija"),
            const.GRUPP_T_KUJUNDAJA: _("Testi kujundaja"),
            const.GRUPP_T_OMANIK: _("Testi omanik"),
            const.GRUPP_T_TOOVAATAJA: _("Töö vaataja"),            
            const.GRUPP_T_KORRALDAJA: _("Testi korraldaja"),
            const.GRUPP_T_HINDAMISJUHT: _("Testi hindamisjuht"),            
            const.GRUPP_KORRALDUS: _("Eksamikorralduse ametnik"),
            const.GRUPP_P_KORRALDUS: _("Piirkondlik korraldaja"),
            const.GRUPP_E_KORRALDUS: _("Eksamikorraldaja"),            
            const.GRUPP_REGAJA: _("Registreerija"),
            const.GRUPP_HINDAMISJUHT: _("Hindamisjuht"),
            const.GRUPP_HINDAMISEKSPERT: _("Hindamise ekspert"),
            const.GRUPP_SISESTAJA: _("Sisestaja"),
            const.GRUPP_PARANDAJA: _("Sisestuse parandaja"),
            const.GRUPP_VAIDEKOM: _("Vaidekomisjoni liige"),
            const.GRUPP_VAIDEKOM_SEKRETAR: _("Vaidekomisjoni sekretär"),
            const.GRUPP_VAIDEKOM_ESIMEES: _("Vaidekomisjoni esimees"),
            const.GRUPP_ERIVAJADUS: _("Eritingimuste spetsialist"),
            const.GRUPP_AMETNIK: _("Eksamikeskuse töötaja"),
            const.GRUPP_OMATEST: _("Oma testi korraldaja"),
            const.GRUPP_OPETAJA: _("Pedagoog"),
            const.GRUPP_K_ADMIN: _("Soorituskoha administraator"),
            const.GRUPP_K_JUHT: _("Koolijuht"),
            const.GRUPP_K_PLANK: _("Plankide haldaja"),
            const.GRUPP_K_PROTOKOLL: _("Protokollisisestaja"),
            const.GRUPP_FAILID: _("Failide üleslaadija"),
            const.GRUPP_K_FAILID: _("Failide laadija"),
            const.GRUPP_OPILANE: _("Õpilane"),
            const.GRUPP_LOPETANU: _("Varemlõpetanu"),
            const.GRUPP_T_ADMIN: _("Testi administraator"),
            const.GRUPP_VAATLEJA: _("Vaatleja"),
            const.GRUPP_HINDAJA_S: _("Hindaja (suulised testid)"),
            const.GRUPP_HINDAJA_K: _("Hindaja (kirjalikud testid)"),
            const.GRUPP_HINDAJA_S2: _("2. hindaja (suuline)"),
            const.GRUPP_INTERVJUU: _("Intervjueerija"),
            const.GRUPP_HIND_INT: _("Hindaja-intervjueerija"),
            const.GRUPP_KOMISJON: _("Eksamikomisjoni liige"),
            const.GRUPP_KOMISJON_ESIMEES: _("Eksamikomisjoni esimees"),
            const.GRUPP_KONSULTANT: _("Konsultant"),
            const.GRUPP_LABIVIIJA: _("Testide läbiviija"),
            #const.GRUPP_KYSED_ADMIN: _("Küsitluste peahaldaja"),
            #const.GRUPP_KYSED: _("Küsitluste haldaja"),
            const.GRUPP_A_PSYH: _("Koolipsühholoog"),
            const.GRUPP_A_PSYHADMIN: _("Koolipsühholoogi litsentside haldaja"),
            const.GRUPP_A_LOGOPEED: _("Logopeed"),
            const.GRUPP_A_LOGOPEEDADMIN: _("Logopeedide litsentside haldaja"),
            const.GRUPP_AINEOPETAJA: _("Aineõpetaja"),
            const.GRUPP_HTMLEDIT: _("Tekstitoimetis lähtekoodi kasutaja"),
            const.GRUPP_STATISTIK: _("Statistik"),
            const.GRUPP_INFOSPETS: _("Infospetsialist"),
            const.GRUPP_PLANK: _("Harno plankide haldaja"),
            const.GRUPP_AVALDET: _("Tulemuste avaldamise teavituste saaja"),
            const.GRUPP_UI_TOLKIJA: _("Kasutajaliidese tõlkija"),
            const.GRUPP_TOOVAATAJA: _("Testitöö vaataja"),
            const.GRUPP_SISUAVALDAJA: _("Ülesannete ja testide avaldaja"),
            }
    
    def grupp_nimi(self, grupp_id):
        nimi = self.grupp_dict().get(grupp_id)
        if not nimi:
            g = Kasutajagrupp.get(grupp_id)
            if g:
                nimi = g.nimi
        return nimi

    @property
    def ametnikgrupp(self):
        "EKK vaate kasutajate grupid"
        return [(k_id, self.grupp_nimi(k_id)) for k_id, in \
                (SessionR.query(Kasutajagrupp.id)
                 .filter(Kasutajagrupp.tyyp.in_(
                     (const.USER_TYPE_EKK, const.USER_TYPE_AV)))
                 .filter(~ Kasutajagrupp.id.in_(
                     (const.GRUPP_A_PSYH, const.GRUPP_A_LOGOPEED)
                     ))
                 .order_by(Kasutajagrupp.nimi).all())]

    @property
    def ylesandegrupp(self):
        "Ülesandega seotud isiku kasutajagrupp"
        return [(k_id, self.grupp_nimi(k_id)) for k_id, in \
                (SessionR.query(Kasutajagrupp.id)
                 .filter_by(tyyp=const.USER_TYPE_Y)
                 .order_by(Kasutajagrupp.nimi).all())]

    @property
    def ylesandegrupp_tooryhm(self):
        "Rollid, mida ainetöörühmaliige tohib teistele kasutajatele anda"
        return [a for a in self.ylesandegrupp if \
                    a[0] in (const.GRUPP_Y_KOOSTAJA,
                             const.GRUPP_Y_VAATAJA)]

    @property
    def testigrupp(self):
        "Innove vaates loodud testiga seotud isiku kasutajagrupp"
        return self.opt_testigrupp(False)

    def opt_testigrupp(self, avalik):
        "Innove vaates loodud testiga seotud isiku kasutajagrupp"
        return [(k_id, self.grupp_nimi(k_id)) for k_id, in \
                (SessionR.query(Kasutajagrupp.id)
                 .filter_by(tyyp=const.USER_TYPE_T)
                 .order_by(Kasutajagrupp.nimi).all())
                if avalik or k_id != const.GRUPP_T_OMANIK]
    
    @property
    def ainelabiviijagrupp(self):
        "Testi läbiviimise grupid"
        return [(const.GRUPP_HINDAJA_K, _("Hindaja (kirjalik)")),
                (const.GRUPP_HINDAJA_S, _("Hindaja (suuline)")),
                (const.GRUPP_INTERVJUU, _("Intervjueerija")),
                (const.GRUPP_KONSULTANT, _("Konsultant")),
                (const.GRUPP_KOMISJON, _("Eksamikomisjoni liige")),
                (const.GRUPP_KOMISJON_ESIMEES, _("Eksamikomisjoni esimees")),
                ]

    @property
    def labiviijagrupp(self):
        "Testi läbiviimise grupid"
        return [(const.GRUPP_HINDAJA_K, _("Hindaja (kirjalik)")),
                (const.GRUPP_HINDAJA_S, _("Hindaja (suuline)")),
                (const.GRUPP_INTERVJUU, _("Intervjueerija")),
                (const.GRUPP_KONSULTANT, _("Konsultant")),
                (const.GRUPP_KOMISJON, _("Eksamikomisjoni liige")),
                (const.GRUPP_KOMISJON_ESIMEES, _("Eksamikomisjoni esimees")),
                (const.GRUPP_VAATLEJA, _("Vaatleja")),
                ]

    @property
    def labiviijagrupp_s12(self):
        "Testi läbiviimise grupid, kus I ja II suuline hindaja on eraldi"
        return [(const.GRUPP_HINDAJA_K, _("Hindaja (kirjalik)")),
                (const.GRUPP_HINDAJA_S12, _("Hindaja (suuline I või II)")),
                (const.GRUPP_HINDAJA_S, _("Hindaja (suuline I)")),
                (const.GRUPP_HINDAJA_S2, _("Hindaja (suuline II)")),                                
                (const.GRUPP_INTERVJUU, _("Intervjueerija")),
                (const.GRUPP_KONSULTANT, _("Konsultant")),
                (const.GRUPP_KOMISJON, _("Eksamikomisjoni liige")),
                (const.GRUPP_KOMISJON_ESIMEES, _("Eksamikomisjoni esimees")),
                (const.GRUPP_VAATLEJA, _("Vaatleja"))]

    @property
    def kasutajagrupp(self):
        "Testidega seotud kasutajate grupid"
        return [(k_id, self.grupp_nimi(k_id)) for k_id, in \
                (SessionR.query(Kasutajagrupp.id)
                 .filter_by(tyyp=const.USER_TYPE_KOOL)
                 .order_by(Kasutajagrupp.nimi).all())]

    @property
    def kasutajagrupp_ehis(self):
        "Kasutajate grupid + EHISes olvate kasutajate grupid"
        return self.kasutajagrupp + [(const.GRUPP_E_OPETAJA, _("Pedagoog (EHISest)")),
                                     (const.GRUPP_E_ADMIN, _("Õppeasutuse juht (EHISest)"))]

    @property
    def kooligrupp(self):
        li = [(const.GRUPP_K_JUHT, _("Koolijuht")),
              (const.GRUPP_K_ADMIN, _("Soorituskoha administraator")),
              #(const.GRUPP_KYSED, _("Küsitluste haldaja")),
              (const.GRUPP_K_PLANK, _("Plankide haldaja")),         
              (const.GRUPP_K_PROTOKOLL, _("Protokollisisestaja")),
              (const.GRUPP_K_FAILID, _("Failide laadija")),              
              (const.GRUPP_AINEOPETAJA, _("Aineõpetaja")),
              ]
        return li

    def get_antav_kooligrupp(self, on_ekk):
        li = [(const.GRUPP_K_ADMIN, _("Soorituskoha administraator")),
              #(const.GRUPP_KYSED, _("Küsitluste haldaja")),
              (const.GRUPP_K_PLANK, _("Plankide haldaja")),         
              (const.GRUPP_K_PROTOKOLL, _("Protokollisisestaja")),
              (const.GRUPP_K_FAILID, _("Failide laadija")),
              (const.GRUPP_AINEOPETAJA, _("Aineõpetaja")),              
              ]
        if on_ekk:
            li = [(const.GRUPP_K_JUHT, _("Koolijuht"))] + li
        return li

    @property
    def normityyp(self):
        return ((const.NORMITYYP_PALLID, _("Punktid")),
                (const.NORMITYYP_KPALLID, _("Keskmised pallid")),
                (const.NORMITYYP_PUNKTID, _("Küsimuse punktid")),                
                (const.NORMITYYP_SUHE, _("Õigete vastuste suhe")),
                (const.NORMITYYP_AEG, _("Aeg")),
                (const.NORMITYYP_VEAD, _("Vigade arv")),
                (const.NORMITYYP_VASTUS, _("Vastus")),
                (const.NORMITYYP_VALEM, _("Valem")),
                (const.NORMITYYP_PROTSENT, _("Protsent")),
                )

    @property
    def normityyp_psyh(self):
        return ((const.NORMITYYP_PALLID, _("Punktid")),
                (const.NORMITYYP_KPALLID, _("Keskmise küsimuse pallid")),
                (const.NORMITYYP_SUHE, _("Õigete vastuste suhe")),
                (const.NORMITYYP_AEG, _("Aeg")),
                (const.NORMITYYP_VEAD, _("Vigade arv")),
                (const.NORMITYYP_VASTUS, _("Vastus")),
                )
   
    @property
    def normityyp_opip(self):
        return ((const.NORMITYYP_VASTUS, _("Vastus")),
                (const.NORMITYYP_VALEM, _("Valem")),
                )

    @property
    def normityyp_diag2(self):
        return ((const.NORMITYYP_PALLID, _("Punktid")),
                (const.NORMITYYP_PROTSENT, _("Protsent")),
                (const.NORMITYYP_VASTUS, _("Vastus")),
                )
    
    def normityyp_nimi(self, normityyp):
        for key, value in self.normityyp:
            if key == normityyp:
                return value

    @property
    def tsmall(self):
        return ((const.TSMALL_VABA, _("Käsitsi kujundatav tagasiside")),
                (const.TSMALL_DIAG, _("D-testi tagasiside")),
                (const.TSMALL_PSYH, _("Koolipsühholoogi testi profiilileht")),
                (const.TSMALL_OPIP, _("Õpipädevustesti profiilileht")),
                )
    
    @property
    def testiliik(self):
        "Tagastatakse kasutajale antud lehekyljel lubatud testiliikide valik"
        li = self.klread_kood('TESTILIIK')
        if self.handler:
            allowed = self.handler.c.user.get_testiliigid(self.handler._permission, const.BT_INDEX)
            if None not in allowed:
                li = [r for r in li if r[0] in allowed]
        return li

    @property
    def testsessioon(self):
        "Tagastatakse kasutajale antud lehekyljel lubatud testsessioonide valik"
        from .test import Testsessioon
        if self.handler:
            allowed = self.handler.c.user.get_testiliigid(self.handler._permission, const.BT_INDEX)
            if None in allowed:
                allowed = None
        else:
            allowed = None
        li = Testsessioon.get_opt(allowed)
        return li

    @property
    def erivajadused(self):
        opt_erivajadus = [('vabastatud', 'Vabastatud')]
        for bitimask, label in ((const.ASTE_BIT_III, 'Põhikool'),
                                (const.ASTE_BIT_G, 'Gümnaasium')):
            q = (Klrida.get_q_by_kood('ERIVAJADUS')
                 .filter(Klrida.bitimask==bitimask)
                 .order_by(Klrida.jrk)
                 )
            aste_opt = [(r[1], r[2]) for r in q.all()]
            opt_erivajadus.append((aste_opt, label))
        return opt_erivajadus

    HINNE = (5, 4, 3, 2, 1)

    expression = [("and", "and"),
                  ("anyN", "anyN"),
                  ("baseValue", "baseValue"),
                  ("containerSize", "containerSize"),
                  ("contains", "contains"),
                  ("correct", "correct"),
                  ("customOperator", "customOperator"),
                  ("default", "default"),
                  ("delete", "delete"),
                  ("divide", "divide"),
                  ("durationGTE", "durationGTE"),
                  ("durationLT", "durationLT"),
                  ("equalRounded", "equalRounded"),
                  ("equal", "equal"),
                  ("fieldValue", "fieldValue"),
                  ("gte", "gte"),
                  ("gt", "gt"),
                  ("index", "index"),
                  ("inside", "inside"),
                  ("integerDivide", "integerDivide"),
                  ("integerModulus", "integerModulus"),
                  ("integerToFloat", "integerToFloat"),
                  ("isNull", "isNull"),
                  ("lte", "lte"),
                  ("lt", "lt"),
                  ("mapResponsePoint", "mapResponsePoint"),
                  ("mapResponse", "mapResponse"),
                  ("match", "match"),
                  ("member", "member"),
                  ("multiple", "multiple"),
                  ("not", "not"),
                  ("null", "null"),
                  ("numberCorrect", "numberCorrect"),
                  ("numberIncorrect", "numberIncorrect"),
                  ("numberPresented", "numberPresented"),
                  ("numberResponded", "numberResponded"),
                  ("numberSelected", "numberSelected"),
                  ("ordered", "ordered"),
                  ("or", "or"),
                  ("outcomeMaximum", "outcomeMaximum"),
                  ("outcomeMinimum", "outcomeMinimum"),
                  ("patternMatch", "patternMatch"),
                  ("power", "power"),
                  ("product", "product"),
                  ("randomFloat", "randomFloat"),
                  ("randomInteger", "randomInteger"),
                  ("random", "random"),
                  ("round", "round"),
                  ("stringMatch", "stringMatch"),
                  ("substring", "substring"),
                  ("subtract", "subtract"),
                  ("sum", "sum"),
                  ("testVariables", "testVariables"),
                  ("truncate", "truncate"),
                  ("variable", "variable"),
                  ]

    rptemplate = [('match_correct', 'Tulemuseks on 1, kui valiti õige vastus (match_correct)'),
                  ('map_response', 'Tulemuseks on valitud vastusele vastavad pallid (map_response)'),
                  ('map_response_point', 'Tulemuseks on valitud punkti sisaldavale piirkonnale vastavad pallid (map_response_point)'),
                  ]

    cardinality = [('single', 'single'),
                   ('multiple', 'multiple'),
                   ('ordered', 'ordered'),
                   ]

    @property
    def cardinality_ordered(self):
        return [(const.CARDINALITY_ORDERED, _("Kogu järjekord õigesti")),
                (const.CARDINALITY_ORDERED_ADJ, _("Paar õigesti kõrvuti")),
                (const.CARDINALITY_ORDERED_SEQ, _("Paar õiges järgnevuses")),
                (const.CARDINALITY_ORDERED_POS, _("Järjekorranumber")),
                ]
    @property
    def cardinality_igap(self):
        return [(const.CARDINALITY_SINGLE, _("Üksainus vastus")),
                (const.CARDINALITY_MULTIPLE, _("Järjekord pole oluline")),
                (const.CARDINALITY_ORDERED_SQ1, _("Õige järgnevus")),
                (const.CARDINALITY_ORDERED_POS, _("Järjekorranumber")),                
                ]

    rd_baseType = [('identifier', 'identifier'),
                   ('float', 'float'),
                   ('integer', 'integer'),
                   ('pair', 'pair'),
                   ('string', 'string'),
                   ]
    baseType = [('boolean', 'boolean'),
                ('directedPair', 'directedPair'),
                ('duration', 'duration'),
                ('file', 'file'),
                ('float', 'float'),
                ('identifier', 'identifier'),
                ('integer', 'integer'),
                ('pair', 'pair'),
                ('point', 'point'),
                ('string', 'string'),
                ('uri', 'uri'),
                ]

    @property
    def tulemus_baseType(self):
        return [(const.BASETYPE_STRING, _("Tekst")),
                (const.BASETYPE_INTEGER, _("Täisarv")),
                (const.BASETYPE_FLOAT, _("Reaalarv")),
                ]

    @property
    def tulemus_baseType_formula(self):
        return [(const.BASETYPE_STRING, _("Tekst")),
                (const.BASETYPE_INTEGER, _("Täisarv")),
                (const.BASETYPE_FLOAT, _("Reaalarv")),
                (const.BASETYPE_BOOLEAN, _("Tõeväärtus")),
                ]

    @property
    def tulemus_baseType_arv(self):
        return [(const.BASETYPE_INTEGER, _("Täisarv")),
                (const.BASETYPE_FLOAT, _("Reaalarv")),
                ]

    @property
    def shape(self):
        return [('rect', _("Ristkülik")),
                ('circle', _("Ring")),
                ('ellipse', _("Ellips")),
                ('poly', _("Polügoon")),
                ]
    @property
    def shape_free(self):
        return [('rect', _("Ristkülik")),
                ('circle', _("Ring")),
                ('ellipse', _("Ellips")),
                ('poly', _("Polügoon")),
                ('freehand', _("Vabakäsi")),             
                ]

    @property
    def tools(self):
        return [('rect', _("Ristkülik")),
                ('circle', _("Ring")),
                ('ellipse', _("Ellips")),
                ('poly', _("Polügoon")),
                ('polyline', _("Murdjoon")),             
                ('line', _("Joon")),
                ('ray', _("Kiir")),                
                ('freehand',  _("Vabakäsi")),
                ('text', _("Tekst"))]

    @property
    def tools_line(self):
        return [('polyline', _("Murdjoon")),             
                ('line', _("Joon")),
                ('ray', _("Kiir")),                
                ('freehand',  _("Vabakäsi")),
                ]

    @property
    def suund(self):
        "Ristsõna sõna suund"
        return [(const.DIRECTION_DOWN, _("alla")),
                (const.DIRECTION_UP, _("üles")),
                (const.DIRECTION_RIGHT, _("paremale")),
                (const.DIRECTION_LEFT, _("vasakule")),
                ]
                 
    @property
    def mimetype_media(self):
        items = list(mimetypes.types_map.items())
        items.append(('.m4a', const.MIMETYPE_AUDIO_MPEG)) # oli olemas py2, pole enam py3 korral
        li = [(v, '%s (%s)' % (v,k)) for k,v in items \
              if v.startswith('video') \
              or v.startswith('audio') \
              or v == 'application/x-shockwave-flash']
        li.sort()
        return li

    @property
    def mimetype(self):
        items = list(mimetypes.types_map.items())
        li = [(v, '%s (%s)' % (v,k)) for k,v in items]
        li.sort()
        return li

    @property
    def arvuti_reg(self):
        return [(const.ARVUTI_REG_POLE, _("Pole vajalik")),
                (const.ARVUTI_REG_ON, _("On käimas")),
                (const.ARVUTI_REG_LUKUS, _("On lõppenud")),
                ]

    # objektiivselt hinnatava ylesande vastuste õige/vale sisestamise valik
    @property
    def oige_vale(self):
        return ((const.C_OIGE, _("+ (õige)")), 
                (const.C_VALE, _("- (vale)")),
                )


    @property
    def ckeditor_iconsets(self):
        # kataloog, mille all on pildifailid eraldi
        ckeditor_path = '/static/lib/ckeditor/src'
        iconsets = (
            (
                ('Cut', _("Lõika"),  ckeditor_path + '/plugins/clipboard/icons/cut.png'),
                ('Copy', _("Kopeeri"),  ckeditor_path + '/plugins/clipboard/icons/copy.png'),
                #('Paste', _(u"Aseta"),  ckeditor_path + '/plugins/clipboard/icons/paste.png'),
                #('PasteFromWord', _(u"Asetamine Wordist"),  ckeditor_path + '/plugins/pastefromword/icons/pastefromword.png'),
                #('PasteText', _(u"Asetamine tavalise tekstina"),  ckeditor_path + '/plugins/pastetext/icons/pastetext.png'),
            ),
            (
                ('Undo', _("Tagasivõtmine"),  ckeditor_path + '/plugins/undo/icons/undo.png'),
                ('Redo', _("Toimingu kordamine"),  ckeditor_path + '/plugins/undo/icons/redo.png'),
                ('Find', _("Otsi"),  ckeditor_path + '/plugins/find/icons/find.png'),
                ('Replace', _("Asenda"),  ckeditor_path + '/plugins/find/icons/replace.png'),
                ('SelectAll', _("Vali kõik"),  ckeditor_path + '/plugins/selectall/icons/selectall.png'),
                ('RemoveFormat', _("Vormingu eemaldamine"),  ckeditor_path + '/plugins/removeformat/icons/removeformat.png'),
            ),
            (
                ('Bold', _("Paks kiri"),  ckeditor_path + '/plugins/basicstyles/icons/bold.png'),
                ('Italic', _("Kursiiv"),  ckeditor_path + '/plugins/basicstyles/icons/italic.png'),
                ('Underline', _("Allajoonitud"),  ckeditor_path + '/plugins/basicstyles/icons/underline.png'),
                ('mathck', _("Matemaatika"),  ckeditor_path + '/plugins/mathck/icons/mathedit.png'),
                #('ckeditor_wiris_formulaEditor', _("MathType"),  ckeditor_path + '/plugins/ckeditor_wiris/icons/formula.png'),
                #('ckeditor_wiris_formulaEditorChemistry', _("ChemType"),  ckeditor_path + '/plugins/ckeditor_wiris/icons/chem.png'),
                ('Subscript', _("Alaindeks"),  ckeditor_path + '/plugins/basicstyles/icons/subscript.png'),
                ('Superscript', _("Ülaindeks"),  ckeditor_path + '/plugins/basicstyles/icons/superscript.png'),
                ('SupSub', _("Kohakuti üla- ja alaindeks"),  ckeditor_path + '/plugins/supsub/icons/supsub.png'),
                ('MatMultiply', _("Korrutamine"),  ckeditor_path + '/plugins/supsub/icons/matmultiply.png'),
                ('MatDivide', _("Jagamine"),  ckeditor_path + '/plugins/supsub/icons/matdivide.png'),
                ('MatFraction', _("Harilik murd"),  ckeditor_path + '/plugins/supsub/icons/matfraction.png'),
                ('ArrowUp', _("Arrow up"),  ckeditor_path + '/plugins/supsub/icons/arrowup.png'),
                ('ArrowDown', _("Arrow down"),  ckeditor_path + '/plugins/supsub/icons/arrowdown.png'),                                
            ),
            (
                ('NumberedList', _("Numberloend"),  ckeditor_path + '/plugins/list/icons/numberedlist.png'),
                ('BulletedList', _("Punktloend"),  ckeditor_path + '/plugins/list/icons/bulletedlist.png'),
                ('Outdent', _("Taande vähendamine"),  ckeditor_path + '/plugins/indent/icons/outdent.png'),
                ('Indent', _("Taande suurendamine"),  ckeditor_path + '/plugins/indent/icons/indent.png'),
                ('Blockquote', _("Plokktsitaat"),  ckeditor_path + '/plugins/blockquote/icons/blockquote.png'),
                ('CreateDiv', _("Div-konteineri loomine"),  ckeditor_path + '/plugins/div/icons/creatediv.png'),
            ),
            (
                ('JustifyLeft', _("Vasakjoondus"),  ckeditor_path + '/plugins/justify/icons/justifyleft.png'),
                ('JustifyCenter', _("Keskjoondus"),  ckeditor_path + '/plugins/justify/icons/justifycenter.png'),
                ('JustifyRight', _("Paremjoondus"),  ckeditor_path + '/plugins/justify/icons/justifyright.png'),
                ('JustifyBlock', _("Rööpjoondus"),  ckeditor_path + '/plugins/justify/icons/justifyblock.png'),
            ),
            (
                ('Image', _("Pilt"),  ckeditor_path + '/plugins/image/icons/image.png'),
                ('Table', _("Tabel"),  ckeditor_path + '/plugins/table/icons/table.png'),
                ('SpecialChar', _("Erimärgi sisestamine"),  ckeditor_path + '/plugins/specialchar/icons/specialchar.png'),
                ('eszett', _("ß sisestamine"),  ckeditor_path + '/plugins/eszett/icons/eszett.png'),
            ),
            (
                ('Format', _("Vorming"),  None),
                ('Font', _("Kiri"),  None),
                ('FontSize', _("Teksti suurus"),  None),
                ('lineheight', _("Reakõrgus"),  None),
                ('TextColor', _("Teksti värv"),  ckeditor_path + '/plugins/colorbutton/icons/textcolor.png'),
                ('BGColor', _("Tausta värv"),  ckeditor_path + '/plugins/colorbutton/icons/bgcolor.png'),
                ('Maximize', _("Maksimeerimine"), ckeditor_path + '/plugins/maximize/icons/maximize.png'),
            ),
            )
        return iconsets

    def get_ckeditor_icon_img(self, icon):
        for iconset in self.ckeditor_iconsets:
            for r_icon, r_title, r_img in iconset:
                if r_icon == icon:
                    return '<img src="%s" alt="%s" title="%s"/>' % (r_img, r_title, r_title)

    def get_ipunkt_icons(self):
        # ckeditori plugin ipunkt nupud
        data = [
            {'name': 'excl', 'value': '!'},
            {'name': 'question', 'value': '?'},
            {'name': 'dot', 'value': '.'},
            {'name': 'comma', 'value': ','},
            {'name': 'apost', 'value': "'"},
            {'name': 'minus', 'value': '-'},
            {'name': 'emdash', 'value': '—'},
            {'name': 'slash', 'value': '/'},
            {'name': 'colon', 'value': ':'},
            {'name': 'semicolon', 'value': ';'},
            {'name': 'bdquo', 'value': '„'},
            {'name': 'rdquo', 'value': '”'},
            {'name': 'quot', 'value': '"'},
            {'name': 'hellip', 'value': '…'},
            {'name': 'space', 'value': ' '}
            ]
        return data
                
    @property
    def math_iconsets(self):
        iconsets = (
            (
                ('fraction', _("Harilik murd")),
                ('square_root', _("Ruutjuur")),
                ('root', _("Juur")),
                ('superscript', _("Ülaindeks")),
                ('subscript', _("Alaindeks")),
                ('multiplication', _("Multiplication")),
                ('division', _("Division")),
                ('plus_minus', _("Plus-minus")),
                ('not_equal', _("Pole võrdne")),
                ('greater_equal', _("Suurem või võrdne")),
                ('less_equal', _("Väiksem kui")),
                ('greater_than', _("Suurem kui")),
                ('less_than', _("Väiksem kui")),
                ('int', _("Integraal")),
                ('indint', _("Määramata intergaal")),
                ('intersect', _("Ühisosa")),
                ('union', _("Ühend")),
                ('infty', _("Lõpmatus")),
                ('overrightarrow', _("Vektor")),
                ('sin', _("Siinus")),
                ('cos', _("Koosinus")),
                ('tan', _("Tangens")),
                ('arcsin', _("Arkussiinus")),
                ('arccos', _("Arkuskoosinus")),
                ('arctan', _("Arkustangens")),
                ('angle', _("Nurk")),
                ('comma', _("Koma")),
                ('parentheses', _("Sulud")),
                ('par_frac', _("Harilik murd sulgudes")),
                ('par_frac_sup', _("Harilik murd sulgudes ja astmega")),             
                ('text', _("Tekst")),
                ('alpha', _("Alfa")),
                ('beta', _("Beeta")),
                ('gamma', _("Gamma")),
                ('delta', _("Delta")),
                ('epsilon', _("Epsilon")),
                ('zeta', _("Dzeeta")),
                ('eta', _("Eeta")),
                ('theta', _("Teeta")),
                ('iota', _("Ioota")),
                ('kappa', _("Kapa")),
                ('lambda', _("Lambda")),
                ('mu', _("Müü")),
                ('nu', _("Nüü")),
                ('xi', _("Ksii")),
                ('pi', _("Pii")),
                ('rho', _("Roo")),
                ('sigma', _("Sigma")),
                ('tau', _("Tau")),
                ('upsilon', _("Üpsilon")),
                ('phi', _("Fii")),
                ('chi', _("Hii")),
                ('psi', _("Psii")),
                ('omega', _("Oomega")),
                ('Gamma', _("Gamma")),
                ('Delta', _("Delta")),
                ('Theta', _("Teeta")),
                ('Lambda', _("Lambda")),
                ('Xi', _("Ksii")),
                ('Pi', _("Pii")),
                ('Sigma', _("Sigma")),
                ('Upsilon', _("Üpsilon")),
                ('Phi', _("Fii")),
                ('Psi', _("Psii")),
                ('Omega', _("Oomega")),
            ),
        )
        return iconsets
            
    def get_googlecharts_metadata(self):
        from .googlecharts_metadata import get_charttypes
        return get_charttypes(self.handler, self.request)

    def lang_sort(self, lang):
        return lang_sort(lang)

    def sorted_lang(self, li):
        "Keelte listi sortimine"
        return sorted(li, key=lang_sort)

    def opt_kordmall(self, testiliik):
        "Testimiskorra mall"
        from .testimine.testimiskord import Testimiskord
        from .test.test import Test
        q = (SessionR.query(Testimiskord.id, Testimiskord.nimi, Test.id)
             .filter(Testimiskord.on_mall==True)
             .join(Testimiskord.test)
             .filter(Test.testityyp==const.TESTITYYP_EKK)
             .filter(Test.testiliik_kood==testiliik)
             .order_by(Test.nimi, Testimiskord.tahis))
        return [(tk_id, '%s (test %d)' % (tk_nimi, t_id)) for (tk_id, tk_nimi, t_id) in q.all()]

    def opt_konsmall(self, testiliik):
        "Testimiskorra mall"
        from .testimine.testimiskord import Testimiskord
        from .test.test import Test        
        q = (SessionR.query(Testimiskord.id, Testimiskord.nimi, Test.id)
             .filter(Testimiskord.on_mall==True)
             .join(Testimiskord.test)
             .filter(Test.testityyp==const.TESTITYYP_KONS)
             .filter(Test.testiliik_kood==testiliik)
             .order_by(Test.nimi, Testimiskord.tahis))
        return [(tk_id, '%s (kons %d)' % (tk_nimi, t_id)) for (tk_id, tk_nimi, t_id) in q.all()]

    def opt_klassid_ryhmad(self, koht):
        "Leitakse kooli klasside ja/või lasteaiarühmade valik"
        # kas on lasteaaed?
        from .koht.koolioppekava import Koolioppekava
        from .koht.ryhm import Ryhm
        li = []
        q = (SessionR.query(Koolioppekava.kavatase_kood)
             .filter_by(koht_id=koht.id))
        kavatasemed = [k for k, in q.all()]
        on_alus = const.E_OPPETASE_ALUS in kavatasemed
        log.debug(f'kavatasemed: {kavatasemed}')
        if on_alus:
            # lasteaia korral peab ryhmade loetelu uuendamiseks
            # uuendama õpilaste loetelu
            self.handler.c.user.uuenda_klass(koht.kool_id, None, None)

            # ryhmaliigid vt
            # http://enda.ehis.ee/avaandmed/rest/klassifikaatorid/ALUS_RYHMA_LIIK/1/JSON
            # rliigid = {"aiaruhm_3-6": "3 kuni 6 aastased lapsed",
            #            "aiaruhm_6-7": "6 kuni 7 aastased lapsed",
            #            "arendus": "arendusrühm", # (vaimse alaarenguga lastele)
            #            "eri": "erirühm", # (erihooldust ja -õpet vajavad lapsed)
            #            "hoiu": "lapsehoiurühm", # kuni 3a
            #            "kehapuudega": "kehapuudega laste rühm ",
            #            "koolieelik": "koolieelikute ettevalmistusrühm",
            #            "liit_uus": "liitrühm",
            #            "liitpuudega": "liitpuudega laste rühm",
            #            "meelepuudega": "meelepuudega laste rühm",
            #            "pa": "pervasiivsete arenguhäiretega rühm",
            #            "sobitus": "sobitusrühm", # (erivajadustega lapsed koos teiste lastega)
            #            "soime": "sõimerühm", # kuni 3a
            #            "tasandus": "tasandusrühm", # (kõnehälvetega ja spetsiifiliste arenguhäiretega lastele) 
            #            }
            q = (SessionR.query(Ryhm.id, Ryhm.nimi, Ryhm.liik)
                 .filter_by(koht_id=koht.id)
                 .order_by(Ryhm.nimi))
            for r_id, r_nimi, r_liik in q.all():
                # ryhma eristame klassidest r-tähega
                li.append((f'r{r_id}', r_nimi))

        if not on_alus or len(kavatasemed) > 1:
            # lisame ka klassid
            li.extend(const.EHIS_KLASS)
        return li

    def opt_feedbackdgm(self):
        return ((const.DGM_TUNNUSED1,
                 _("Õpilase taseme tulpdiagramm"),
                 _("Vertikaalne tulpdiagramm")),                
                (const.DGM_BARNP,
                 _("Õpilase tulemuse lintdiagramm"),
                 _("Horisontaalne tulpdiagramm")),
                (const.DGM_TUNNUSED2,
                 _("Grupi taseme tulpdiagramm"),
                 _("Virnastatud vertikaalne tulpdiagramm")),
                (const.DGM_TUNNUSED3,
                 _("Klasside ühe tunnuse taseme tulpdiagramm"),
                 _("Vertikaalne tulpdiagramm")),
                (const.DGM_KLASSYL,
                 _("Klassi tulemuste tulpdiagramm ülesannete kaupa"),
                 _("Vertikaalne tulpdiagramm")),                
                (const.DGM_HINNANG,
                 _("Grupi hinnanguküsimuse tulpdiagramm"),
                 _("Vertikaalne tulpdiagramm")),
                (const.DGM_GTBL,
                 _("Grupi tulemuste tabel"),
                 _("Tabel")),
                (const.DGM_KTBL,
                 _("Klasside tulemuste tabel"),
                 _("Tabel")),
                (const.DGM_OPYLTBL,
                 _("Õpilase tulemuste tabel"),
                 _("Tabel")),
                )

    def title_feedbackdgm(self, dname):
        for _dname, title, subtitle in self.opt_feedbackdgm():
            if _dname == dname:
                return title
    
