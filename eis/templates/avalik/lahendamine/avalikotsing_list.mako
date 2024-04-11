% if c.items != '':
${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid ülesandeid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav ülesanne"),
          msg_found_many=_("Leiti {n} tingimustele vastavat ülesannet"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
    ${h.th_sort('ylesanne.id', _("ID"))}
    ${h.th_sort('ylesanne.nimi', _("Nimetus"))}
    ${h.th(_("Õppeaine"))}
    ${h.th(_("Teema"))}
    ${h.th(_("Alateema"))}
    ${h.th_sort('ylesanne.aste_mask', _("Kooliaste"))}
    ${h.th(_("Testi liik"))}
    </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        ${rcd.id}
      </td>
      <td>
        ${h.link_to(rcd.nimi, url=h.url('lahendamine1', id=rcd.id), class_='LISTPOST')}
      </td>
      <td>
        <% yained = list(rcd.ylesandeained) %>
        % for yaine in yained:
        ${yaine.aine_nimi}<br/>
        % endfor
      </td>
      <td>
        % for yaine in yained:
        % for r in yaine.ylesandeteemad:
            ${r.teema_nimi}<br/>
        % endfor
        % endfor
      </td>
      <td>
        % for yaine in yained:
        % for r in yaine.ylesandeteemad:
            ${r.alateema_nimi}<br/>
        % endfor
        % endfor
      </td>
      <td>${rcd.aste_nimed or ''}</td>
      <td>
        % for tl in rcd.testiliigid:
        ${tl.nimi or ''}
        % endfor
      </td>
    </tr>
  % endfor
  </tbody>
</table>

<script>
  ## paneme lingile loetelutingimused kaasa
  $('.LISTPOST').click(function() {
    $('<form method="POST" style="display:none"><input type="hidden" name="list_url" class="list_url" value="'+$('input.list_url').val()+'" /></form>')
      .insertAfter($(this))
      .attr({
        action: $(this).attr('href')
      }).submit();
    return false;
  });
</script>
% endif
