import unicodedata

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SaabumisedController(BaseResourceController):
    """Turvakottide ja ümbrike saabumise registreerimine
    """
    _permission = 'sisestamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/sisestamine/saabumine.mako'

    def index(self):
        self._copy_search_params()
        return self.render_to_response(self._INDEX_TEMPLATE)

    @action(renderer='json')
    def create(self):
        self._copy_search_params()
        if self.c.kotinr:
            # turvakoti saabumine
            err, msg = self._create_turvakott()
        else:
            # ümbriku saabumine
            err, msg = self._create_ymbrik()

        return [err, msg]

    def _create_turvakott(self):
        "Turvakoti saabumine"
        msg = None
        err = False
        
        # skanner loeb - asemel +, asendame õigeks
        self.c.kotinr = self.c.kotinr.replace('+','-').upper()

        q = model.Turvakott.query.filter_by(kotinr=self.c.kotinr)
        self.c.kott = q.first()
        if not self.c.kott:
            msg = _('Numbriga {s} turvakotti ei ole').format(s=self.c.kotinr)
            err = True
        elif self.c.kott.suund == const.SUUND_VALJA:
            msg = _('Numbriga {s} turvakott on väljastuskott ja seda ei peaks tagastama').format(s=self.c.kotinr)
            err = True
        else:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid and self.c.kott.testipakett.testikoht.testiosa.test.testiliik_kood not in liigid:
                msg = _('Turvakott {s} on seotud testiga, mille liik ei ole kasutajale sisestamiseks lubatud testiliikide seas').format(s=self.c.kotinr)
                err = True
                
            elif self.c.kott.staatus in (const.M_STAATUS_VALJASTATUD, const.M_STAATUS_TAGASTAMISEL):
                self.c.kott.staatus = const.M_STAATUS_TAGASTATUD
                model.Session.commit()
                msg = _('Turvakoti {s1} saabumine on registreeritud. Turvakott oli väljastatud soorituskohale: {s2}').format(
                      s1=self.c.kotinr, s2=self.c.kott.testipakett.testikoht.koht.nimi)
                q = model.SessionR.query(sa.func.count(model.Turvakott.id)).\
                    filter(model.Turvakott.staatus.in_((const.M_STAATUS_VALJASTATUD, const.M_STAATUS_TAGASTAMISEL))).\
                    filter(model.Turvakott.suund==const.SUUND_TAGASI).\
                    join(model.Turvakott.testipakett).\
                    filter(model.Testipakett.testikoht_id==self.c.kott.testipakett.testikoht_id)
                cnt = q.scalar()
                if cnt == 1:
                    msg += _(', kust on tagastamata veel {s} turvakott.').format(s=cnt)
                elif cnt > 1:
                    msg += _(', kust on tagastamata veel {s} turvakotti.').format(s=cnt)
                else:
                    msg += _(', kust on kõik turvakotid nüüd tagastatud.')

            else:
                msg = ('Turvakoti {s1} staatus on: {s2}').format(s1=self.c.kotinr, s2=self.c.kott.staatus_nimi)
        return err, msg

    def _create_ymbrik(self):
        "Ümbriku saabumine"
        msg = None
        err = False
        
        if self.c.y_tahis:
            # skanner loeb - asemel +, asendame õigeks
            self.c.y_tahis = self.c.y_tahis.replace('+','-').upper()
            # peaümbrikul olev keele kood loetakse mingite diakriitiliste kriipsudega, mis tuleb eemaldada
            self.c.y_tahis = self.c.y_tahis.replace('`','')
            self.c.y_tahis = ''.join((c for c in unicodedata.normalize('NFD', self.c.y_tahis) \
                                      if unicodedata.category(c) != 'Mn'))

            # ümbriku tähis võib olla 6-osaline (kui on liigiga ümbrik) või 5-osaline (peaümbrik)
            li = self.c.y_tahis.split('-')
            if len(li) == 5:
                # kui on peaymbrik 5-kohalise tähisega, siis eraldame keele
                # millel on 4-kohaline tähis
                testikoht_tahis = '-'.join(li[:4])
                lang = li[4].lower()
                self.c.ymbrik = model.Tagastusymbrik.query.\
                                filter_by(tahised=testikoht_tahis).\
                                join(model.Tagastusymbrik.testipakett).\
                                filter(model.Testipakett.lang==lang).\
                                first()
            else:
                # ümbrikuliigile vastava kirje korral on sama tähis ka kirjes

                # kahe protokollirühma ümbriku tähises on protokollirühmade vahel kaldkriips,
                # mille asemel skanner valesti,
                # 3757-E-L-002-01/02-1 asemel 3757-E-L-002-01-O02-1, asendame "-O" -> "/"
                if (len(li) == 7) and (li[-2][0] == 'O'):
                    li[-3:-1] = [li[-3]+'/'+li[-2][1:]]
                    self.c.y_tahis = '-'.join(li)
                self.c.ymbrik = model.Tagastusymbrik.query.\
                                filter_by(tahised=self.c.y_tahis).\
                                first()
        if not self.c.ymbrik:
            msg = _('Numbriga {s} ümbrikku ei ole').format(s=self.c.y_tahis)
            err = True
        else:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid and self.c.ymbrik.testipakett.testikoht.testiosa.test.testiliik_kood not in liigid:
                msg = _('Ümbrik {s} on seotud testiga, mille liik ei ole kasutajale sisestamiseks lubatud testiliikide seas').format(s=self.c.y_tahis)
                err = True
                
            elif self.c.ymbrik.staatus in (const.M_STAATUS_VALJASTATUD, const.M_STAATUS_HINDAJA, const.M_STAATUS_LOODUD):
                hindaja = self.c.ymbrik.labiviija
                self.c.ymbrik.labiviija = None
                if hindaja:
                    self.c.ymbrik.staatus = const.M_STAATUS_HINNATUD
                else:
                    self.c.ymbrik.staatus = const.M_STAATUS_TAGASTATUD
                model.Session.commit()
                if hindaja:
                    msg = _('Ümbriku {s1} saabumine on registreeritud. Ümbrik oli väljastatud hindajale {s2}').format(
                          s1=self.c.y_tahis, s2=hindaja.kasutaja.nimi)
                else:                   
                    msg = _('Ümbriku {s1} saabumine on registreeritud. Ümbrik oli väljastatud soorituskohale: {s2}').format(
                          s1=self.c.y_tahis, s2=self.c.ymbrik.testipakett.testikoht.koht.nimi)
                    q = model.SessionR.query(sa.func.count(model.Tagastusymbrik.id)).\
                        filter(model.Tagastusymbrik.staatus.in_((const.M_STAATUS_VALJASTATUD, const.M_STAATUS_LOODUD))).\
                        join(model.Tagastusymbrik.testipakett).\
                        filter(model.Testipakett.testikoht_id==self.c.ymbrik.testipakett.testikoht_id)
                    cnt = q.scalar()
                    if cnt == 1:
                        msg += _(', kust on tagastamata veel {s} ümbrik.').format(s=cnt)
                    elif cnt > 1:
                        msg += _(', kust on tagastamata veel {s} ümbrikku.').format(s=cnt)
                    else:
                        msg += _(', kust on kõik ümbrikud nüüd tagastatud.')
            else:
                msg = _('Ümbriku {s1} staatus on: {s2}. Ümbrik oli väljastatud soorituskohale: {s3}').format(
                      s1=self.c.y_tahis, s2=self.c.ymbrik.staatus_nimi, s3=self.c.ymbrik.testipakett.testikoht.koht.nimi)
        return err, msg
