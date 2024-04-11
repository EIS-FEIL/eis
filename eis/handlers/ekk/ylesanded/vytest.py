# -*- coding: utf-8 -*- 
"Testi vormilt tulemise andmed"
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

def set_vy_test(handler, item):
    """Vormi avamisel kontrollitakse, kas on parameeter, mis näitab, et tuldi testi vormilt.
    Kui on, siis jäetakse see meelde, et kuvada tagasi testile mineku nuppu
    ja uue ylesande korral võimaldada lisamist testi
    """
    vy_id = handler.request.params.get('vy_id')
    if vy_id:
        vy = model.Valitudylesanne.get(vy_id)
        if vy:
            ty = vy.testiylesanne
            muuta_pallid = ty.max_pallid is None
            testiosa = ty.testiosa
            komplekt = vy.komplekt
            handler.request.session['looylesanne'] = (item.id, vy.id, testiosa.id, testiosa.test_id, muuta_pallid)
            handler.request.session.changed()
            return vy.id

def get_vy_test(handler, item):
    """Leiame testi, kui ylesande loomisele tuldi testist
    """
    try:
        y_id, vy_id, testiosa_id, test_id, muuta_pallid = handler.request.session.get('looylesanne')
    except:
        return False
    else:
        if y_id == item.id:
            handler.c.vy_id = vy_id
            handler.c.vy_testiosa_id = testiosa_id
            handler.c.vy_test_id = test_id
            handler.c.vy_muuta_pallid = muuta_pallid
            return vy_id

def lisatesti(handler, item, vy_id):
    """Lisame loodud ylesande testi
    """
    err = None
    vy = model.Valitudylesanne.get(vy_id)
    if vy:
        ty = vy.testiylesanne
        testiosa = ty.testiosa
        komplekt = vy.komplekt
        test = testiosa.test

        # lisame testi
        if not handler.c.user.has_permission('ekk-testid', const.BT_UPDATE, test=test):
            err = _("Ülesannet ei saa testi lisada, sest selleks puudub õigus")
        elif komplekt.staatus != const.K_STAATUS_KOOSTAMISEL:
            err = _("Ülesannet ei saa testi lisada, sest komplekt ei ole enam koostamisel")
        elif komplekt.lukus:
            err = _("Ülesannet ei saa testi lisada, sest komplekt on lukus")
        else:
            vy.ylesanne_id = item.id
            # siin veel ylesandel palle ei ole, mistõttu ei saa ty palle määrata
            vy.update_koefitsient(ty)
            model.Session.commit()
    if err:
        handler.error(err)

def set_ty_pallid(handler, item, vy_id):
    """Kui ty pallid on veel määramata, siis määrtakse ylesande max pallid
    """
    vy = model.Valitudylesanne.get(vy_id)
    if vy:
        ty = vy.testiylesanne
        testiosa = ty.testiosa
        test = testiosa.test
        if (ty.max_pallid is None or handler.c.vy_muuta_pallid) and not testiosa.lotv:
            if handler.c.user.has_permission('ekk-testid', const.BT_UPDATE, test=test) and \
               test.staatus == const.T_STAATUS_KOOSTAMISEL:
                ty.max_pallid = item.max_pallid or 0
                model.Session.flush()
                test.arvuta_pallid()
                vy.update_koefitsient(ty)
