from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KasutajagrupidController(BaseResourceController):

    _permission = 'admin'

    _MODEL = model.Kasutajagrupp
    _SEARCH_FORM = forms.admin.KasutajagrupidForm # valideerimisvorm otsinguvormile
    _ITEM_FORM = forms.admin.KasutajagruppForm # valideerimisvorm muutmisvormile
    _INDEX_TEMPLATE = 'admin/kasutajagrupid.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/kasutajagrupp.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/kasutajagrupid_list.mako'
    _PARTIAL = True

    def _search(self, q):
        c = self.c
        if c.oigus_id == '0':
            # kõik õigused
            c.oigus_id = None
        if c.oigus_id:
            q = (q.with_entities(model.Kasutajagrupp,
                                 model.Kasutajagrupp_oigus.bitimask)
                 .join(model.Kasutajagrupp.kasutajagrupp_oigused)
                 .filter(model.Kasutajagrupp_oigus.kasutajaoigus_id==c.oigus_id)
                 )
        return q

    def _paginate(self, q):
        # ei soovita paginaatorit, soovitakse kõik grupid ühel lehel kuvada
        return q.all()

    def _update(self, item):
        old_nimi = item.nimi
        item.from_form(self.form.data, self._PREFIX)
        oigused = self.form.data.get('o')

        if not oigused:
            oigused = []

        d = dict()
        for o in oigused:
            oigus_id = o.get('oigus_id')
            bitimask = o['b_index'] | o['b_show'] | o['b_create'] | o['b_update']
            if bitimask:
                d[oigus_id] = bitimask

        log_list = list()
        
        # eemaldame ylearused
        li = []
        for kgo in item.kasutajagrupp_oigused:
            oigus_id = kgo.kasutajaoigus_id
            if oigus_id not in list(d.keys()):
                log_list.append('Eemaldatud' + ': %s (%s)' % (kgo.nimi, _smask(kgo.bitimask)))
                kgo.delete()
            else:
                bitimask = d.pop(oigus_id)
                if kgo.bitimask != bitimask:
                    log_list.append('Muudetud' + ': %s (%s -> %s)' % (kgo.nimi, _smask(kgo.bitimask), _smask(bitimask)))
                    kgo.bitimask = bitimask
                    log.debug('kgo(%d).bitimask=%s' % (oigus_id, _smask(kgo.bitimask)))
        # lisame uued
        for o_id, bitimask in d.items():
            kgo = model.Kasutajagrupp_oigus(kasutajagrupp=item,
                                            kasutajaoigus_id=o_id,
                                            bitimask=bitimask)
            o = model.Kasutajaoigus.get(o_id)
            log_list.append('Lisatud' + ': %s (%s)' % (o.nimi, _smask(bitimask)))
            item.kasutajagrupp_oigused.append(kgo)

        # systeem peab uuesti arvutama minimaalse kasutajate arvu piirangu
        User.min_user_count = None
        self._log_oigused(log_list, item, old_nimi)

    def _log_oigused(self, log_list, item, old_nimi):
        if log_list:
            buf = 'Grupi õiguseid muudeti\n' 
            if item.nimi != old_nimi:
                buf += 'Grupi nimi (senini): "%s"\n' % (old_nimi)
            buf += '\n'.join(log_list)
            self.log_add(const.LOG_PERM, buf, item.nimi)

def _smask(bitimask):
    if bitimask == const.BT_INDEX:
        return 'index'
    elif bitimask == const.BT_SHOW:
        return 'show'
    elif bitimask == const.BT_VIEW:
        return 'view'
    elif bitimask == const.BT_CREATE:
        return 'create'
    elif bitimask == const.BT_ALL:
        return 'modify'
    else:
        return str(bitimask)
