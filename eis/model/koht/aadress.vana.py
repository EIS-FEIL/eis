# -*- coding: utf-8 -*-
# $Id: aadress.py 1096 2017-01-11 06:17:05Z ahti $

from eis.model.entityhelper import *

class Aadress(EntityHelper, Base):
    """Isiku või koha aadress
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood1 = Column(String(4)) # 1. taseme komponent - maakond
    kood2 = Column(String(4)) # 2. taseme komponent - omavalitsus
    kood3 = Column(String(4)) # 3. taseme komponent - asustusüksus
    kood4 = Column(String(4)) # 4. taseme komponent - väikekoht
    kood5 = Column(String(4)) # 5. taseme komponent - liikluspind
    kood6 = Column(String(4)) # 6. taseme komponent - nimi
    kood7 = Column(String(4)) # 7. taseme komponent - aadressnumber
    kood8 = Column(String(4)) # 8. taseme komponent - hoone osa
    normimata = Column(String(200)) # normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil
    tais_aadress = Column(String(200)) # täisaadress tekstina
    lahi_aadress = Column(String(200)) # lähiaadress tekstina
    adr_id = Column(Integer) # aadressi identifikaatori ADSis, kui aadress on ADSist üles leitud
    staatus = Column(Integer, nullable=False) # olek: 0=const.A_STAATUS_PUUDUB - aadress on sisestamata; 1=const.A_STAATUS_N_TEGEMATA - aadress on sisestatud, kuid selle vastet ADSis ei ole veel otsitud; 2=const.A_STAATUS_N_LUHTUS - ADSist ühest vastet ei leitud; 3=const.A_STAATUS_N_TEHTUD - ADSi vaste on leitud; 4=const.A_STAATUS_N_KEHTETU - ADSis kehtetu;
    leitud = Column(Integer) # mitu aadressi ADSist leiti
    meetod = Column(String(12)) # millise teenuse abil ADSi aadress leiti (kompotsing, normal, tekstotsing)
    teade = Column(String(200)) # viimasel normaliseerimisel saadud teade
    kasutaja = relationship('Kasutaja', uselist=False, back_populates='aadress') # viide kasutajale, kui on kasutaja aadress
    koht = relationship('Koht', uselist=False, back_populates='aadress') # viide kohale, kui on koha aadress

    KOOD2_TALLINN = '784'
    KOOD2_TARTU = '795'
    KOOD2_NARVA = '511'
    KOOD2_PARNU = '625'

    @property
    def maakond(self):
        return self.get_kood_nimetus(1)

    @property
    def vald(self):
        return self.get_kood_nimetus(2)

    @property
    def vald_liigita(self):
        return self.get_kood_nimetus(2, liigita=True)

    @property
    def asustusyksus(self):
        return self.get_kood_nimetus(3)

    @property
    def asustusyksus_liigita(self):
        return self.get_kood_nimetus(3, liigita=True)

    def get_kood_nimetus(self, tase, liigita=False):
        from .aadresskomponent import Aadresskomponent
        kood = self.__getattr__('kood%s' % tase)
        if kood:
            return Aadresskomponent.get_str_by_tase_kood(tase, kood, liigita)

    def from_form(self, data, prefix='', handler=None):
        """Aadress salvestatakse postitatud vormilt"""
        
        modified = False
        
        normimata = data.get('%snormimata' % prefix)
        if self.normimata != normimata:
            self.normimata = normimata
            modified = True

        koodid = [None] * 8
        for tasekood in data.get(prefix+'kood'):
            if tasekood:
                tase, kood = tasekood.split('.')
                tase = int(tase)
                koodid[tase-1] = kood
        for tase in range(1,9):
            key = 'kood%d' % tase
            if self.__getattr__(key) != koodid[tase-1]:
                self.__setattr__(key, koodid[tase-1])
                modified = True

        if modified:
            self.need_normal()
                
        if not self.kood1 and not self.normimata:
            # aadress puudub
            self.staatus = const.A_STAATUS_PUUDUB

        if handler and modified and self.normimata:
            # teeme kohe normaliseerimise ADSis
            from eis.lib.xtee import ads
            reg = ads.Ads(handler=handler)
            try:
                ads.leia_ads_aadress(reg, self)
            except Exception as e:
                pass

        return modified

    def from_rr(self, data):
        """Aadress salvestatakse RRi vastusest
        """
        
        modified = False
        
        kood1 = data.get('maakond_id')
        kood2 = data.get('vald_id')
        kood3 = data.get('asula_id')
        normimata = data.get('aadress')

        if kood1 or kood2 or kood3 or normimata:
            if self.normimata != normimata or \
                    self.kood1 != kood1 or \
                    self.kood2 != kood2 or \
                    self.kood3 != kood3:
                self.normimata = normimata
                self.kood1 = kood1
                self.kood2 = kood2
                self.kood3 = kood3
                self.kood4 = None
                self.kood5 = None
                self.kood6 = None
                self.kood7 = None
                self.kood8 = None

                # RR ei anna ADSi koode, aadress tuleb uuesti normaliseerida
                self.need_normal()
                
        if self.puudub:
            # aadress puudub
            self.staatus = const.A_STAATUS_PUUDUB

    def from_ehak(self, ehak):
        """EHAKi asula koodist tuletatakse kood1,kood2,kood3
        """
        from .aadresskomponent import Aadresskomponent
        q = Aadresskomponent.query.filter(Aadresskomponent.tase<=3)
        try:
            n_ehak = int(ehak)
        except:
            q = q.filter_by(kood=ehak)
        else:
            if n_ehak < 1000:
                koodid = ['%04d' % n_ehak, '%03d' % n_ehak]
                if n_ehak < 100:
                    koodid.append('%02d' % n_ehak)
                q = q.filter(Aadresskomponent.kood.in_(koodid))
            else:
                q = q.filter_by(kood=ehak)

        r = q.first()
        if r:
            komp3 = komp2 = komp1 = None
            if r.tase == 3:
                komp3 = r
            elif r.tase == 2:
                self.kood3 = None
                komp2 = r
            elif r.tase == 1:
                self.kood2 = None
                komp1 = r

            if komp3:
                self.kood3 = komp3.kood
                komp2 = komp3.ylem
            if komp2:
                self.kood2 = komp2.kood
                komp1 = komp2.ylem
            if komp1:
                self.kood1 = komp1.kood
            return r.tase

    @property
    def puudub(self):
        return not self.kood1 and not self.normimata

    def need_normal(self):
        "Märgime kirje normaliseerimist vajavaks"
        self.adr_id = self.leitud = self.meetod = None
        self.tais_aadress, self.lahi_aadress = self.str_aadress(True)
        self.staatus = const.A_STAATUS_N_TEGEMATA
        self.teade = None

    def from_koodaadress(self, koodaadress):
        """Komponendid eraldatakse koodaadressilt"""
        # koodaadressil on 29 kohta komponentidele + 4 kohta versioonile
        assert len(koodaadress) >= 29, 'Koodaadress liiga lühike'
        pos1 = 0
        for n in range(1,9):
            if n == 1:
                pos2 = pos1 + 2
            elif n == 2:
                pos2 = pos1 + 3
            else:
                pos2 = pos1 + 4
            kood = koodaadress[pos1:pos2]
            if kood == '00' or kood == '000' or kood == '0000':
                kood = None
            self.__setattr__('kood%d' % n, kood)
            pos1 = pos2

    def str_aadress(self, lahi=False, ainult_lahi=False):
        """Aadress teisendatakse tekstiks, funktsioon need_normal paigutab tulemuse 
        väljadele tais_aadress ja lahi_aadress.
        Aadressi jooksvaks kasutamiseks tuleks kasutada neid välju, mitte seda funktsiooni.
        """
        from .aadresskomponent import Aadresskomponent

        def get_nimi(tase, kood):
            rcd = Aadresskomponent.get_by_tase_kood(tase, kood)
            return rcd and rcd.nimetus_liigiga or ''

        lahiaadress = ''
        taisaadress = ''
        
        if self.kood4:
            lahiaadress += ', ' + get_nimi(4, self.kood4)
        if self.kood5:
            lahiaadress += ', ' + get_nimi(5, self.kood5)
        if self.kood6:
            lahiaadress += ', ' + get_nimi(6, self.kood6)
        if self.kood7:
            lahiaadress += ' ' + get_nimi(7, self.kood7)
        if self.kood8:
            lahiaadress += '-' + get_nimi(8, self.kood8)

        if self.normimata:
            lahiaadress += ' ' + self.normimata

        lahiaadress = lahiaadress.strip(', -')

        if ainult_lahi:
            return lahiaadress

        if self.kood1:
            taisaadress += get_nimi(1, self.kood1)
        if self.kood2:
            taisaadress += ', ' + get_nimi(2, self.kood2)
        if self.kood3:
            taisaadress += ', ' + get_nimi(3, self.kood3)

        if lahiaadress:
            taisaadress += ', ' + lahiaadress

        taisaadress = taisaadress.strip(', -')

        if lahi:
            return taisaadress, lahiaadress
        else:
            return taisaadress

    def li_print_aadress(self):
        """Tagastame listi prinditava aadressi ridadest
        """
        li = [] 
        if self.kasutaja:
            postiindeks = self.kasutaja.postiindeks
        elif self.koht:
            postiindeks = self.koht.postiindeks
        else:
            postiindeks = None

        if self.lahi_aadress:
            li.append(self.lahi_aadress)
            asula = self.asustusyksus
            vald = self.vald
            maakond = self.maakond
            if asula:
                li.append(asula)
            if vald:
                li.append(vald)
            if maakond and postiindeks:
                li.append('%s %s' % (postiindeks, maakond))
            elif maakond:
                li.append(maakond)
            elif postiindeks:
                li.append(postiindeks)

        elif self.tais_aadress:
            li.append(self.tais_aadress)
            if postiindeks:
                li.append(postiindeks)

        elif self.kood4 or self.kood5 or self.normimata:
            li_lahi = []
            if self.normimata:
                li_lahi.append(self.normimata)
            for n in range(4, 9):
                nimetus = self.get_kood_nimetus(n)
                if nimetus:
                    li_lahi.append(nimetus)
            li.append(' '.join(li_lahi))

            asula = self.asustusyksus
            vald = self.vald
            maakond = self.maakond
            if asula:
                li.append(asula)
            if vald:
                li.append(vald)
            if maakond and postiindeks:
                li.append('%s %s' % (postiindeks, maakond))
            elif maakond:
                li.append(maakond)
            elif postiindeks:
                li.append(postiindeks)
            
        return li

    def log_update(self):
        "Koha aadressi muudatused kantakse koha logisse"

        from .aadresskomponent import Aadresskomponent
        if not self.koht:
            # pole koha aadress
            return

        for key, old_value in self._sa_instance_state.committed_state.items():
            if key == 'tais_aadress':
                new_value = self.__getattr__(key)
                
                if isinstance(old_value, str):
                    old_value = old_value.strip()
                if isinstance(new_value, str):
                    new_value = new_value.strip()

                if isinstance(old_value, sa.util.langhelpers._symbol):
                    old_value = None
                if isinstance(new_value, sa.util.langhelpers._symbol):
                    new_value = None

                if type(old_value) == type(new_value):
                    changed = old_value != new_value
                else:
                    changed = str(old_value) != str(new_value)

                if changed:
                    self.koht._append_log('aadress', old_value, new_value)
