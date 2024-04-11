% if c.sessioonid:
<div style="height:12px"> </div>
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th(_('Testsessioon'))}
      ${h.th(_('Õppeaasta'))}
      ${h.th(_('Testiliik'))}
      ${h.th(_('Leping'))}
    </tr>
  </thead>
  <tbody>
    <% cnt = -1 %>
    % for sessioon in c.sessioonid:
    <tr>
      % if sessioon:
      <td>${sessioon.nimi}</td>
      <td>${sessioon.oppeaasta}</td>
      <td>${sessioon.testiliik_nimi}</td>
      % else:
      <td colspan="3">${_("Üldtingimused")}</td>
      % endif
      <td>
        <%
           sessioon_id = sessioon and sessioon.id or None
           is_first = True
        %>
      % for leping_id in c.data[sessioon_id]:
        % if not is_first:
        <p> </p>
        % endif
        <div>
       <%
         cnt += 1
         leping = model.Leping.get(leping_id)
         lleping = c.kasutaja.get_labiviijaleping(leping_id, sessioon_id)
         is_first = False
       %>
        <strong>${leping.nimetus}</strong><br/>
        <%
          name = 'lep-%d.nous' % cnt
          fldid = h.toid(name)
        %>
        <label class="custom-control custom-checkbox custom-control-inline ">
          <input type="checkbox" onchange="toggle_kinnita(this)" ${lleping and lleping.noustunud and 'checked="true"' or ''}
                 class="nous custom-control-input" name="${name}" value="1" id="${fldid}">
          <span class="custom-control-label" for="${fldid}">
            ${_('Olen tutvunud töövõtulepingu tingimustega (kättesaadavad <a target="_blank" href="{url}">siin</a>) ja olen töövõtulepingu tingimustega nõus.').format(url=leping.url)}
          </span>
        </label>
        
        ${h.hidden('lep-%d.leping_id' % cnt, leping_id)}
        ${h.hidden('lep-%d.testsessioon_id' % cnt, sessioon_id)}       
        % if lleping and lleping.noustunud:
        <div>${_("Nõusolek antud")} ${h.str_from_date(lleping.noustunud)}</div>
        % endif
        % if leping.on_hindajaleping:
        <div class="nous3">
        ${h.checkbox('lep-%d.on_hindaja3' % cnt, 1, checked=lleping and lleping.on_hindaja3, label=_("Soovin osaleda 3. hindamisel"))}
        </div>
        % endif
        </div>
        % endfor
      </td>
    </tr>
    % endfor
  </tbody>
</table>
<script>
  function toggle_kinnita()
  {
    $('#kinnita').toggle($('input.nous:checked').length>0);
    $.each($('input.nous'), function(n, item){
       var nous3 = $(item).closest('div').find('.nous3');
       nous3.toggle($(item).prop('checked'));
    });
  }
  $(function(){
    toggle_kinnita();
  });
</script>
<br/>
% endif
