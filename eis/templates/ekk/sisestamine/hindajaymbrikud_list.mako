<div>
      % if c.items:
      <table width="100%" class="table tablesorter list" border="0" >
        <thead>
          <tr>
            ${h.th(_('Ümbriku tähis'), sorter='text')}
            ${h.th(_('Ümbriku liik'))}
            ${h.th(_('Hindamiskogum'))}
            ${h.th(_('Soorituskoht'))}
            ${h.th(_('Soorituskeel'))}
            ${h.th(_('Tööde arv ümbrikus'))}
            ${h.th('', sorter='false')}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <%
            testiprotokoll = rcd.testiprotokoll
            testipakett = testiprotokoll.testipakett
            tagastusymbrikuliik = rcd.tagastusymbrikuliik
          %>
          <tr>
            <td>${rcd.tahised}</td>
            <td>${tagastusymbrikuliik.nimi}</td>
            <td>
              % for hk in tagastusymbrikuliik.hindamiskogumid:
              ${hk.tahis}
              % endfor
            </td>
            <td>${testipakett.testikoht.koht.nimi}</td>
            <td>${model.Klrida.get_lang_nimi(testipakett.lang)}</td>
            <td>
              ##${testiprotokoll.tehtud_toodearv}
              ${rcd.tehtud_toodearv}
            </td>
            <td>
              ${h.btn_remove(id=rcd.id, value=_('Tühista'),
              confirm=_('Kas oled kindel, et soovid ümbriku väljastamise tühistada?'))}
              ${h.btn_to(_('Arvuta uuesti'), h.url_current('update', id=rcd.id), method='post')}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
      % endif

      <table class="table table-responsive">
        <tr>
          <td>${_("Hindamiseks antud tööde arv kokku")}</td>
          <td>${c.hindaja1.toode_arv or 0} </td>
        </tr>
        <tr>
          <td>${_("Plaanitud hinnata töid")}</td>
          <td>${c.hindaja1.planeeritud_toode_arv}</td>
        </tr>
      </table>
</div>
