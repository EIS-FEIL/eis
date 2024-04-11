<% 
  c.can_update = c.user.has_permission('nimekirjad', const.BT_UPDATE, c.testimiskord) and c.kand != '1'
%>
% if len(c.items) > 0:
% if c.cnt:
% if c.kand=='1':
${h.alert_notice(_("Õppeasutusele on tulemuste vaatamise õiguse andnud {n} sooritajat").format(n='<span class="brown">%d</span>' % c.cnt), False)}
% else:
${h.alert_notice(_("Õppeasutusest on registreeritud {n} õpilast").format(n='<span class="brown">%d</span>' % c.cnt), False)}
% endif
% endif
<table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
  <caption>${_("Sooritajad")}</caption>
  <col width="20px"/>
  <thead>
    <tr>
      % for label in c.header:
      ${h.th(label)}
      % endfor
      % if c.can_update:
      ${h.th('', sorter="false")}
      % endif
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <%
      row = c.prepare_item(rcd)
      sooritaja = rcd[0]
      sooritaja_id = sooritaja.id
      url_rcd = not c.testimiskord.sooritajad_peidus \
          and h.url('nimekiri_kanne', testimiskord_id=c.testimiskord_id, id=sooritaja_id)
      url_del = c.can_update and not sooritaja.muutmatu \
          and sooritaja.staatus > const.S_STAATUS_TYHISTATUD \
          and sooritaja.staatus <= const.S_STAATUS_ALUSTAMATA \
          and sooritaja.kool_voib_tyhistada(c.user.koht_id, c.test.testiliik_kood) \
          and h.url('nimekiri_delete_sooritaja', testimiskord_id=c.testimiskord_id, id=sooritaja_id)
      can_delete = sooritaja.staatus == const.S_STAATUS_REGAMATA
    %>
    <tr>
      % for ind, value in enumerate(row):
      <td>
        % if ind == 1 and url_rcd:
        ## nimi, mis pole peidus
        <span style="display:none;">${value}</span>
        ${h.link_to(value, url_rcd)}
        % else:
        ${value}
        % endif
      </td>
      % endfor
      % if c.can_update:
      <td>
        % if url_del:
        % if can_delete:
        ${h.remove(url_del)}
        % else:
        <a href="${url_del}" class="tyhist" title="${_("Tühista")}">${h.mdi_icon('mdi-delete')}</a>
        % endif
        % endif
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
</table>
% else:
${_("Sooritajaid pole nimekirja lisatud")}
% endif

<div id="tyhistamine" class="d-none">
  ${h.form_save(None, form_name="form_del", class_="form-del")}  
  <div class="form-group mb-3">
    ${h.flb3(_("Põhjus"),'pohjus')}
    ${h.textarea('pohjus', '', rows=4, ronly=False)}
  </div>
  ${h.submit(_("Tühista registreering"))}
  ${h.end_form()}
</div>
<script>
  $('a.tyhist').click(function(){
    $('div#tyhistamine form').prop('action', $(this).prop('href'))
    dialog_el($('div#tyhistamine'), "${_("Registreeringu tühistamine")}");
    return false;
  });
</script>
