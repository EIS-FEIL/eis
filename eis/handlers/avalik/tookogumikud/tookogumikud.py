from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from .jagamised import get_jagamised

log = logging.getLogger(__name__)

class TookogumikudController(BaseResourceController):

    _permission = 'tookogumikud'

    _MODEL = model.Tookogumik
    _INDEX_TEMPLATE = 'avalik/tookogumikud/toolaud.mako' 
    _EDIT_TEMPLATE = 'avalik/tookogumikud/tookogumik.sisu.mako'
    _NEW_TEMPLATE = 'avalik/tookogumikud/tookogumik.mako'     
    _ITEM_FORM = forms.avalik.tookogumikud.TookogumikForm
    _DEFAULT_SORT = 'tookogumik.id' # vaikimisi sortimine
    _ignore_default_params = ['csv','xls']
    _actions = 'index,new,update,edit,delete' # võimalikud tegevused
    _get_is_readonly = False
    
    def index(self):
        # test_id on siis, kui siia on suunatud mujalt lehelt kindla testi asjus
        test_id = self.request.params.get('test_id')
        if test_id:
            data = {'test_id': test_id}
            self._copy_search_params(data, save=True, upath='/tookogumik/testiotsing')            
            self.c.current_search_tab = 'tab_t'

        c = self.c
        q = (model.SessionR.query(model.Tookogumik)
             .filter(model.Tookogumik.kasutaja_id==c.user.id)
             .order_by(model.Tookogumik.nimi, sa.desc(model.Tookogumik.id))
             )
        c.tookogumikud = list(q.all())
        if not c.tookogumikud:
            item = model.Tookogumik.lisa_tookogumik(c.user.id)
            model.Session.commit()
            c.tookogumikud = [item]

        # milline töökogumik on vaikimisi kohe avatud?
        dparams = self._get_default_params(upath='/tookogumik/open_tk')
        if dparams:
            tk_id = dparams.get('open_tk_id')
            if tk_id:
                # kontrollime, et selle ID-ga töökogumik on veel alles
                tookogumikud_id = [r.id for r in c.tookogumikud]
                if tk_id in tookogumikud_id:
                    c.open_tk_id = tk_id
        if not c.open_tk_id :
            c.open_tk_id = c.tookogumikud[0].id
        
        self.c.opperyhmad = self._search_opperyhmad(10)
        get_jagamised(self)
        self._get_opt()
        
        return self.render_to_response(self._INDEX_TEMPLATE)
    
    def new(self):
        c = self.c
        # leiame olemasolevate töökogumike nimed
        q = (model.Session.query(model.Tookogumik.nimi)
             .filter(model.Tookogumik.kasutaja_id==c.user.id)
             )
        old_names = [s for s, in q.all()]

        # loome uue töökogumiku "Töökogumik"
        c.item = model.Tookogumik.lisa_tookogumik(c.user.id)

        # teeme nime unikaalseks
        name = dflt = c.item.nimi
        for n in range(1, 1000):
            if name in old_names:
                name = f'{dflt} ({n})'
            else:
                break
        c.item.nimi = name
        
        model.Session.commit()

        # jätame meelde, et uus töökogumik on vaikimisi avatud
        self._edit(c.item)
        self.c.open_tk_id = c.item.id
        
        return self.render_to_response(self._NEW_TEMPLATE)

    def _edit(self, item):    
        # kasutaja avab töökogumiku
        # jätame meelde viimasena avatud töökogumiku, et seda järgmisel töölaua avamisel
        # vaikimisi kohe avatuna näidata
        data = {'open_tk_id': item.id}
        self._set_default_params(data, upath='/tookogumik/open_tk')

    def _search_opperyhmad(self, limit):
        if not self.c.user.koht_id:
            return []
        q = (model.SessionR.query(model.Opperyhm)
             .filter(model.Opperyhm.kasutaja_id==self.c.user.id)
             .filter(model.Opperyhm.koht_id==self.c.user.koht_id)
             .order_by(sa.desc(model.Opperyhm.created))
             .limit(limit)
             )
        return q.all()

    def _get_opt(self):
        "Otsingute valikväljade sisu"
        c = self.c
        q = (model.SessionR.query(model.Ylesandekogu.aine_kood).distinct()
             .filter(model.Ylesandekogu.staatus==const.YK_STAATUS_AVALIK)
             )
        koguained = [kood for kood, in q.all()]
        c.opt_aine_yk = [r for r in c.opt.klread_kood('AINE') if r[0] in koguained]
        
    def _update(self, id):
        "Töökogumiku muutmine"
        item = self.c.item
        item.from_form(self.form.data, 'f_')
        if not item.nimi:
            item.nimi = _('Töökogumik')
        self._save_items(item)
        
    def _save_items(self, item1):
        "Töökogumiku sisu muutmine"
        item = self.c.item
        if len(item.tkosad):
            tkosa = item.tkosad[0]
        else:
            tkosa = model.Tkosa(tookogumik=item,
                                seq=1)

        seq = 0
        tkylesanded = {r.id: r for r in tkosa.tkylesanded}
        tktestid = {r.id: r for r in tkosa.tktestid}
        #items = []
        for itemid in self.request.params.getall('itemid'):
            if not itemid:
                continue
            itemtype, i_id = itemid.split('-')
            i_id = int(i_id)
            seq += 1
            if itemtype == 'yky':
                # lisame ylesandekogust ylesande
                yky = model.Koguylesanne.get(i_id)
                rcd = model.Tkylesanne(tkosa=tkosa,
                                       seq=seq,
                                       ylesanne_id=yky.ylesanne_id,
                                       ylesandekogu_id=yky.ylesandekogu_id)
            elif itemtype == 'yoy':
                # lisame ylesandeotsingust saadud ylesande
                rcd = model.Tkylesanne(tkosa=tkosa,
                                       seq=seq,
                                       ylesanne_id=i_id,
                                       ylesandekogu_id=None)
            elif itemtype == 'tot':
                # lisame testiotsingust saadud testi
                rcd = model.Tktest(tkosa=tkosa,
                                   seq=seq,
                                   test_id=i_id,
                                   ylesandekogu_id=None)
            elif itemtype == 'ykt':
                # lisame ylesandekogust testi
                ykt = model.Kogutest.get(i_id)
                rcd = model.Tktest(tkosa=tkosa,
                                   seq=seq,
                                   test_id=ykt.test_id,
                                   ylesandekogu_id=ykt.ylesandekogu_id)
            elif itemtype == 'tky':
                # juba lisatud ylesanne
                r = model.Tkylesanne.get(i_id)
                if not r:
                    pass
                elif r.tkosa_id != tkosa.id:
                    # tõstame teisest töökogumikust siia
                    old_tk = r.tkosa.tookogumik
                    if old_tk.kasutaja_id == item.kasutaja_id:
                        r.tkosa = tkosa
                        r.seq = seq
                elif i_id in tkylesanded:
                    # järjestuse muutmine
                    rcd = tkylesanded.pop(i_id)
                    rcd.seq = seq
            elif itemtype == 'tkt':
                # juba lisatud test
                r = model.Tktest.get(i_id)
                if not r:
                    # test on vahepeal kustutatud
                    pass
                elif r.tkosa_id != tkosa.id:
                    # tõstame teisest töökogumikust siia
                    old_tk = r.tkosa.tookogumik
                    if old_tk.kasutaja_id == item.kasutaja_id:
                        r.tkosa = tkosa
                        r.seq = seq
                elif i_id in tktestid:
                    # järjestuse muutmine
                    rcd = tktestid.pop(i_id)
                    rcd.seq = seq

        # kustutatud 
        for id, tky in list(tkylesanded.items()):
            tky.delete()
        for id, tkt in list(tktestid.items()):
            tkt.delete()

        model.Session.commit()
        res = {'rc': 'OK'}
        return Response(json_body=res)

    def _perm_params(self):
        if not self.c.user.has_permission('tookogumikud', const.BT_INDEX):
            self.error(_('Õpetaja töölauale on ligipääs ainult õpetajatel!'))
            return False
        return {'obj':self.c.item}

    def _get_perm_bit(self):
        action = self.c.action
        if action == 'delete':
            tkv_id = self.request.params.get('tkv_id')
            if tkv_id:
                self.c.tkv = model.Tkvaataja.get(tkv_id)
                if self.c.tkv and self.c.tkv.kasutaja_id == self.c.user.id:
                    # on mulle jagamine ja soovin seda jagamist kustutada
                    # selleks piisab, kui mul on töökogumiku vaatamise õigus
                    return const.BT_SHOW
        return super(TookogumikudController, self)._get_perm_bit()

    def _after_delete(self, parent_id=None):
        #return Response(json_body={'rc':True})
        return Response('')
    
    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Tookogumik.get(id)
        super(TookogumikudController, self).__before__()
