from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from .koht import Koht
from .koolioppekava import Koolioppekava

class Aadresskomponent(Base):
    """Koopia aadressiandmete süsteemi (ADS) aadressikomponentide klassifikaatorist
    """
    __tablename__ = 'aadresskomponent'
    created = Column(DateTime) # kirje loomise aeg
    modified = Column(DateTime) # kirje viimase muutmise aeg
    id = Column(Integer, primary_key=True, autoincrement=True) 
    tase = Column(Integer, nullable=False) # komponendi tase: 1 - maakond; 2 - omavalitsus; 3 - asustusüksus; 4 - väikekoht (AÜ AK, GÜ); 5 - liikluspind (tee, tänav); 6 - nimi; 7 - aadressnumber (maja, krunt); 8 - hoone osa (number- ja/või tähtlisand)
    kood = Column(String(4), nullable=False) # komponendi kood, unikaalne taseme piires; tasemel 1 on 2 kohta; tasemel 2 on 3 kohta; tasemetel 3-8 on 4 kohta
    nimetus = Column(String(192), nullable=False) # nimetus
    nimetus_liigiga = Column(String(192), nullable=False) # nimetus liigiga
    ylemkomp_tase = Column(Integer) # ülemkomponendi tase
    ylemkomp_kood = Column(String(4)) # ülemkomponendi kood
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek: 1 - kehtiv; 0 - kehtetu
    ads_log_id = Column(Integer) # ADS muudatuse kirje logId
    __table_args__ = (
        sa.UniqueConstraint('tase','kood'),
        )

    @classproperty
    def query(cls):
        "Mugavusmeetod kirjet väljastava päringu alustamiseks"
        return SessionR.query(cls)

    def delete(self, *args, **kwargs):
        if self in Session.deleted:
            return False
        rc = Session.delete(self)
        return rc

    def log_delete(self):
        pass

    def log_update(self):
        pass

    def log_insert(self):
        pass

    def before_update(self):
        self.modified = datetime.now()
    
    def before_insert(self):
        self.created = datetime.now()
        self.modified = datetime.now()

    @property
    def ylem(self):
        if self.ylemkomp_kood:
            return self.get_by_tase_kood(self.ylemkomp_tase, self.ylemkomp_kood)

    @property
    def aadress(self):
        if self.ylem:
            return self.ylem.aadress + ', ' + self.nimi
        else:
            return self.nimi

    @property
    def tasekood(self):
        return '%s.%s' % (self.tase, self.kood)

    @classmethod
    def get_by_tasekood(cls, tasekood):
        tase, kood = tasekood.split('.')
        return cls.get_by_tase_kood(tase, kood)

    @classmethod
    def get_by_tase_kood(cls, tase, kood):
        return cls.query.\
            filter_by(tase=int(tase)).\
            filter_by(kood=kood).first()

    @classmethod
    def get_komp_from_rr(cls, data):
        """Rahvastikuregistrist saadud aadressiandmete struktuuri lisatakse komponendid ja täisaadress
        """
        from .aadress import Aadress
        adr_id = data['ADS_ADR_ID']
        aadress = adr_id and Aadress.get(adr_id)
        tasekoodid = []
        if aadress:
            data['taisaadress'] = aadress.tais_aadress
            data['normimata'] = ''
            data['adr_id'] = aadress.id;
            komponendid = (aadress.kood1,
                           aadress.kood2,
                           aadress.kood3,
                           aadress.kood4,
                           aadress.kood5,
                           aadress.kood6,
                           aadress.kood7,
                           aadress.kood8)
            for tase, kood in enumerate(komponendid):
                if kood:
                    tasekoodid.append('%s.%s' % (tase+1, kood))
        data['koodid'] = tasekoodid
        return data

    @classmethod
    def get_str_by_tase_kood(cls, tase, kood, liigita=False):
        if tase == 2 and kood == '784' and liigita:
            # ADS-is on Tallinna linn, peame panema nimetavasse
            return 'Tallinn'

        rcd = cls.get_by_tase_kood(tase, kood)
        if rcd:
            if liigita:
                # jätame lõpust ära liigi (küla, alevik, linn, alev, väikekoht, tn, tee)
                if tase <= 4:
                    return rcd.nimetus.rsplit(' ', 1)[0]
                return rcd.nimetus
            else:
                return rcd.nimetus_liigiga

    @classmethod
    def get_opt(cls, ylemkomp_tasekood, tase=None, selected=None, ylemaga=False, tasemega=True):
        """Valikute loetelu
        """
        if ylemkomp_tasekood and '.' in ylemkomp_tasekood:
            ylemkomp_tase, ylemkomp_kood = ylemkomp_tasekood.split('.')
        elif not ylemkomp_tasekood or ylemkomp_tasekood == 'EST':
            ylemkomp_tase = ylemkomp_kood = None
        else:
            ylemkomp_tase = None
            ylemkomp_kood = 'X'
            
        q = Aadresskomponent.query
        if ylemkomp_tase or not tase:
            q = (q.filter_by(ylemkomp_kood=ylemkomp_kood)
                 .filter_by(ylemkomp_tase=ylemkomp_tase))
        if tase:
            q = q.filter_by(tase=tase)

        if selected:
            # kasutame kehtivaid komponente ja lisaks see komponent, mis on juba valitud
            selected_tase, selected_kood = selected.split('.')
            q = q.filter(sa.or_(sa.and_(Aadresskomponent.staatus==const.B_STAATUS_KEHTIV,
                                        Aadresskomponent.tase!=6),
                                sa.and_(Aadresskomponent.tase==int(selected_tase),
                                        Aadresskomponent.kood==selected_kood)))
        else:
            # kasutame ainult kehtivaid komponente
            q = q.filter(Aadresskomponent.staatus==const.B_STAATUS_KEHTIV)
            # jätame välja nime taseme
            # sest on palju 6. taseme komponente, milles keegi avatavasti ei ela 
            # ja mida valikuna ei kuvata - 
            # katastriüksused, raudteelõigud, järved, teepeenrad jms,
            # kuid ka talud on 6. tasemel - 
            # talud sisestatakse tekstiväljal ja hiljem normaliseerimise käigus leitakse komponent
            q = q.filter(Aadresskomponent.tase!=6)
        
        # sordime nii, et maja- ja korterinumbrid oleks arvuliselt sorditud
        q = q.order_by(sa.text("to_number(textcat('0', nimetus), text(99999999)), nimetus_liigiga"))
        li = []
        for rcd in q.all():
            if tasemega:
                value = rcd.tasekood
            else:
                value = rcd.kood
            nimi = rcd.nimetus_liigiga
            if ylemaga:
                item = (value, nimi, {'data-kood1': rcd.ylemkomp_kood})
            else:
                item = (value, nimi)
            li.append(item)
        return li

    def get_opt_alamad(self, tase=None):
        return self.get_opt(self.tasekood, tase)

    def get_kohad_q(self, on_soorituskoht=False, on_plangikoht=False, oppetase=None):
        """Leitakse kohad antud haldusüksuses
        """
        from .aadress import Aadress
        f = Aadress.get_field_tase(self.tase)
        q = Koht.query.\
            join(Koht.aadress).\
            filter(f==self.kood)

        if on_soorituskoht:
            q = q.filter(Koht.on_soorituskoht==True)
        if on_plangikoht:
            q = q.filter(Koht.on_plangikoht==True)            
            if self.tase == 1:
                # maakonnavalitsuse alluvusest jätta välja need koolid, mis on linnavalitsuse alluvuses
                Koht1 = sa.orm.aliased(Koht)
                # PostgreSQL 9.4:
                q = q.filter(~ sa.exists()
                           .where(Koht1.on_plangikoht==True)
                           .where(sa.func.concat('2.', Aadress.kood2)==Koht1.valitsus_tasekood))
                # PostgreSQL 8 (concat puudub):
                # q = q.filter(~ sa.exists()
                #            .where(Koht1.on_plangikoht==True)
                #            .where("'2.'||aadress.kood2=koht_1.valitsus_tasekood"))

        if not on_soorituskoht and not on_plangikoht:
            q = q.filter(Koht.staatus==const.B_STAATUS_KEHTIV)

        if oppetase:
            q = q.filter(Koht.koolioppekavad.any(Koolioppekava.oppetase_kood==oppetase))
        return q

    def get_kohad(self, on_soorituskoht=False, on_plangikoht=False, oppetase=None):
        """Leitakse soorituskohad antud haldusüksuses
        """
        q = self.get_kohad_q(on_soorituskoht, on_plangikoht, oppetase)
        return q.order_by(Koht.nimi).all()

    def get_koht_opt(self):
        """Leitakse kohad antud haldusüksuses
        """
        return [(rcd.id, rcd.nimi) for rcd in self.get_kohad()]

    def get_soorituskoht_opt(self):
        """Leitakse soorituskohad antud haldusüksuses
        """
        return [(rcd.id, rcd.nimi) for rcd in self.get_kohad(on_soorituskoht=True)]

    def get_plangikoht_opt(self, oppetase=None):
        """Leitakse plankide moodulis kasutatavad kohad antud haldusüksuses
        """
        return [(rcd.id, rcd.nimi) for rcd in self.get_kohad(on_plangikoht=True, oppetase=oppetase)]

    @classmethod
    def sama_maakonna_koodid(cls, maakonnad):
        "Leitakse kõik samanimeliste maakondade koodid, sh ka need maakonnad, mis enam ei kehti"
        EndMaakond = sa.orm.aliased(Aadresskomponent)
        qm = (SessionR.query(EndMaakond.kood)
              .filter(EndMaakond.nimetus==Aadresskomponent.nimetus)
              .filter(EndMaakond.tase==1)
              .filter(Aadresskomponent.tase==1)
              .filter(Aadresskomponent.kood.in_(maakonnad))
              )
        return [r[0] for r in qm.all()]

    def is_used(self):
        from .aadress import Aadress

        if self.tase == 1:
            f = Aadress.kood1
        elif self.tase == 2:
            f = Aadress.kood2
        elif self.tase == 3:
            f = Aadress.kood3
        elif self.tase == 4:
            f = Aadress.kood4
        elif self.tase == 5:
            f = Aadress.kood5
        elif self.tase == 6:
            f = Aadress.kood6
        elif self.tase == 7:
            f = Aadress.kood7
        elif self.tase == 8:
            f = Aadress.kood8

        cnt = Aadress.query.filter(f==self.kood).count()
        return cnt > 0
