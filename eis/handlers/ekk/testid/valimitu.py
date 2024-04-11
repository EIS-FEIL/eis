# -*- coding: utf-8 -*- 
from cgi import FieldStorage
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ValimituController(BaseResourceController):
    """Mitme ülesande valimine korraga failist
    """
    _permission = 'ekk-testid'
    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/testid/komplekt.valimitu.mako'
    _INDEX_TEMPLATE = 'ekk/testid/komplekt.valimitu.mako'
    #_ITEM_FORM = forms.ekk.testid.KomplektForm 
    _actions = 'index,create'
    _no_paginate = True
    
    def _query(self):
        pass

    def _create_upload(self):
        "Failist loetakse ylesannete ID-d ja kuvatakse ylesannete loetelu"
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            self.error(_("Faili ei leitud"))
        else:
            try:
                value = value.value.decode('utf-8').replace(',',' ')
            except:
                self.error(_("Faili sisu või vorming ei sobi. Ülesandeid saab laadida tekstifailist, milles on täisarvud (eraldatud koma või tühikuga)."))
            else:
                items = []
                chosen = []
                notfound = []
                for ylesanne_id in value.split():
                    try:
                        ylesanne_id = int(ylesanne_id)
                    except:
                        self.error(_("Failis tohivad olla ainult täisarvud"))
                        break
                    else:
                        if ylesanne_id not in chosen:
                            chosen.append(ylesanne_id)
                            ylesanne = model.Ylesanne.get(ylesanne_id)
                            if not ylesanne:
                                notfound.append(str(ylesanne_id))
                            else:
                                items.append(ylesanne)
                if notfound:
                    self.error('%s: %s' % (_("Valitud ID-ga ülesannet ei ole"), ', '.join(notfound)))

                self.c.items = items
                if items:
                    # kui mõni ylesanne on juba valitud, siis kuvame märkeruudu,
                    # et kasutaja määraks, kas valitud asendada või mitte
                    for vy in self.c.komplekt.valitudylesanded:
                        if vy.ylesanne_id:
                            self.c.taidetud = True
                            break
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create_add(self):
        ylesanded_id = self.request.params.getall('y_id')
        tyhjad = self.request.params.get('tyhjad')
        valitudylesanded = list(self.c.komplekt.valitudylesanded)
        if tyhjad:
            # juba valitud ylesandeid ei asendata
            valitudylesanded = [vy for vy in valitudylesanded if not vy.ylesanne_id]
            
        vy_cnt = len(valitudylesanded)
        cnt = 0
        for ind, y_id in enumerate(ylesanded_id):
            if ind >= vy_cnt:
                # komplektis pole rohkem ylesandeid
                break
            # võtame järgmise ylesande
            vy = valitudylesanded[ind]
            ylesanne = model.Ylesanne.get(y_id)
            if ylesanne:
                if ylesanne.max_pallid is None:
                    ylesanne.max_pallid = ylesanne.calc_max_pallid()
                vy.ylesanne = ylesanne
                ty = vy.testiylesanne
                if not self.c.testiosa.lotv and ty.max_pallid is None:
                    ty.max_pallid = ylesanne.max_pallid or 0
                vy.update_koefitsient(ty)
                cnt += 1
        model.Session.flush()
        self.c.test.arvuta_pallid()
        model.Session.commit()

        file_cnt = len(ylesanded_id)
        buf = _("Valiti {n} ülesannet").format(n=cnt)
        self.notice(buf)
        return self._after_update(None)
    
    def _after_update(self, id):
        #self.success()
        return HTTPFound(location=self.url('test_valitudylesanded', 
                                           test_id=self.c.test.id,
                                           testiosa_id=self.c.testiosa.id,
                                           komplektivalik_id=self.c.komplektivalik_id,
                                           komplekt_id=self.c.komplekt_id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.komplekivalik_id = self.request.matchdict.get('komplektivalik_id')
        self.c.komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
