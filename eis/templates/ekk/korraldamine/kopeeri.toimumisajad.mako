## Sama testimiskorra teise toimumisaja valik, 
## et selle korraldusandmed kopeerida

${h.form_save(None, h.url('korraldamine_soorituskohad',
toimumisaeg_id=c.toimumisaeg.id))}
${h.hidden('sub', 'kopeeri')}
<div class="my-1">
  ${h.checkbox('koht_yle', label=_("Kirjuta kohtadele määramine üle ka siis, kui sooritaja on juba kohale määratud"))}
</div>
<table class="table table-borderless table-striped">
  <col/>
  <col/>
  <tbody>
    % for osa, ta in c.tadata:
    <tr>
      <td>
        % if ta != c.toimumisaeg:
        ${h.radio('ta_id', ta.id, label=ta.tahised)}
        % else:
        <div class="pl-5">${ta.tahised}</div>
        % endif
      </td>
      <td>${osa.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>

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

${h.end_form()}

