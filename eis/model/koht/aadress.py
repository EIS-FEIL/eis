# -*- coding: utf-8 -*-

from eis.model.entityhelper import *

class Aadress(EntityHelper, Base):
    """Isiku või koha aadress
    """
    id = Column(Integer, primary_key=True) # ADR_ID
    kood1 = Column(String(4)) # 1. taseme komponent - maakond
    kood2 = Column(String(4)) # 2. taseme komponent - omavalitsus
    kood3 = Column(String(4)) # 3. taseme komponent - asustusüksus
    kood4 = Column(String(4)) # 4. taseme komponent - väikekoht
    kood5 = Column(String(4)) # 5. taseme komponent - liikluspind
    kood6 = Column(String(4)) # 6. taseme komponent - nimi
    kood7 = Column(String(4)) # 7. taseme komponent - aadressnumber
    kood8 = Column(String(4)) # 8. taseme komponent - hoone osa
    tais_aadress = Column(String(200)) # täisaadress tekstina
    lahi_aadress = Column(String(200)) # lähiaadress tekstina
    sihtnumber = Column(Integer) # sihtnumber
    staatus = Column(Integer, nullable=False) # olek: 0 - kehtetu; 1 - kehtiv
    ads_log_id = Column(Integer) # ADS muudatuse kirje logId
    uus_adr_id = Column(Integer) # kui kirje on tühistatud, siis kehtiva kirje ID
    
    KOOD2_TALLINN = '784'
    KOOD2_TARTU = '793' #'795'
    KOOD2_NARVA = '511'
    KOOD2_PARNU = '624' #'625'

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

    @classmethod
    def get_select2_opt(cls, text):
        LIMIT = 12
        #to_tsvector('english',tais_aadress) @@ plainto_tsquery('english',:text) "+
        q = (SessionR.query(Aadress.id, Aadress.tais_aadress)
             .filter(sa.func.to_tsvector('simple', Aadress.tais_aadress)
                     .op('@@')(sa.func.plainto_tsquery(text)))
             .filter(Aadress.staatus==const.B_STAATUS_KEHTIV)
             .order_by(Aadress.tais_aadress)
             .limit(LIMIT)
             )
        log_query(q)
        li = []
        for (a_id, tais_aadress) in q.all():
            li.append({'id': a_id,
                       'text': tais_aadress,
                       })
        return {'results': li}

    @classmethod
    def get_field_tase(cls, tase):
        fields = (Aadress.kood1,
                  Aadress.kood2,
                  Aadress.kood3,
                  Aadress.kood4,
                  Aadress.kood5,
                  Aadress.kood6,
                  Aadress.kood7,
                  Aadress.kood8)
        if 0 < tase < 9:
            return fields[tase - 1]
        
    @classmethod
    def adr_from_form(cls, obj, data, prefix=''):
        """Aadress salvestatakse postitatud vormilt"""
        obj.normimata = data.get(prefix + 'normimata')
        obj.aadress_id = data.get(prefix + 'adr_id')

    @classmethod
    def find_adr(cls, koodid, normimata=None):
        from .aadresskomponent import Aadresskomponent
        adr_id = None
        if normimata:
            li_normimata = [normimata]
        else:
            li_normimata = []
        for tase in range(8,0,-1):
            kood = koodid[tase-1]
            if kood:
                fields = [Aadress.kood1,
                          Aadress.kood2,
                          Aadress.kood3,
                          Aadress.kood4,
                          Aadress.kood5,
                          Aadress.kood6,
                          Aadress.kood7,
                          Aadress.kood8]
                q = SessionR.query(Aadress.id, Aadress.staatus, Aadress.uus_adr_id).filter(fields[tase-1]==kood)
                for field2 in fields[tase:]:
                    q = q.filter(field2==None)
                q = q.order_by(sa.desc(Aadress.staatus))
                for r in q.all():
                    adr_id, staatus, uus_adr_id = r
                    break
                if adr_id:
                    if staatus == const.B_STAATUS_KEHTETU and uus_adr_id:
                        if Aadress.get(uus_adr_id):
                            adr_id = uus_adr_id
                    break
                else:
                    nimi = Aadresskomponent.get_str_by_tase_kood(tase, kood, False)
                    li_normimata.insert(0, nimi)
        #log.debug('FIND_ADR %s / %s' % (adr_id, li_normimata))
        return adr_id, ' '.join(li_normimata)

    @classmethod
    def from_rr(cls, data):
        """Aadress salvestatakse RRi vastusest
        """
        kood1 = data.get('maakond_id')
        kood2 = data.get('vald_id')
        kood3 = data.get('asula_id')
        normimata = data.get('aadress')
        return cls.find_adr([kood1, kood2, kood3, None, None, None, None, None], normimata)

    @classmethod
    def from_ehak(cls, ehak, normimata=None):
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

        koodid = [None] * 8
        r = q.first()
        if r:
            tase = r.tase
            if tase == 3:
                koodid[2] = r.kood
                r = r.ylem
                tase = 2
            if tase == 2:
                koodid[1] = r.kood
                r = r.ylem
                tase = 1
            if tase == 1:
                koodid[0] = r.kood
        return cls.find_adr(koodid, normimata)

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

    def str_aadress(self, obj, lahi=False, ainult_lahi=False):
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

        if obj.normimata:
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

    def li_print_aadress(self, obj):
        """Tagastame listi prinditava aadressi ridadest
        """
        li = [] 
        postiindeks = obj.postiindeks
        buf = self.lahi_aadress or ''
        if obj.normimata:
            buf += ' ' + obj.normimata
        li.append(buf)
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

