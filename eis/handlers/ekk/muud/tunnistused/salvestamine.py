from eis.lib.baseresource import *
log = logging.getLogger(__name__)
from eis.s3file import S3FileBuf

# digitemplile allkirjastamiseks jäetud PDFide kataloog MinIOS
DIGITEMPEL_PDF_DIR = 'digitempel/pdf'
# digitempli poolt allkirjastatud failide kataloog MinIOs
DIGITEMPEL_ASICE_DIR = 'digitempel/asice'

class SalvestamineController(BaseResourceController):
    """Väljaspool EISi digiallkirjastatud tunnistuste salvestamine EISi andmebaasi
    """
    _permission = 'tunnistused'
    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'ekk/muud/tunnistused.salvestamine.mako'

    _index_after_create = True

    def index(self):
        sub = self._get_sub()
        if sub:
            #log.warn("INDEX sub=%s" % sub)
            return eval('self._index_%s' % sub)()
        self._get_protsessid()
        try:
            sbuf = S3FileBuf()
            ootel = len(list(sbuf.s3file_list(DIGITEMPEL_PDF_DIR)))
            valmis = len(list(sbuf.s3file_list(DIGITEMPEL_ASICE_DIR)))
        except:
            log.error('tunnistuste salvestamise katalooge ei saa lugeda')
        else:
            p = ''
            #if ootel > 0:
            #    protsent = int(round(puhvris / ootel * 100))
            #    p = ' ({p}% allkirjastatud)'.format(p=protsent)
            self.notice(f'Allkirjastamisel {ootel} faili. Salvestamist ootab {valmis} faili.')
        return self.render_to_response(self._INDEX_TEMPLATE)

    def create(self):
        c = self.c
        for rcd in self._query_protsessid(True):
            rcd.lopp = datetime.now()
        
        childfunc = lambda protsess: self._salvesta(protsess)
        params = {'liik': model.Arvutusprotsess.LIIK_SALVESTAMINE,
                  'kirjeldus': 'Tunnistuste salvestamine',
                  }
        model.Arvutusprotsess.start(self, params, childfunc)
        self.success('Tunnistuste salvestamine käivitatud')
        return self._redirect('index')

    def _salvesta(self, protsess):
        n = 0
        notfound = 0
        sbuf = S3FileBuf()
        li = list(sbuf.s3file_list(DIGITEMPEL_ASICE_DIR))
        total = len(li)
        for ind, obj in enumerate(li):
            fn = obj.object_name
            basename = fn.split('/')[-1]
            tunnistusenr = basename.split('.')[0]
            tunnistus = model.Tunnistus.query.filter_by(tunnistusenr=tunnistusenr).first()
            if tunnistus:
                data_dok = sbuf.s3file_get(fn)
                tunnistus.set_filedata(data_dok, basename)
                tunnistus.staatus = const.N_STAATUS_SALVESTATUD
                model.Session.commit()
                sbuf.s3file_remove(fn)
                n += 1
            else:
                notfound += 1
                #fn_err = os.path.join(vead, basename)
                #os.rename(fn, fn_err)
            if protsess:
                if protsess.lopp:
                    buf = 'Salvestamine katkestatud. '
                    buf += 'Kataloogis olnud %d failist salvestati %d.' % (total, n)
                    if notfound:
                        buf += ' %d failile vastavaid tunnistuste kirjeid ei leitud.' % notfound
                    raise Exception(buf.strip()[:256])
                protsess.edenemisprotsent = (ind + 1) * 100 / total
                model.Session.commit()

        buf = 'Kataloogis olnud %d failist salvestati %d.' % (total, n)
        if notfound:
            buf += ' %d failile vastavaid tunnistuste kirjeid ei leitud.' % notfound
        protsess.viga = buf.strip()[:256]
        model.Session.commit()
    
    def _search_protsessid(self, q):
        q = q.filter(model.Arvutusprotsess.liik == model.Arvutusprotsess.LIIK_SALVESTAMINE)
        return q

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    sbuf = S3FileBuf()
    li = list(sbuf.s3file_list(DIGITEMPEL_ASICE_DIR))
    total = len(li)
    for ind, obj in enumerate(li):
        fn = obj.object_name
        basename = fn.split('/')[-1]
        tunnistusenr = basename.split('.')[0]
        print(f'leitud {basename}')
        if tunnistusenr == 'proov':
            data_dok = sbuf.s3file_get(fn)
            outfn = f'/tmp/{basename}'
            with open(outfn, 'wb') as f:
                f.write(data_dok)
            sbuf.s3file_remove(fn)
            print(f'salvestatud {outfn}')
    
