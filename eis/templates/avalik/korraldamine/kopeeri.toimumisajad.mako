## Sama testimiskorra teise toimumisaja valik, 
## et selle korraldusandmed kopeerida

${h.form_save(None, h.url_current('create'))}
${h.hidden('sub', 'kopeeri')}
<table class="table table-borderless table-striped">
  <col/>
  <col/>
  <col width="70px"/>
  <col width="70px"/>
  <thead>
    <tr>
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Testiosa"))}
      ${h.th(_("Ruumid"))}
      ${h.th(_("Läbiviijad"))}
    </tr>
  </thead>
  <tbody>
    % for osa, ta, on_testikoht, on_ruumid, on_labiviijad in c.tadata:
    <tr>
      <td>
        % if on_testikoht and ta != c.toimumisaeg:
        ${h.radio('ta_id', ta.id, label=ta.tahised)}
        % else:
        <div class="pl-5">${ta.tahised}</div>
        % endif
      </td>
      <td>${osa.nimi}</td>
      % if not on_testikoht:
      <td colspan="2">
        ${_("Toimub mujal")}
      </td>
      % else:
      <td>
        % if on_ruumid:
        ${h.mdi_icon('mdi-check', style="color:#00b140", title=_("Ruumid määratud"))}
        % elif on_ruumid == False:
        ${h.mdi_icon('mdi-alert', style="color:#fb786e", title=_("Ruumid määramata"))}
        % else:
        -
        % endif
      </td>
      <td>
        % if on_labiviijad:
        ${h.mdi_icon('mdi-check', style="color:#00b140", title=_("Läbiviijad määratud"))}
        % elif on_labiviijad == False:
        ${h.mdi_icon('mdi-alert', style="color:#fb786e", title=_("Läbiviijad määramata"))}
        % else:
        -
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>

% if ta.labiviijate_jaotus:
<div id="cplvr" class="py-1" style="display:none">
  <div class="d-flex flex-wrap">
    ${h.flb(_("Kopeeritavad läbiviijate rollid"))}
    <div class="pl-4">
      % for g_id, g_nimi in c.lvrollid:
      <% tacls = ' '.join([f'tag-{ta_id}' for ta_id, rollid_id in c.ta_lvr_id.items() if g_id in rollid_id]) %>
      <div class="tag ${tacls}">${h.checkbox('lvr_id', g_id, label=g_nimi)}</div>
      % endfor
    </div>
  </div>
</div>
% endif

<div id="submitcopy" class="py-1" style="display:none">
  ${h.submit(_("Kopeeri"), clicked=True, onclick="set_spinner($(this))")}
</div>
${h.end_form()}

<script>
  $('input[name="ta_id"]').click(function(){
    ## kuvame rollid, mida võiks saada kopeerida
    var notag = $('#cplvr .tag:not(.tag-' + this.value);
    notag.hide();
    notag.find('input').prop('checked', false);
    var tag = $('#cplvr .tag-' + this.value);
    tag.show().prop('checked',true);
    $('#cplvr').toggle(tag.length > 0);
    $('#submitcopy').show();
  });
</script>
