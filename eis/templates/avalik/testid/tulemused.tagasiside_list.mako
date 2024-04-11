${h.hidden('list_url', h.get_list_url(nosort=True))}
<table width="100%" class="table table-borderless table-striped" border="0" >
<tbody>
% for sooritaja in c.items:
% if sooritaja.staatus == const.S_STAATUS_TEHTUD:
<tr>
  <td>
    ${h.link_to(sooritaja.nimi, h.url_current('show', id=sooritaja.id, lang=c.lang))}
  </td>
</tr>
% endif
% endfor
</tbody>
</table>
