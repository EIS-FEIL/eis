from itertools import groupby
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis
from cgi import FieldStorage
import eis.handlers.ekk.otsingud.kohateated as kt
from eis.handlers.ekk.korraldamine.valim import send_valimiteade
log = logging.getLogger(__name__)

class LisavalikudController(BaseResourceController):
    """Peale nimistu laadimist failist 
    määratakse üksikute inimeste kaupa keel
    ja eemaldatakse need registreeringud, mida pole vaja.
    """
    _permission = 'regamine'
    _ITEM_FORM = forms.ekk.regamine.NimistulisavalikudForm # valideerimisvorm muutmisvormile
    _actions = 'create,show' # võimalikud tegevused

    def edit(self):
        self.c.protsess_id = self.request.matchdict.get('protsess_id')
        protsess = model.Arvutusprotsess.get(self.c.protsess_id)
        if protsess and not protsess.lopp:
            url = self.url('regamine_nimistu_edit_sooritajad',
                           korrad_id=self.c.korrad_id,
                           testiliik=self.c.testiliik)
            raise HTTPFound(location=url)

        self.c.korrad_id = self.request.matchdict.get('korrad_id')
        korrad_id = list(map(int, self.c.korrad_id.split('-')))
        self.c.korrad = [model.Testimiskord.get(kord_id) for kord_id in korrad_id]
        
        # leiame testiliigi
        q = (model.Session.query(model.Test.testiliik_kood)
             .join(model.Test.testimiskorrad)
             .filter(model.Testimiskord.id.in_(korrad_id)))
        for r, in q.all():
            self.c.testiliik = r
            break

        # leiame protsessiga laaditud sooritajad
        q = self._q_laaditud_sooritajad(korrad_id, self.c.protsess_id)
        items = groupby(list(q.all()), lambda r: r.kasutaja_id)
        rows = []
        for kasutaja_id, grouper in items:
            kasutaja = model.Kasutaja.get(kasutaja_id)
            di = {j.testimiskord_id: j for j in grouper }
            sooritajad = [di.get(kord_id) for kord_id in korrad_id]
            rows.append((kasutaja, sooritajad))
        self.c.rows = rows
        return self.render_to_response('ekk/regamine/nimistu.lisavalikud.mako')

    def _q_laaditud_sooritajad(self, korrad_id, protsess_id):
        "Protsessiga laaditud sooritajate päring"
        q = (model.Session.query(model.Sooritaja)
             .join((model.Kasutajaprotsess,
                    sa.and_(model.Kasutajaprotsess.kasutaja_id==model.Sooritaja.kasutaja_id,
                            model.Kasutajaprotsess.arvutusprotsess_id==protsess_id)))
             .filter(model.Sooritaja.testimiskord_id.in_(korrad_id))
             .order_by(model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi,
                       model.Sooritaja.kasutaja_id)
             )
        return q
    
    def _create(self, **kw):
        self.c.testiliik = self.request.params.get('testiliik')
        self.c.korrad_id = self.request.matchdict.get('korrad_id')
        korrad_id = self.c.korrad_id.split('-')
        korrad = [model.Testimiskord.get(kord_id) for kord_id in korrad_id]

        testiruumid_id = set()
        for k_row in self.form.data.get('k'):
            kasutaja_id =k_row.get('id')
            for s_row in k_row.get('tk'):
                kord_id = s_row.get('tk_id')
                sooritaja = model.Sooritaja.get_by_kasutaja(kasutaja_id, kord_id)
                if not sooritaja:
                    continue
                for sooritus in sooritaja.sooritused:
                    if sooritus.testiruum_id:
                        testiruumid_id.add(sooritus.testiruum_id)
                if not s_row.get('s_id'):
                    # registreeringut pole vaja
                    staatus = sooritaja.staatus
                    if staatus < const.S_STAATUS_ALUSTAMATA:
                        kt.send_tyhteade(self, sooritaja.kasutaja, sooritaja)
                        sooritaja.tyhista()
                        if staatus <= const.S_STAATUS_REGAMATA:
                            model.Session.flush()
                            sooritaja.delete()
                    else:
                        self.error(_("{s1} registreeringut testile {s2} ei saa enam kustutada").format(
                            s1=sooritaja.kasutaja.nimi, s2=sooritaja.testimiskord.tahised))
                else:
                    # muudame keelt
                    lang = s_row.get('lang')
                    if lang:
                        sooritaja.lang = lang
                    sooritaja.kursus_kood = s_row.get('kursus')
                    sooritaja.kinnita_reg()
        
        for testiruum_id in testiruumid_id:
            testiruum = model.Testiruum.get(testiruum_id)
            if testiruum:
                testiruum.set_sooritajate_arv()

        model.Session.commit()       
        buf = _("Andmed on salvestatud. ")

        n = 0
        teated = self.request.params.get('teated')
        if teated:
            # saadame registreerimise teated
            if self.request.is_ext():
                for k_row in self.form.data.get('k'):
                    kasutaja_id = k_row.get('id')
                    kasutaja = model.Kasutaja.get(kasutaja_id)
                    if kt.send_regteade(self, kasutaja, self.c.testiliik):
                        n += 1
                model.Session.commit()

            if n:
                buf += _("Registreerimisteated saadeti {n} testisooritajale. ").format(n=n)

        if n == 0:
            buf += _("Registreerimise teateid ei saadetud. ")

        # vaadatakse, kas selle protsessi käigus laaditud sooritajad kuuluvad valimisse
        # ja kui kuuluvad, siis saadetakse koolidele valimisse kuulumise teade
        protsess_id = self.request.matchdict.get('protsess_id')
        cnt = 0
        for kord in korrad:
            cnt += send_valimiteade(self, kord, protsess_id)
        if cnt:
            buf += _("Koolidele saadeti {n} valimisse kuulumise teadet. ").format(n=cnt)
            
        self.notice(buf)
        return HTTPFound(location=self.url('regamised', focus_nimistu=True))
