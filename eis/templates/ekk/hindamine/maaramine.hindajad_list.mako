${h.pager(c.items)}
% if c.items:
<%
  on_koht = c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or \
     c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD or \
     c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD or \
     c.toimumisaeg.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
%>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % if c.kaks_hindajat:
      ${h.th_sort('kasutaja_1.perenimi kasutaja_1.eesnimi', _("I hindaja"))}
      ${h.th_sort('labiviija_1.tahis', _("Tähis"))}
      ${h.th_sort('kasutaja_2.perenimi kasutaja_2.eesnimi', _("II hindaja"))}
      ${h.th_sort('labiviija_2.tahis', _("Tähis"))}
      % else:
      ${h.th_sort('kasutaja_1.perenimi kasutaja_1.eesnimi', _("Hindaja"))}
      ${h.th_sort('labiviija_1.tahis', _("Tähis"))}
      % endif

      % if on_koht:
      ${h.th_sort('labiviija_1.testikoht_id', _("Soorituskoht"))}
      % endif     
      ${h.th_sort('hindamiskogum.tahis', _("Hindamiskogum"))}
      % if c.testimiskord.sisaldab_valimit:
      ${h.th_sort('labiviija_1.valimis', _("Valim"))}
      % endif
      ${h.th_sort('labiviija_1.lang', _("Keel"))}
      ${h.th_sort('labiviija_1.staatus', _("Olek"))}
      ${h.th_sort('labiviija_1.planeeritud_toode_arv', _("Planeeritud hinnata"))}
      ${h.th_sort('labiviija_1.hinnatud_toode_arv', _("Tegelikult hinnatud"))}
      ${h.th('')}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <%
       if c.kaks_hindajat:
         kogum, hindaja1, hindaja2 = rcd
       else:
         kogum, hindaja1 = rcd
         hindaja2 = None
       hindaja = hindaja1 or hindaja2
       hkasutaja1 = hindaja1 and hindaja1.kasutaja or None
       hkasutaja2 = hindaja2 and hindaja2.kasutaja or None
    %>
    <tr>
      <td>
	    % if hkasutaja1:
        ${h.link_to(hkasutaja1.nimi,
        h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=hindaja1.id))}
        % endif
      </td>
      <td>
        % if hindaja1:
        ${hindaja1.tahis}
        % endif
      </td>
      % if c.kaks_hindajat:
      <td>
        % if hindaja2 and hkasutaja2:
        ${h.link_to(hkasutaja2.nimi,
        h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=hindaja2.id))}
        % endif
      </td>
      <td>
        % if hindaja2:
        ${hindaja2.tahis}
        % endif
      </td>
      % endif

      % if on_koht:
      <td>
        % if hindaja.testikoht:
        ${hindaja.testikoht.koht.nimi}
        % endif
      </td>
      % endif
      <td>${kogum.tahis}</td>
      % if c.testimiskord.sisaldab_valimit:
      <td>
        % if hindaja.valimis:
        ${_("Valim")}
        % endif
      </td>
      % endif
      <td>${model.Klrida.get_lang_nimi(hindaja.lang)}</td>
      <td>
        ${hindaja.staatus_nimi}
      </td>
      <td>
        ${hindaja.planeeritud_toode_arv}
        ${h.edit_js("open_wnd(%s, '%s')" % (hindaja.id,hindaja.planeeritud_toode_arv or ''))}
      </td>
      <td>
        % if hindaja1:
          ${hindaja1.hinnatud_toode_arv or 0}
        % endif
        % if hindaja1 and hindaja2:
        /
        % endif
        % if hindaja2:
          ${hindaja2.hinnatud_toode_arv or 0}
        % endif
      </td>
      <td>
        % if (not hindaja1 or not hindaja1.toode_arv) and (not hindaja2 or not hindaja2.toode_arv):
        ${h.remove(h.url_current('delete', id=hindaja.id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<script>
  function open_wnd(hindaja_id, toode_arv)
  {
    var contents = $('#wnd_arv').html().replace('__ID__', hindaja_id).replace('__ARV__', toode_arv);
    open_dialog({'contents_html': contents,
                 'title': '${_("Planeeritud hindamiste arv")}',
                 'size': 'sm',
                 'backdrop': true});
  }
</script>
<div id="wnd_arv" style="visibility:hidden;display:none">
${h.form_save('__ID__', form_name='fsarv', class_='fsarv')}
<%
   if c.sooritajatearvud:
      maxvalue = max([r['total'] for r in c.sooritajatearvud.values()])
   else:
      maxvalue = c.toimumisaeg.get_sooritajatearv()
%>
${h.posint5('planeeritud_toode_arv', '__ARV__', maxvalue=maxvalue)}
${h.submit()}
${h.end_form()}
</div>
