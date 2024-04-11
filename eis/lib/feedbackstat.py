import sqlalchemy as sa
import operator
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.model import Tagasisidevorm
from .feedbackdgm import FeedbackDgmBarnp
_ = i18n._

class FeedbackStat:
    "Filtri tingimused, mis määravad, milliste soorituste kohta tagasiside genereeritakse"
    
    def __init__(self, liik, lang, test_id, sooritaja, testimiskord_id=None, testimiskorrad_id=None, kool_koht_id=None, kand_koht_id=None, klass=None, paralleel=None, nimekiri_id=None, opetajad_id=None, sooritajad_id=None, testiruum_id=None, kursus=None, klassidID=None, valimis=None, piirkond_id=None, format='html'): 
        self.format = format
        self.is_pdf = format == 'pdf'
        self.is_xls = format == 'xls'
        self.liik = liik
        self.lang = lang
        self.valimis = valimis
        self.test_id = test_id
        if testimiskord_id:
            # argument on kasutusel siis, kui on parajasti yks testimiskord
            testimiskorrad_id = [testimiskord_id]
        self.testimiskorrad_id = testimiskorrad_id
        self.testimiskord_id = testimiskorrad_id and len(testimiskorrad_id) == 1 and testimiskorrad_id[0]
        # valimi tingimused
        # testimiskorrasisene valim
        self.sis_valim_tk_id = None
        # statistikas arvestatavate valimi testimiskordade ID
        self.valimid_tk_id = None
        # kas kõik statistikas arvestatavad valimid on avaldet
        self.v_avaldet = self.new_avaldet()

        # oma maakonna ja 4 suurema linna päringus seadmiseks
        self.maakond_kood = None
        self.linn_kood = None
        self.piirkond_id = piirkond_id
        self.kool_koht_id = kool_koht_id
        self.kand_koht_id = kand_koht_id
        self.klassidID = klassidID
        if klassidID and len(klassidID) == 1:
            k = klassidID[0]
            self.klass = k.klass
            self.paralleel = k.paralleel
        else:
            self.klass = klass
            self.paralleel = paralleel

        self.nimekiri_id = nimekiri_id
        self.opetajad_id = opetajad_id
        self.sooritajad_id = sooritajad_id
        self.sooritaja = sooritaja
        self.sooritaja_testimiskord_id = sooritaja and sooritaja.testimiskord_id or -1
        self.testiruum_id = testiruum_id
        self.kursus = kursus
        self._test = self._testimiskord = None
        self.from_stat = None

    @classmethod
    def new_avaldet(cls):
        "Luuakse objekt, milles saab hoida tulemuste avaldamise infot"
        class Avaldet:
            def __init__(self):
                # statistikas arvestatavate valimi testimiskordade avaldatus
                self.alatestitulemused_avaldet = None
                self.ylesandetulemused_avaldet = None
                self.aspektitulemused_avaldet = None
                self.koondtulemus_avaldet = None
                # statistikas mittearvestatavad avaldatud valimite testimiskorrad,
                # mille tulemusi siiski kuvatakse gtbl-is, kui erineb mittevalimist
                self.mittestat_valimid_tk_id = []
                
            def from_tk(self, tk):
                "Kindla testimiskorra avaldatus"
                if tk:
                    self.alatestitulemused_avaldet = tk.alatestitulemused_avaldet
                    self.ylesandetulemused_avaldet = tk.ylesandetulemused_avaldet
                    self.aspektitulemused_avaldet = tk.aspektitulemused_avaldet
                    self.koondtulemus_avaldet = tk.koondtulemus_avaldet
                return self
            
        return Avaldet()
    
    def stat_for(self, test_id, sooritaja, testimiskord_id=None):
        "Filtri tingimused samade sooritajate mingi muu testi soorituste kohta"
        stat2 = FeedbackStat(self.liik, self.lang, test_id, sooritaja,
                             testimiskord_id=testimiskord_id)
        stat2.from_stat = self
        return stat2
        
    @property
    def test(self):
        if not self._test and self.test_id:
            self._test = model.Test.getR(self.test_id)
        return self._test

    @property
    def testimiskord(self):
        if not self._testimiskord and self.testimiskord_id:
            self._testimiskord = model.Testimiskord.getR(self.testimiskord_id)
        return self._testimiskord

    def g_filter(self, q, group_type=None, valimis=None, mittestat=False):
        "Lisame päringule filtri grupi stat saamiseks"
        # group_type - grupi liik, vt const.FBR_*
        # valimis:
        #   None - kõik antud testimiskorra sooritajad
        #   False - mitte-valimi sooritajad antud testimiskorral
        #   True - valimi sooritajad (testimiskorra sisesel valimil
        #          või eraldatud testimiskorral)
        # mittestat - kas arvestada ka mittearvestatavaid valimeid 
        stat = self
        qf = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
              .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
              .filter(sa.or_(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD,
                             model.Sooritaja.pallid!=None)) # võib olla III hindamine pooleli, mis tulemust ei mõjuta
              .filter(model.Sooritaja.test_id==stat.test_id)
              )
        if stat.from_stat:
            # isikud määratakse teise testi sooritajate järgi (taustaküsitluses)
            # teise testi alampäring
            #from_q = model.Session.query(model.Sooritaja.kasutaja_id)
            #from_q = stat.from_stat.g_filter(from_q)
            #qf = qf.filter(model.Sooritaja.kasutaja_id.in_(from_q.subquery()))
            from_q = sa.select(model.Sooritaja.kasutaja_id)
            from_q = stat.from_stat.g_filter(from_q)
            qf = qf.filter(model.Sooritaja.kasutaja_id.in_(from_q))

        if stat.kursus:
            qf = qf.filter(model.Sooritaja.kursus_kood==stat.kursus)

        if valimis is None:
            # võib olla ette antud generate() argumendina
            valimis = stat.valimis
        if valimis is None:
            # kui pole ette antud, kas teha valimi päring, siis tehakse valimi päring
            # juhul, kui valim on olemas ja on linna või suurem grupp
            valim_types = (const.FBR_LINN, const.FBR_MAAKOND, const.FBR_RIIK, const.FBR_RIIK_PR)
            if (stat.sis_valim_tk_id or stat.valimid_tk_id) \
                   and group_type in valim_types:
                valimis = True
            else:
                valimis = None

        if valimis:
            # valimi tulemused
            li_tk_id = stat.valimid_tk_id or []
            if mittestat:
                # arvestada ka mittearvestatavaid valimeid
                li_tk_id = li_tk_id + (stat.v_avaldet.mittestat_valimid_tk_id or [])
            if li_tk_id:
                # eraldatud valimi testimiskord
                if len(li_tk_id) == 1:
                    tk_id = li_tk_id[0]
                    qf = qf.filter(model.Sooritaja.testimiskord_id==tk_id)
                else:
                    qf = qf.filter(model.Sooritaja.testimiskord_id.in_(li_tk_id))
            elif stat.sis_valim_tk_id:
                # testimiskorra sisene valim
                tk_id = stat.sis_valim_tk_id
                qf = qf.filter(model.Sooritaja.testimiskord_id==tk_id)
                qf = qf.filter(model.Sooritaja.valimis==True)
            else:
                # valim puudub
                qf = qf.filter(model.Sooritaja.testimiskord_id==-1)
        else:
            # algse testimiskorra tulemused
            if stat.testimiskord_id:
                qf = qf.filter(model.Sooritaja.testimiskord_id==stat.testimiskord_id)
            elif stat.testimiskorrad_id:
                qf = qf.filter(model.Sooritaja.testimiskord_id.in_(stat.testimiskorrad_id))
            if valimis == False:
                # otsitakse mitte-valimi sooritajaid
                qf = qf.filter(model.Sooritaja.valimis==False)
                
        if not group_type and model.Tagasisidevorm.is_individual(stat.liik):
            # õpilaste kaupa
            tk_id = stat.testimiskord_id or stat.sooritaja_testimiskord_id
            # õpilase korral kasutame kogu Eesti keskmist
            qf = qf.filter(model.Sooritaja.testimiskord_id==tk_id)
            return qf

        if not group_type or group_type == const.FBR_GRUPP:
            if stat.nimekiri_id:
                qf = qf.filter(model.Sooritaja.nimekiri_id==stat.nimekiri_id)
            if stat.testiruum_id:
                qf = qf.filter(model.Sooritaja.sooritused.any(
                    model.Sooritus.testiruum_id==stat.testiruum_id))

        if not group_type or group_type in (const.FBR_KOOL, const.FBR_KLASS, const.FBR_OPETAJA, const.FBR_GRUPP):
            if stat.kool_koht_id:
                qf = qf.filter(model.Sooritaja.kool_koht_id==stat.kool_koht_id)
            if stat.kand_koht_id:
                qf = qf.filter(model.Sooritaja.kandideerimiskohad.any(
                    model.Kandideerimiskoht.koht_id==stat.kand_koht_id))

        if not group_type or group_type in (const.FBR_KLASS, const.FBR_GRUPP):
            if stat.klassidID:
                fkl = None
                for klassID in stat.klassidID:
                    if klassID.paralleel:
                        fitem = sa.and_(model.Sooritaja.klass==klassID.klass,
                                        model.Sooritaja.paralleel==klassID.paralleel)
                    else:
                        fitem = model.Sooritaja.klass==klassID.klass

                    if stat.kand_koht_id:
                        # sisseastumiseksam
                        if klassID.klass == model.KlassID.KANDIDAADID:
                            # sisseastumiseksami korral kõik minu kooli kandideerivad
                            # (ei ole päris klass)
                            fitem = model.Sooritaja.kandideerimiskohad.any(
                                sa.and_(model.Kandideerimiskoht.koht_id==stat.kand_koht_id,
                                        model.Kandideerimiskoht.automaatne==False))
                        else:
                            # on päris klass, aga vaja on ainult oma kooli õpilasi
                            fitem = sa.and_(fitem, model.Sooritaja.kool_koht_id==stat.kand_koht_id)

                    if fkl is None:
                        fkl = fitem
                    else:
                        fkl = sa.or_(fkl, fitem)
                qf = qf.filter(fkl)
            else:
                if stat.klass:
                    qf = qf.filter(model.Sooritaja.klass==stat.klass)
                    qf = qf.filter(model.Sooritaja.paralleel==stat.paralleel)

        if not group_type or group_type in (const.FBR_OPETAJA, const.FBR_GRUPP):
            if stat.opetajad_id:
                if len(stat.opetajad_id) == 1:
                    qf = qf.filter(model.Sooritaja.testiopetajad.any(
                        model.Testiopetaja.opetaja_kasutaja_id==stat.opetajad_id[0]))
                else:
                    qf = qf.filter(model.Sooritaja.testiopetajad.any(
                        model.Testiopetaja.opetaja_kasutaja_id.in_(stat.opetajad_id)))

        if group_type == const.FBR_MAAKOND:
            qf = (qf.join(model.Sooritaja.kool_koht)
                  .join(model.Koht.aadress)
                  .filter(model.Aadress.kood1==stat.maakond_kood))

        elif group_type == const.FBR_LINN:
            qf = (qf.join(model.Sooritaja.kool_koht)
                  .join(model.Koht.aadress)
                  .filter(model.Aadress.kood1==stat.maakond_kood)
                  .filter(model.Aadress.kood2==stat.linn_kood))

        return qf
