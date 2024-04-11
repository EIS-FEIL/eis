${h.not_top()}
<%include file="/common/message.mako"/>
% if not c.items:
${_("Valitud testiliigiga teste, kuhu saaks registreerida, praegu rohkem ei ole.")}
% else:
${h.form(h.url_current('create'), method='post', disablesubmit=True)}
${h.hidden('testiliik', c.testiliik)}
<div class="listdiv">
  ${h.rqexp()}
  <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
    <thead>
      <tr>
        <th></th>
        ${h.th(_("Test"))}
        ${h.th(_("Testimiskord"))}
        ${h.th(_("Toimumise aeg"))}
      </tr>
    </thead>
    <tbody>
      <% c.opilane = c.kasutaja.opilane %>
      % for n, rcd in enumerate(c.items):
      <%
         c.sooritaja = c.kiirvalik_id and model.Sooritaja.get_by_kasutaja(c.kasutaja.id, rcd.id)
         inputstyle = not c.sooritaja and 'style="display:none"' or ''
         trcls = n % 2 and 'evenback' or ''
         c.testimiskord = rcd
         c.test = rcd.test
      %>
      <tr class="${trcls}">
        <td>
          ${h.checkbox('valik_id', rcd.id, class_='valik_id')}
        </td>
        <td>
          ${c.test.nimi}
        </td>
        <td>${rcd.tahised}</td>
        <td>
          <span class="invisible">${rcd.alates and rcd.alates.isoformat() or ''}</span>${rcd.millal}
        </td>
      </tr>
      <tr class="rowinput-${rcd.id} ${trcls}" ${inputstyle}>
        <td></td>
        <td colspan="4">
          <%
            c.tsuffix = f'_{rcd.id}'
            c.reg_kool = True
          %>
          <%include file="/avalik/regamine/avaldus.testiseaded.mako"/>
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
<br/>
<script>
  function toggle_add(){   
     var visible = ($('input.valik_id:checked').length > 0);
     $('span#add').toggleClass('invisible', !visible);
     $('input[name="valik_id"]').each(function(ind, valik){
           var rcd_id = valik.value;
           $('.rowinput-'+rcd_id).toggle(valik.checked);
     });
  }
  $(function(){
    $('table#table_isikud').tablesorter();
    $('input.valik_id').click(toggle_add);
    toggle_add();
  });
</script>
</div>

<div class="text-right">
<span id="add" class="invisible">
  ${h.submit_dlg(_("Salvesta"))}
</span>
</div>
${h.end_form()}

% endif

