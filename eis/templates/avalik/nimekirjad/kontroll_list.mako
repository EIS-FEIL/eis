
<table width="100%" class="table table-borderless table-striped tablesorter" >
  <caption>${_("Õpilased")}</caption>
  <thead>
    <tr>
      ${h.th(_("Isikukood"))}
      ${h.th(_("Eesnimi"))}
      ${h.th(_("Perekonnanimi"))}
      ${h.th(_("Paralleel"))}
      ${h.th(_("Test"))}
      ${h.th(_("Kursus"))}
      ${h.th(_("Keel"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Eritingimused"))}      
    </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
    <%
       opilane, sooritaja = rcd
       row = c.prepare_row(rcd)
    %>
    <tr>
      % for value in row[:-2]:
      <td>${value}</td>
      % endfor
      <td>
        % if sooritaja:
          % if sooritaja.staatus == const.S_STAATUS_TEHTUD:
          ${h.link_to(sooritaja.staatus_nimi, 
                      h.url('nimekirjad_kontroll_tulemus', id=sooritaja.id))}
          % else:
          ${sooritaja.staatus_nimi}
          % endif
        % endif
      </td>
      <td>
        % if sooritaja and sooritaja.on_erivajadused:
        ${h.link_to_dlg(_("Jah"), h.url_current('show', id=sooritaja.id, sub='erivajadus'),
              title=_("Eritingimused"), width=800)}        
        % endif
      </td>
    </tr>
  % endfor
  </tbody>
</table>
