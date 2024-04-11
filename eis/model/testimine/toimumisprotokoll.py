"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.test import Testiosa
from eis.s3file import S3File
from .toimumisaeg import Toimumisaeg
from .sooritaja import Sooritaja
from .sooritus import Sooritus
from .testikoht import Testikoht
from .testiopetaja import Testiopetaja
from .testiruum import Testiruum
from .testipakett import Testipakett
from .labiviija import Labiviija
_ = usersession._

class Toimumisprotokoll(EntityHelper, Base, S3File):
    """Testi toimumise protokoll.
    Võib olla seotud:
    - testimiskorra ja kohaga (põhikooli eksamid);
    - ühe toimumisaja ühe testikohaga (riigieksamid);
    - testikoha ühe testiruumiga (TE, SE);
    - pedagoogile määratud testi ühe testiruumiga (kutseeksam).
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True) # viide testimiskorrale (puudub kutseeksami korral)   
    testimiskord = relationship('Testimiskord', foreign_keys=testimiskord_id, back_populates='toimumisprotokollid')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide kohale
    koht = relationship('Koht', foreign_keys=koht_id)
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True, nullable=False) # viide testikohale ja toimumisajale (kui toimumise protokoll ei ole toimumisajaga seotud, siis viide esimese testiosa toimumisaja testikohale)
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id, back_populates='toimumisprotokollid')
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide testiruumile, kui toimumise protokoll on testiruumiga seotud (SE, TE)
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='toimumisprotokollid')
    lang = Column(String(2)) # soorituskeel (e-testis ja p-testi tulemustega protokollil puudub, sest on ühine kõigi keelte kohta)
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # testi toimumise protokolli olek: 0=const.B_STAATUS_KEHTETU - kehtetu; 1=const.B_STAATUS_KEHTIV - kehtiv; 2=const.B_STAATUS_KINNITATUD - kinnitatud; 3=const.B_STAATUS_EKK_KINNITATUD - kinnitatud eksamikeskuse poolt
    markus = Column(Text) # märkused
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    kehtivuskinnituseta = Column(Boolean) # kohalikust serverist saadud DDOCi kohta: kas on Sertifitseerimiskeskuse poolt kehtivuskinnitatud või ei ole veel (kohalikus serveris ei ole võimalik kehtivuskinnitusteenust kasutada)
    edastatud = Column(DateTime) # kohaliku serveri korral: protokolli ja vastuste faili keskserverisse edastamise aeg
    ruumifailid = relationship('Ruumifail', order_by='Ruumifail.id', back_populates='toimumisprotokoll')
    __table_args__ = (
        sa.UniqueConstraint('testimiskord_id', 'koht_id', 'lang','testikoht_id', 'testiruum_id'),
        )
    _cache_dir = 'toimumisprotokoll'

    @property
    def lang_nimi(self):
        if self.lang:
            return Klrida.get_lang_nimi(self.lang)

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_EKK_KINNITATUD:
            return _("Kinnitatud (eksamikeskuse poolt)")
        elif self.staatus == const.B_STAATUS_KINNITATUD:
            return _("Kinnitatud")
        else:
            return _("Kinnitamata")

    @property
    def tahistus(self):
        tahised = self.testikoht.tahised
        if self.testiruum:
            tahised = '%s-%s' % (tahised, self.testiruum.tahis)
        return tahised

    @property
    def testikohad(self):
        if not self.testimiskord or not self.testimiskord.prot_tulemusega:
            return [self.testikoht]
        
        q = (Testikoht.query
             .filter_by(koht_id=self.koht_id)
             .join(Testikoht.toimumisaeg)
             .filter(Toimumisaeg.testimiskord_id==self.testimiskord_id)
             .join(Toimumisaeg.testiosa)
             .order_by(Testiosa.seq)
             )
        return q.all()

    @property
    def testipaketid(self):
        q = Testipakett.query
        if self.lang:
            q = q.filter_by(lang=self.lang)
        if self.testiruum_id:
            q = q.filter_by(testiruum_id=self.testiruum_id)
        elif not self.testimiskord or self.testimiskord.prot_tulemusega == False:
            q = q.filter_by(testikoht_id=self.testikoht_id)
        else:
            q = (q.join(Testipakett.testikoht)
                 .filter(Testikoht.koht_id==self.koht_id)
                 .join(Testikoht.toimumisaeg)
                 .filter(Toimumisaeg.testimiskord_id==self.testimiskord_id)
                 .join(Toimumisaeg.testiosa)
                 .order_by(Testiosa.seq)
                 )
        return q.all()

    @property
    def leidub_suulist(self):
        testimiskord = self.testimiskord
        if testimiskord:
            if not testimiskord.on_helifailid:
                return False
            if testimiskord.prot_tulemusega == False:
                testiosa = self.testikoht.toimumisaeg.testiosa
                return testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)
            test = testimiskord.test
        else:
            test = self.testikoht.testiosa.test
        for testiosa in test.testiosad:
            if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
                return True
        return False

    @property
    def millal(self):
        def _vahemik(alates, kuni):
            alates = alates.strftime('%d.%m.%Y')
            if not kuni:
                return alates
            kuni = kuni.strftime('%d.%m.%Y')
            if alates != kuni:
                return '%s-%s' % (alates, kuni)
            else:
                return alates

        buf = None
        if not self.testimiskord or self.testimiskord.prot_tulemusega == False:
            try:
                # kutseeksam
                testiruum = self.testiruum
                nimekiri = testiruum.nimekiri
                alates = nimekiri.alates
                kuni = nimekiri.kuni
            except:
                alates = kuni = None
            if alates:
                buf = _vahemik(alates, kuni)
            else:
                buf = self.testikoht.millal
        else:
            q = (SessionR.query(Testiruum.algus)
                 .join(Testiruum.testikoht)
                 .join(Testikoht.toimumisaeg)
                 .filter(Toimumisaeg.testimiskord_id==self.testimiskord_id)
                 .filter(Testikoht.koht_id==self.koht_id)
                 )
            li = [r[0] for r in q.all()]
            alates = min(li)
            kuni = max(li)
            if alates:
                buf = _vahemik(alates, kuni)
            elif self.testimiskord:
                buf = self.testimiskord.millal
        return buf

    def delete_subitems(self):    
        self.delete_subrecords(['ruumifailid',
                                ])
    
    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud testikohas.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        testimiskord = self.testimiskord
        if permission == 'tprotopetaja' and testimiskord.osalemise_naitamine:
            # kas on aineõpetaja?
            # aineõpetajal on õigus oma õpilaste punktide sisestamiseks
            if testimiskord.prot_tulemusega:
                q = (SessionR.query(Sooritaja.id)
                    .filter(Sooritaja.testiopetajad.any(
                        Testiopetaja.opetaja_kasutaja_id==user.id))
                     .join(Sooritaja.sooritused))
                if self.testiruum_id:
                    q = q.filter(Sooritus.testiruum_id==self.testiruum_id)
                else:
                    q = q.filter(Sooritus.testikoht_id==self.testikoht_id)
                return q.count() > 0
            else:
                return False

        if testimiskord.osalemise_naitamine:
            # kas on soorituskoha administraatorina õigus protokollile?
            # need õigused toimivad ainult siis, kui osalemist näidatakse
            # (kui osalemist ei näidata, siis saab ainult testi admin protokolli täita)
            if permission in ('tprotsisestus', 'toimumisprotokoll') and \
              self.koht.has_permission(permission, perm_bit, user):
                return True         

        def on_testiadmin(testiruum_id):
            # toimumisaeg, kus testi adminil on õigus protokolli sisestada
            # kas isik on testi administraator?
            q = (SessionR.query(Labiviija.id)
                 .filter(Labiviija.kasutaja_id==user.id)
                 .filter(Labiviija.staatus>const.L_STAATUS_KEHTETU)
                 .filter(Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                 )
            if testiruum_id:
                q = q.filter(Labiviija.testiruum_id==testiruum_id)
            else:
                q = q.filter(Labiviija.testikoht_id==self.testikoht_id)
            # kas isik on testi admin
            return q.count() > 0

        # kontrollitakse testi admini õigust
        rc = False
        ta = self.testikoht.toimumisaeg
        if ta.prot_admin and on_testiadmin(self.testiruum_id):
            # testiadminidel on vähemalt sisestamisõigus ja kasutaja on testiadmin
            if permission == 'tprotsisestus':
                # testi admin võib sisestada
                rc = True
            elif permission == 'toimumisprotokoll' and ta.prot_admin == const.PROT_KINNIT:
                # testi admin võib kinnitada juhul, kui ta on igas ruumis testiadmin (ES-2573)
                rc = True
                if not self.testiruum_id:
                    # kui pole yhe ruumi protokoll, siis on vaja
                    # kontrollida kõik soorituskoha testiruumid
                    q = (SessionR.query(Testiruum.id)
                         .filter(Testiruum.testikoht_id==self.testikoht_id))
                    for testiruum_id, in q.all():
                        if not on_testiadmin(testiruum_id):
                            rc = False
                            break
            if rc:
                return True

        if not testimiskord.osalemise_naitamine:
            # kui osalemist ei näidata, siis võib ainult testi admin protokolli täita
            return False
                    
        if self.testiruum:
            return self.testiruum.has_permission(permission, perm_bit, user)
        if self.testikoht.has_permission(permission, perm_bit, user):
            # komisjoni esimehe õigus
            return True
        
        if user.app_name == const.APP_EKK:
            # eksamikeskuse vaate õiguste kontroll
            kasutaja = user.get_kasutaja()
            if not kasutaja:
                return False
            test = self.testimiskord.test
            piirkond_id = self.koht.piirkond_id
            rc = kasutaja.has_permission(permission, 
                                         perm_bit,
                                         koht_id=const.KOHT_EKK,
                                         piirkond_id=piirkond_id,
                                         aine_kood=test.aine_kood, 
                                         testiliigid=[test.testiliik_kood])
            return rc
        else:
            if user.koht_id == self.koht_id and user.on_avalikadmin:
                return True

            # kas isikul on protokolli kõigis testikohtades see õigus olemas
            for tkoht in self.testikohad:
                if not tkoht.has_permission(permission, perm_bit, user):
                    return False
            return True
