## Ülesannete valikul otsingu tulemuse näitamise vorm
<span id="progress"></span>
<%include file="/common/message.mako" />
% if c.items != '' and len(c.items) == 0:
${_("Otsingu tingimustele vastavaid ülesandeid ei ole")}
% elif c.items:
${h.pager(c.items, form='#form_search_y')}
<table width="100%" class="table table-borderless table-striped singleselect" >
  <tr>
    <th></th>
    ${h.th_sort('ylesanne.id', _("ID"))}
    ${h.th_sort('ylesanne.nimi', _("Nimetus"))}
    ${h.th_nosort('ylesandeteema.alateema_kood', _("Alateema"))}
    ${h.th_nosort('ylesandeteema.teema_kood', _("Teema"))}
    ${h.th_sort('ylesanne.arvutihinnatav', _("Arvutiga hinnatav"))}
    ${h.th_sort('ylesanne.max_pallid', _("Toorpunktid"))}
  </tr>
  % for item in c.items:
  <tr>
    <td>
      % if set(c.komplekt.keeled) & set(item.keeled) == set(c.komplekt.keeled):
      ${h.submit(_("Vali"),id='ylesanne_id_%d' % item.id)}
      % endif
    </td>
    <td>${item.id}</td>
    <td>${h.link_to(item.nimi, h.url('ylesanne', id=item.id), target='_blank')}
    </td>
    <% yained = list(item.ylesandeained) %>
    <td>
      % for yaine in yained:
      % for r in yaine.ylesandeteemad:
      ${r.alateema_nimi}<br/>
      % endfor
      % endfor
    </td>
    <td>
      % for yaine in yained:
      % for r in yaine.ylesandeteemad:
      ${r.teema_nimi}<br/>
      % endfor
      % endfor
    </td>
    <td>${h.sbool(item.arvutihinnatav)}</td>
    <td>${h.fstr(item.max_pallid)}</td>
  </tr>
  % endfor
</table>

% endif
