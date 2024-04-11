"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *

from .tulemus import Tulemus
from .kyslisa import Kyslisa

class Kysimus(EntityHelper, Base):
    """Küsimus, valikute kogum.
    Kui sisuplokk on tekst, siis küsimus on tekstis olev lünk.
    Kui sisuplokk on sobitusplokk, siis küsimus on valikuhulk.    
    Kui on piltide lohistamise sisuplokk, siis küsimus vastab ühele lohistatavale pildile.
    """
    ASEND_PAREMAL = 0 
    ASEND_PAREMAL_S = 10 # paremal sticky
    ASEND_ALL = 1
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood = Column(String(100)) # vastuse muutuja, QTI responseIdentifier (puudub kolme hulga sobitamises teises hulgas, kahe hulga sobitamises valikute küsimustes 1 ja 2, pangaga lünga valikute küsimuses)
    seq = Column(Integer) # järjekorranumber: kui kysimus on valikuhulk, siis väärtus on 1 või 2 (või 3 või ...)
    selgitus = Column(String(255)) # selgitus    
    sisuplokk_id = Column(Integer, ForeignKey('sisuplokk.id'), index=True) # viide sisuplokile
    sisuplokk = relationship('Sisuplokk', foreign_keys=sisuplokk_id, back_populates='kysimused')
    sisuobjekt_id = Column(Integer, ForeignKey('sisuobjekt.id'), index=True) # viide küsimusega seotud sisuobjektile nendes ülesandetüüpides: piltide lohistamine (pos), tekstide lohistamine (txpos), piltide lohistamine II (pos2), ristsõna (crossword), multimeedia (media)
    sisuobjekt = relationship('Sisuobjekt', back_populates='kysimused')
    objseq = Column(Integer, sa.DefaultClause('1'), nullable=False) # sisuobjektiga seotud küsimuse tähendus: 1=const.OBJSEQ_K - tavaline küsimus; 2=const.OBJSEQ_COUNTER - multimeedia kuulamiste loendur; 3=const.OBJSEQ_POS - multimeedia mängimise järg
    vastusesisestus = Column(Integer) # p-testi vastuste sisestamiseks kasutatav viis: 1 - sarnane sooritajaga
    pseudo = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on pseudoküsimus (ei arvestata valede/õigete vastuste arvu)
    segamini = Column(Boolean) # kas segada valikud (QTI shuffle)
    max_vastus = Column(Integer) # max vastuste arv (QTI maxAssociations, maxStrings)
    max_vastus_arv = Column(Integer) # arvutatud max võimalik vastuste arv
    min_vastus = Column(Integer) # min vastuste arv (QTI minAssociations, minStrings)
    rtf = Column(Boolean) # kas valikute sisestamisel kasutada kirevat toimetit
    rtf_notshared = Column(Boolean) # kas nupuriba on lahtri sees (või ühine, mitme lahtri vahel jagatud)
    rtf_enter = Column(String(1)) # kireva teksti korral: 1=const.RTF_ENTER_P - reavahetus teeb uue lõigu; 2=const.RTF_ENTER_BR - reavahetus teeb uue rea
    
    # Text
    pikkus = Column(Integer) # avatud lünga pikkus; ristsõna sõna pikkus
    max_pikkus = Column(Integer) # avatud lünga vastuse või avatud vastusega küsimuse maksimaalne pikkus 
    reakorgus = Column(Float) # rea kõrgus avatud lüngas
    ridu = Column(Integer) # avatud lünga korral ridade arv; järjestamise korral: 1 - ühel real; muidu - üksteise all; piltide lohistamise korral: 1 - pildid kuvatakse tausta kõrval; muidu - pildid kuvatakse tausta all; pangaga lünkteksti korral: 2 - pangast saab lohistada kõikide sõnade vahele ja lünki lahendajale ei kuvata; sobitamise valikutehulga 1 korral: küsimuste hulga seq (1 või 2), teine hulk on valikute hulk; muidu - pangast saab lohistada ainult lünkadesse
    mask = Column(String(256)) # avatud lünga mask
    pos_x = Column(Integer) # ristsõna ja avatud pildi korral: mitmes veerg
    pos_y = Column(Integer) # ristsõna ja avatud pildi korral: mitmes rida
    vorming_kood = Column(String(15)) # avatud lünga vorming
    vihje = Column(String(256)) # vihje, mis kuvatakse lahendajale enne vastuse sisestamist
    algvaartus = Column(Boolean) # true - vihje jääb vastuse algväärtuseks; false - vihjet kuvatakse ainult tühjal väljal, kuni selles pole kursorit
    laad = Column(String(256)) # atribuudi style väärtus avatud lünga korral
    joondus = Column(String(10)) # teksti joondus lüngas: left=const.JUSTIFY_LEFT - vasak; center=const.JUSTIFY_CENTER - kesk; right=const.JUSTIFY_RIGHT - parem; justify=const.JUSTIFY_BLOCK - rööp; ristsõna sõnaseletuse korral suund, kuhupoole jääb sõna: left=const.DIRECTION_LEFT - vasakule; down=const.DIRECTION_DOWN - alla; right=const.DIRECTION_RIGHT - paremale; up=const.DIRECTION_UP - üles
    n_asend = Column(Integer) # nupurea asend (matemaatika sisestamise korral), panga asend (pangaga lünga korral): 0 - paremal; 1 ja NULL - all; 10 - paremal ja liigub kursoriga kaasa
    sonadearv = Column(Boolean) # kas kokku lugeda ja kuvada vastuses olevate sõnade arv
    tekstianalyys = Column(Boolean) # avatud vastusega küsimuse korral: kas hindajale kuvatakse eestikeelse teksti analüüs (EstNLTK)
    kyslisa = relationship('Kyslisa', uselist=False, back_populates='kysimus')
    joonistamine = relationship('Joonistamine', uselist=False, back_populates='kysimus')
    erand346 = Column(Boolean) # miinuspunkte ei anta juhul, kui on kaks vastust, millest üks on õige ja teine on vale (suur erand EH-346, kasutusel pangaga lüngas)
    hindaja_markused = Column(Boolean) # kas hindaja saab teksti sisse märkida vigu ja kommentaare (ksmarkus)
    vastus_taisekraan = Column(Boolean) # kas vastuse vaatajal ja hindajal on täisekraani (maksimeerimise) nupp

    _parent_key = 'sisuplokk_id'
    trans = relationship('T_Kysimus', cascade='all', back_populates='orig')
    valikud = relationship('Valik', order_by='Valik.seq', back_populates='kysimus')
    valikvastused1 = relationship('Valikvastus', foreign_keys='Valikvastus.valik1_kysimus_id', cascade='all', back_populates='valik1')
    valikvastused2 = relationship('Valikvastus', foreign_keys='Valikvastus.valik2_kysimus_id', cascade='all', back_populates='valik2')
    
    tulemus_id = Column(Integer, ForeignKey('tulemus.id'), index=True) # viide vastuste hindamise kirjele
    tulemus = relationship('Tulemus', foreign_keys=tulemus_id, back_populates='kysimused')
    oigsus_tulemused = relationship('Tulemus', foreign_keys='Tulemus.oigsus_kysimus_id', cascade='save-update,merge,refresh-expire', back_populates='oigsus_kysimus') # kysimused, mida hinnatakse ja mille vastus värvitakse antud kysimusega
    evast_edasi = Column(Boolean) # kas vastus kandub edasi kasutamiseks alatesti järgmistes ülesannetes
    evast_kasuta = Column(Boolean) # kas kasutada varasemast edasi kantud vastuseid vaikimisi algseisuna
    muutmatu = Column(Boolean) # kas lahendajal ei lasta vastust muuta (kasutusel juhul, kui evast_kasuta=true)
    ei_arvesta = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas arvestastada vastust tulemustes (true - õpipädevustesti tulemuste vaates seda vastust ei kuvata)
    matriba = Column(Text) # lahendaja matemaatikaredaktori nupureal kuvatavate ikoonide nimed, komaeraldatud (kui küsimus ei kasuta üle kogu ülesande kehtivat nupuriba)
    peida_start = Column(Boolean) # kas peita alustamise nupp (heli salvestamise korral)
    peida_paus = Column(Boolean) # kas peita pausi nupp (heli salvestamise korral)
    peida_stop = Column(Boolean) # kas peita lõpetamise nupp (heli salvestamise korral)
    naita_play = Column(Boolean) # kas lahendamisel kuvada vastuse mahamängimise nupp (heli salvestamise korral)

    __table_args__ = (
        sa.UniqueConstraint('sisuobjekt_id','objseq'),
        )

    def on_vastatud(self):
        if self.id:
            from eis.model.eksam import Kysimusevastus
            q = (SessionR.query(sa.func.count(Kysimusevastus.id))
                 .filter(Kysimusevastus.kysimus_id==self.id)
                 )
            cnt = q.scalar()
            return cnt > 0

    @property
    def result(self):
        """Vormis vastuse välja nimi
        """
        return const.RPREFIX + self.kood

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .sisuplokk import Sisuplokk

        sisuplokk = self.sisuplokk or self.sisuplokk_id and Sisuplokk.get(self.sisuplokk_id)
        if sisuplokk:
            sisuplokk.logi('Küsimus %s %s %s' % (self.kood or '', self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    def delete_subitems(self):
        self.delete_eelvaade()
        Session.flush()
        self.delete_subrecords(['valikud',
                                ])
        from eis.model.testimine import Kysimusestatistika
        for kst in Session.query(Kysimusestatistika).filter_by(kysimus_id=self.id).all():
            kst.delete()
        from eis.model.eksam import Kysimusevastus
        q = Session.query(Kysimusevastus.id).filter_by(kysimus_id=self.id)
        if q.first():
            raise sa.exc.IntegrityError(q, {}, None)
        if self.kyslisa:
            self.kyslisa.delete()
        if self.joonistamine:
            self.joonistamine.delete()
        if self.tulemus:
            if len(self.tulemus.kysimused) == 1:
                self.tulemus.delete()

    def delete_eelvaade(self):
        from eis.model.testimine import Sooritus, Sooritaja
        from eis.model.eksam import Kvsisu, Kysimusevastus, Ylesandevastus
        # kustutame kysimuse ylesannete eelvaadetest
        q = (Session.query(Kvsisu)
             .filter(sa.exists().where(sa.and_(
                 Kvsisu.kysimusevastus_id==Kysimusevastus.id,
                 Kysimusevastus.kysimus_id==self.id,
                 Kysimusevastus.ylesandevastus_id==Ylesandevastus.id,
                 Ylesandevastus.sooritus_id==None)))
             )
        q.delete(synchronize_session='fetch')        

        q = (Session.query(Kysimusevastus)
             .filter(Kysimusevastus.kysimus_id==self.id)
             .filter(sa.exists().where(sa.and_(
                 Kysimusevastus.ylesandevastus_id==Ylesandevastus.id,
                 Ylesandevastus.sooritus_id==None)))
             )
        q.delete(synchronize_session='fetch')        

        # kustutame kysimuse testide eelvaadetest
        q = (Session.query(Kvsisu)
             .filter(sa.exists().where(sa.and_(
                 Kvsisu.kysimusevastus_id==Kysimusevastus.id,
                 Kysimusevastus.kysimus_id==self.id,
                 Kysimusevastus.ylesandevastus_id==Ylesandevastus.id,
                 Ylesandevastus.sooritus_id==Sooritus.id,
                 Sooritus.sooritaja_id==Sooritaja.id,
                 Sooritaja.regviis_kood==const.REGVIIS_EELVAADE)))
             )
        q = (Session.query(Kysimusevastus)
             .filter(Kysimusevastus.kysimus_id==self.id)
             .filter(sa.exists().where(sa.and_(
                 Kysimusevastus.ylesandevastus_id==Ylesandevastus.id,
                 Ylesandevastus.sooritus_id==Sooritus.id,
                 Sooritus.sooritaja_id==Sooritaja.id,
                 Sooritaja.regviis_kood==const.REGVIIS_EELVAADE)))
             )
        q.delete(synchronize_session='fetch')                
        
    def gen_kood(self, default_kood=None):
        from .sisuplokk import Sisuplokk
        from .ylesanne import Ylesanne
        
        if not self.kood:
            sisuplokk = self.sisuplokk or self.sisuplokk_id and Sisuplokk.get(self.sisuplokk_id)
            if not sisuplokk:
                return
            ylesanne = sisuplokk.ylesanne or sisuplokk.ylesanne_id and Ylesanne.get(sisuplokk.ylesanne_id)
            if not ylesanne:
                return
            self.kood = ylesanne.gen_kysimus_kood(default_kood)
        return self.kood

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['valikud','trans'])
        cp.tulemus_id = None
        if self.kyslisa:
            rcd_cp = self.kyslisa.copy()
            cp.kyslisa = rcd_cp
        if self.joonistamine:
            rcd_cp = self.joonistamine.copy()
            cp.joonistamine = rcd_cp
        if self.tulemus:
            cp.tulemus = cp_t = self.tulemus.copy()
            cp_t.oigsus_kysimus_id = None
            cp_t.ylesanne_id = None
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        if self.kyslisa:
            li.extend(self.kyslisa.pack(delete, modified))
        if self.joonistamine:
            li.extend(self.joonistamine.pack(delete, modified))
        for rcd in self.valikud:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def list_kood1(self):
        tyyp = self.sisuplokk.tyyp
        if tyyp == const.INTER_GAP:
            return [v.kood for v in self.sisuplokk.kysimus.valikud]
        else:
            return [v.kood for v in self.valikud]

    def list_kood2(self):
        tyyp = self.sisuplokk.tyyp
        if tyyp == const.INTER_MATCH2:
            k = self.sisuplokk.get_kysimus(seq=2)
            return [v.kood for v in k.valikud]
        elif tyyp == const.INTER_MATCH3:
            k = self.sisuplokk.get_kysimus(seq=2)
            return [v.kood for v in k.valikud]        
        else:
            return [v.kood for v in self.valikud]

    @property
    def valikud_opt(self):
        return [(v.kood, v.get_sisestusnimi(self.rtf)) for v in self.valikud]

    def get_valik(self, kood):
        for v in self.valikud:
            if v.kood == kood:
                return v

    def set_seq(self):
        if self.seq is None:
            self.seq = self.get_seq()

    def best_entries(self, correct=False):
        """Leiame vastused, mille korral saaks kõige rohkem hindepalle.
        """
        if self.tulemus:
            from eis.model.ylesanne.sisuplokk import Sisuplokk
            sisuplokk = self.sisuplokk or Sisuplokk.get(self.sisuplokk_id)
            if sisuplokk.tyyp in (const.INTER_ORDER, const.INTER_GR_ORDER):
                if sisuplokk.tyyp == const.INTER_GR_ORDER:
                    max_vastus = self.max_vastus
                else:
                    max_vastus = len(self.valikud)
                results = {}
                max_mx_pallid = None
                # leiame parima tulemuse andva hindamismaatriksi
                for n_mx, hm_read in self.tulemus.get_maatriksid():
                    hm_read = hm_read[:max_vastus]
                    mx_pallid = sum([hm.pallid for hm in hm_read])
                    if max_mx_pallid is None or max_mx_pallid < mx_pallid:
                        max_mx_pallid = mx_pallid
                        results = hm_read
                return results
            
            elif sisuplokk.tyyp == const.INTER_GR_GAP:
                # tuleb tagada, et üks valik ei saaks esineda rohkem, kui teda tegelikult on olemas
                # (kui üks valik võib olla mitmes kohas õige vastus, aga seda valikut esineb ainult üks,
                # siis tuleb ülejäänud välja jätta)

                # kysime esmalt kõik vastused ja hiljem jätame osad välja
                entries = self.tulemus.best_entries(None)
                # entries on [(piltobjekt.kood, valik.kood),...]

                # koostame dicti, milles on iga pildi kohta selle pildi lubatud esinemiste arv
                cnt_piltobjektid = {}
                for rcd in sisuplokk.piltobjektid:
                    cnt_piltobjektid[rcd.kood] = rcd.max_vastus or 1

                cnt_valikud = {} # piirkonnad
                for rcd in sisuplokk.kysimus.valikud:
                    if rcd.max_vastus:
                        cnt_valikud[rcd.kood] = rcd.max_vastus
                li = []
                n = 0
                for rcd in entries:
                    if rcd.korduv_tabamus:
                        tabamuste_arv = rcd.tabamuste_arv or self.max_vastus
                    else:
                        tabamuste_arv = 1
                    for seq in range(tabamuste_arv):
                        if self.max_vastus and n >= self.max_vastus:
                            # piisavalt palju vastuseid on juba koos
                            break
                        if rcd.kood1 not in cnt_piltobjektid:
                            # vigane hindamismaatriksi kirje, sellist pilti pole
                            break
                        if cnt_piltobjektid[rcd.kood1] == 0:
                            # seda pilti ei saa rohkem kordi kasutada
                            break
                        if cnt_valikud.get(rcd.kood2) == 0:
                            # sellesse piirkonda ei saa rohkem pilte lohistada
                            break

                        if rcd.kood2 in cnt_valikud:
                            cnt_valikud[rcd.kood2] -= 1
                        cnt_piltobjektid[rcd.kood1] -= 1
                        n += 1
                        li.append(rcd)
                    if self.max_vastus and n >= self.max_vastus:
                        # piisavalt palju vastuseid on juba koos
                        break                    
                return li

            elif sisuplokk.tyyp == const.INTER_POS:
                entries = self.tulemus.best_entries(self.max_vastus, correct)
                
                li = []
                n = 0
                for rcd in entries:
                    if rcd.korduv_tabamus:
                        tabamuste_arv = rcd.tabamuste_arv or self.max_vastus
                    else:
                        tabamuste_arv = 1
                    if n + tabamuste_arv <= (self.max_vastus or 1):
                        for seq in range(tabamuste_arv):
                            n += 1
                            li.append(rcd)
                    if self.max_vastus and n >= self.max_vastus:
                        # piisavalt palju vastuseid on juba koos
                        break
                return li
           
            elif sisuplokk.tyyp == const.INTER_PUNKT:
                # leiame õigete vastuste seast alamhulga,
                # kus yhe lynga kohta poleks mitut vastust
                entries = self.tulemus.best_entries(None, correct)
                max_vastus = self.max_vastus or self.max_vastus_arv or 1
                lyngad = []
                li = []
                n = 0
                for rcd in entries:
                    nseq = rcd.koordinaadid
                    if nseq not in lyngad:
                        lyngad.append(nseq)
                        li.append(rcd)
                        n += 1
                        if n >= max_vastus:
                            break
                return li
           
            elif sisuplokk.tyyp == const.INTER_MATCH3:
                # arvestame eraldi hulkade 1 ja 2 vahelist maximumi
                # ja hulkade 2 ja 3 vahelist maximumi
                # ja valikute oma maximumi
                # NB! ei arvesta hindamismaatriksit 3
                entries = self.tulemus.best_entries(None, correct)
                li = []
                valikuhulk2 = sisuplokk.get_kysimus(seq=2)
                valikuhulk3 = sisuplokk.get_kysimus(seq=3)
                max1 = valikuhulk2.max_vastus
                max2 = valikuhulk3.max_vastus
                valikud1 = {v.kood: v.max_vastus for v in self.valikud if v.max_vastus is not None}
                valikud2 = {v.kood: v.max_vastus for v in valikuhulk2.valikud if v.max_vastus is not None}
                valikud3 = {v.kood: v.max_vastus for v in valikuhulk3.valikud if v.max_vastus is not None}
                cnt = cnt1 = cnt2 = 0
                for rcd in entries:
                    #log.debug('hm %s %s-%s (maatriks %s)' % (rcd.id, rcd.kood1, rcd.kood2, rcd.maatriks))
                    if rcd.maatriks == 1:
                        if max1 and max1 <= cnt1:
                            # hulkade 1 ja 2 vaheline max on täis
                            log.debug('hulkade 1 ja 2 vaheline max on täis: %s <= %s' % (max1, cnt1))
                            continue
                        left1 = valikud1.get(rcd.kood1)
                        left2 = valikud2.get(rcd.kood2)
                        if left1 == 0:
                            log.debug('valiku %s max on täis' % rcd.kood1)
                            continue
                        if left2 == 0:
                            log.debug('valiku %s max on täis' % rcd.kood2)
                            continue                        
                        if left1:
                            valikud1[rcd.kood1] = left1 - 1
                        if left2:
                            valikud2[rcd.kood2] = left2 - 1
                        cnt1 += 1
                    elif rcd.maatriks == 2:
                        if max2 and max2 <= cnt2:
                            # hulkade 1 ja 2 vaheline max on täis
                            log.debug('hulkade 1 ja 2 vaheline max on täis: %s <= %s' % (max2, cnt2))                            
                            continue
                        left2 = valikud2.get(rcd.kood1)
                        left3 = valikud3.get(rcd.kood2)
                        if left2 == 0:
                            log.debug('valiku %s max on täis' % rcd.kood1)
                            continue
                        if left3 == 0:
                            log.debug('valiku %s max on täis' % rcd.kood2)
                            continue                        
                        if left2:
                            valikud2[rcd.kood1] = left2 - 1
                        if left3:
                            valikud3[rcd.kood2] = left3 - 1
                        cnt2 += 1

                    # valik läheb arvesse
                    cnt += 1
                    li.append(rcd)
                    if self.max_vastus and self.max_vastus <= cnt:
                        # kogu max on täis
                        break
                return li
            else:
                return self.tulemus.best_entries(self.max_vastus, correct)
        else:
            return []

    def correct_entries(self):
        return self.best_entries(True)

    def give_tulemus(self, arvutihinnatav=None):
        from .ylesanne import Ylesanne
        if not self.tulemus:
            sisuplokk = self.sisuplokk
            ylesanne = sisuplokk.ylesanne or Ylesanne.get(sisuplokk.ylesanne_id)
            self.tulemus = Tulemus(ylesanne=ylesanne,
                                   kood=self.kood,
                                   arvutihinnatav=arvutihinnatav)
        return self.tulemus

    def give_kyslisa(self):
        if not self.kyslisa:
            self.kyslisa = Kyslisa(asend_paremal=True)
            self.kyslisa.kysimus = self
        return self.kyslisa

    def give_joonistamine(self):
        from .joonistamine import Joonistamine

        if not self.joonistamine:
            self.joonistamine = Joonistamine()
            self.joonistamine.kysimus = self
        return self.joonistamine

    def get_min_vastus(self):
        return self.min_vastus or 0

    def get_max_vastus(self):
        if self.max_vastus:
            return self.max_vastus
        sisuplokk = self.sisuplokk
        if sisuplokk.tyyp == const.INTER_INL_TEXT:
            return 1
        elif sisuplokk.tyyp == const.INTER_GAP:            
            return 1
        elif sisuplokk.tyyp == const.INTER_GR_GAP:
            cnt = 0
            for obj in sisuplokk.piltobjektid:
                cnt += obj.max_vastus or 1
            return cnt
        elif sisuplokk.tyyp == const.INTER_MCHOICE:
            valikuhulk = sisuplokk.get_baaskysimus(seq=2)
            return valikuhulk and len(valikuhulk.valikud) or 1
        elif sisuplokk.tyyp == const.INTER_MATCH3:
            valikuhulk1 = sisuplokk.get_kysimus(seq=1)
            if valikuhulk1.ridu == 0:
                return len(self.valikud) or 1
            else:
                valikuhulk3 = sisuplokk.get_kysimus(seq=3)
                return len(valikuhulk1.valikud) + len(valikuhulk3.valikud)
        elif sisuplokk.tyyp == const.INTER_PUNKT:
            return self.max_vastus_arv
        return len(self.valikud) or 1
        
    @property
    def gap_lynkadeta(self):
        # pangaga lynga korral: kas on lohistamine igale poole või ainult lynkadesse
        return self.ridu == 2

