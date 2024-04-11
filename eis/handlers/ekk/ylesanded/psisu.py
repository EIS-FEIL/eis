from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from . import vytest

log = logging.getLogger(__name__)

class PsisuController(BaseResourceController):

    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/psisu.mako' 
    _ITEM_FORM = forms.ekk.ylesanded.PsisuForm

    _SP_NEW_TEMPLATE = 'ekk/ylesanded/psisuplokk.new.mako' 
    _SP_EDIT_TEMPLATE = 'ekk/ylesanded/psisuplokk.edit.mako' 

    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine
    _get_is_readonly = False

    def _new(self, item):
        c = self.c
        item.max_pallid = None
        c.vy_id = self.request.params.get('vy_id')
        if c.vy_id:
            # testilt suunatud
            c.vy = model.Valitudylesanne.get(c.vy_id)
            # uue ylesande õppeaineks võtame testi õppeaine
            q = (model.Session.query(model.Test.aine_kood)
                 .join(model.Testiylesanne.valitudylesanded)
                 .join(model.Testiylesanne.testiosa)
                 .join(model.Testiosa.test)
                 .filter(model.Valitudylesanne.id==c.vy_id))
            for aine_kood in q.all():
                c.aine_kood = aine_kood
                break
            
    def _create(self, **kw):
        item = BaseResourceController._create(self)
        item.ptest = True
        item.etest = False
        item.arvutihinnatav = True
        item.vastvorm_kood = const.VASTVORM_KP
        item.hindamine_kood = const.HINDAMINE_OBJ
        item.pallemaara = False
        item.post_create()
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)

        model.Session.flush()
        vy_id = vytest.set_vy_test(self, item)
        if vy_id:
            # ylesande loomisele tuldi testist nupuga "Loo uus"
            # lisame uue ylesande testi
            vytest.lisatesti(self, item, vy_id)
        model.Session.commit()
        return item

    def _edit(self, item):
        vytest.set_vy_test(self, item)
        vytest.get_vy_test(self, item)
        if self.c.vy_id:
            self.c.vy = model.Valitudylesanne.get(self.c.vy_id)
            
    def _update(self, item):
        item.nimi = self.form.data['f_nimi']
        aine = self.form.data['f_aine_kood']
        self._set_pohiaine(item, aine)

    def _set_pohiaine(self, item, aine):
        yaine = None
        for r in item.ylesandeained:
            if r.aine_kood == aine:
                yaine = r
                break
        if not (yaine and yaine.seq == 0):
            # kui aine ei olnud seni põhiaine
            if not yaine:
                # uus aine
                yaine = model.Ylesandeaine(aine_kood=aine, seq=0)
                item.ylesandeained.append(yaine)

            # märgime aine põhiaineks
            seq = yaine.seq = 0
            for r in item.ylesandeained:
                if r != yaine:
                    seq = r.seq = seq + 1


    def _edit_lisa(self, id):
        # uue sisuploki lisamise akna avamine
        return self.render_to_response(self._SP_NEW_TEMPLATE)

    def _update_lisa(self, id):
        # uute sisuplokkide lisamine
        c = self.c
        schema = forms.ekk.ylesanded.PsisuplokkNewForm
        form = Form(self.request, schema=schema)
        if form.validate():
            c.sisuplokid = []
            karv = form.data['karv']
            c.tyyp = tyyp = form.data['tyyp']
            max_pallid = form.data['max_pallid']
            max_vastus = form.data['max_vastus']
            oige_pallid = form.data['oige_pallid']
            pintervall = form.data['pintervall']
            koodid = form.data['koodid']
            varv = form.data['varv']

            def _gen_seq_1(n):
                # genereeritakse arvuline kood
                return str(n + 1)

            def _gen_seq_A(n):
                # genereeritakse täheline kood
                chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                try:
                    return chars[n]
                except:
                    return str(n + 1)

            def _gen_vkood(n):
                if koodid == 'A':
                    vkood = vnimi = _gen_seq_A(n)
                elif koodid == '1A':
                    vkood = _gen_seq_1(n)
                    vnimi = _gen_seq_A(n)
                else:
                    vkood = vnimi = _gen_seq_1(n)
                return vkood, vnimi
            
            for n in range(karv):
                plokk = model.Sisuplokk(tyyp=tyyp, ylesanne_id=c.item.id, max_pallid=max_pallid)
                c.item.sisuplokid.append(plokk)
                c.sisuplokid.append(plokk)
                if tyyp == const.INTER_CHOICE:
                    kysimus = plokk.give_kysimus()
                    tulemus = kysimus.give_tulemus(arvutihinnatav=True)
                    tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
                    tulemus.baastyyp = const.BASETYPE_IDENTIFIER
                    kysimus.max_vastus = max_vastus
                    tulemus.oige_pallid = oige_pallid
                    tulemus.max_pallid = max_pallid
                    for n in range(varv):
                        vkood, vnimi = _gen_vkood(n)
                        valik = model.Valik(kood=vkood, nimi=vnimi, selgitus=vnimi, seq=n, kysimus=kysimus)
                    model.Session.flush()
                    model.Session.refresh(kysimus)
                    #kysimus.valikud.append(valik)
                    tulemus.set_valikvastus(kysimus.id, None)
                elif tyyp == const.INTER_EXT_TEXT:
                    kysimus = plokk.give_kysimus()
                    tulemus = kysimus.give_tulemus(arvutihinnatav=False)                    
                    tulemus.kardinaalsus = const.CARDINALITY_SINGLE
                    tulemus.baastyyp = const.BASETYPE_STRING
                    tulemus.max_pallid = max_pallid
                    tulemus.pintervall = pintervall
                    model.Session.flush()
            model.Session.commit()
            return self.render_to_response(self._SP_EDIT_TEMPLATE)
        else:
            template = self._SP_NEW_TEMPLATE
            html = form.render(template, extra_info=self.response_dict)
            return Response(html)            

    def _edit_sp(self, id):
        # olemasoleva sisuploki muutmise akna avamine
        sisuplokk_id = self.request.params.get('sisuplokk_id')
        sp = model.Sisuplokk.get(sisuplokk_id)
        assert sp.ylesanne_id == self.c.item.id, _("Vale ülesanne")
        self.c.sisuplokid = [sp]
        self.c.tyyp = sp.tyyp
        return self.render_to_response(self._SP_EDIT_TEMPLATE)

    def _update_sp(self, id):
        # sisuplokkide muutmine
        item = self.c.item
        schema = forms.ekk.ylesanded.PsisuplokidForm
        self.form = Form(self.request, schema=schema)
        if self.form.validate():
            for row in self.form.data['sp']:
                sp = model.Sisuplokk.get(row['id'])
                if sp:
                    assert sp.ylesanne_id == item.id, 'Vale ülesanne'
                    if sp.tyyp == const.INTER_CHOICE:
                        self._update_sp_choice(item, sp, row)
                    elif sp.tyyp == const.INTER_EXT_TEXT:
                        self._update_sp_exttext(item, sp, row)

            model.Session.flush()
            item.calc_max_pallid()
            if self.c.vy_id:
                vytest.set_ty_pallid(self, item, self.c.vy_id)

            model.Session.commit()
            raise HTTPFound(location=self.url_current('edit', id=item.id))
        else:
            template = self._SP_EDIT_TEMPLATE
            html = self.form.render(template, extra_info=self.response_dict)
            return Response(html)                        
            
    def _update_sp_choice(self, item, sp, row):
        for krow in row['k']:
            kysimus = sp.kysimus
            tulemus = kysimus.give_tulemus(arvutihinnatav=True)
            tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
            tulemus.baastyyp = const.BASETYPE_IDENTIFIER
            kysimus.kood = tulemus.kood = krow['kood']
            kysimus.max_vastus = krow['max_vastus']
            tulemus.oige_pallid = krow['oige_pallid']
            tulemus.max_pallid = krow['max_pallid']

            hms = {hm.kood1: hm for hm in tulemus.hindamismaatriksid}
            oigekood = krow['oige']
            for kood in oigekood:
                if kood in hms:
                    hm = hms.pop(kood)
                else:
                    hm = model.Hindamismaatriks(kood1=kood)
                    tulemus.hindamismaatriksid.append(hm)
                hm.oige = True
                hm.pallid = tulemus.oige_pallid or 1
            for hm in hms.values():
                hm.delete()
                        
    def _update_sp_exttext(self, item, sp, row):                
        for krow in row['k']:
            kysimus = sp.kysimus
            tulemus = kysimus.give_tulemus(arvutihinnatav=False)
            tulemus.kardinaalsus = const.CARDINALITY_SINGLE
            tulemus.baastyyp = const.BASETYPE_STRING
            kysimus.kood = tulemus.kood = krow['kood']            
            tulemus.max_pallid = krow['max_pallid']
            tulemus.pintervall = krow['pintervall']

    def _delete_sp(self, id):
        sisuplokk_id = self.request.params.get('sisuplokk_id')
        sp = model.Sisuplokk.get(sisuplokk_id)
        if sp and sp.ylesanne_id == self.c.item.id:
            try:
                sp.delete()
                model.Session.commit()
            except sa.exc.IntegrityError as e:
                msg = _("Ei saa enam kustutada, sest on seotud andmeid")
                try:
                    log.info('%s [%s] %s' % (msg, self.request.url, repr(e)))
                    log.info(e.statement)
                    log.info(e.params)
                except:
                    #if self.is_devel: raise
                    pass
                self.error(msg)
                model.Session.rollback()
        raise HTTPFound(location=self.url_current('edit', id=self.c.item.id))

    def _perm_params(self):
        return {'obj':self.c.item}

    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Ylesanne.get(id)
            vytest.get_vy_test(self, self.c.item)

