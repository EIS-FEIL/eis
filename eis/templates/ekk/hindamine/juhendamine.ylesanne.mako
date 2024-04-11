${h.link_to(_("Ülesanne") + ' %d: %s' % (c.ylesanne.id,c.ylesanne.nimi),
h.url('ylesanne', id=c.ylesanne.id), target='_blank')}

<table width="100%"  class="table">
  <tr>
    <td class="fh">${_("Lahendusjuhis")}</td>
  </tr>
  <tr>
    <td>
      ${h.literal(c.ylesanne.get_juhis(c.lang))}
    </td>
  </tr>
</table>
<br/>

<table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
  <caption>${_("Hindamisaspektid")}</caption>
  <thead>
    <tr>
      <th>${_("Aspekt")}</th>
      <th>${_("Max pallid")}</th>
      <th>${_("Hindamisjuhend")}</th>
    </tr>
  </thead>
  <tbody>
    % if len(c.ylesanne.hindamisaspektid) == 0:
    <tr>
      <td colspan="4">${_("Ülesandel pole ühtegi hindamisaspekti")}</td>
    </tr>
    % endif

    % for n, rcd in enumerate(c.ylesanne.hindamisaspektid):
    <tr>
      <td>${rcd.aspekt_nimi}</td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>
        ${rcd.hindamisjuhis or rcd.aspekt.ctran.kirjeldus or ''}
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
<br/>

<table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      <th>${_("Küsimus")}</th>
      <th>${_("Vastus")}</th>
      <th>${_("Avalik")}</th>
      <th>${_("Küsija / küsimise aeg")}</th>
      <th>${_("Vastaja / vastamise aeg")}</th>
    </tr>
  </thead>
  <tbody>
    % if len(c.ylesanne.hindamiskysimused) == 0:
    <tr>
      <td colspan="5">Ei ole küsimusi</td>
    </tr>
    % endif

    % for n, rcd in enumerate(c.ylesanne.hindamiskysimused):
    <tr>
      <td>${rcd.kysimus}</td>
      <td>${rcd.vastus}
        ${h.btn_to_dlg(_("Vasta"), h.url('hindamine_edit_juhendamine',
        toimumisaeg_id=c.toimumisaeg.id,id=c.item.id,hindamiskysimus_id=rcd.id, lang=c.lang, sub='vastus',partial=True), 
        title=_("Vastus"), width=560)}        
      </td>
      <td>${h.sbool(rcd.avalik)}</td>
      <td>
        ${rcd.kysija_kasutaja.nimi}
        ${h.str_from_datetime(rcd.kysimisaeg)}
      </td>
      <td>
        % if rcd.vastaja_kasutaja:
        ${rcd.vastaja_kasutaja.nimi}
        ${h.str_from_datetime(rcd.vastamisaeg)}
        % endif
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
<br/>

${h.btn_to_dlg(_("Lisa hindamisküsimus"), h.url('hindamine_edit_juhendamine',
toimumisaeg_id=c.toimumisaeg.id,id=c.item.id, lang=c.lang,
alatest_id=c.alatest_id, komplekt_id=c.komplekt_id, sub='vastus', partial=True), 
title=_("Ülesanne"), width=560)}
