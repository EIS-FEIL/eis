## Ülesannete valikul otsingu tulemuse näitamise vorm
<span id="progress"></span>
<%include file="/common/message.mako" />
% if c.items != '' and len(c.items) == 0:
${_("Otsingu tingimustele vastavaid ülesandeid ei ole")}
% elif c.items:
##${h.pager(c.items, form='#form_search_y')}
<% cnt = len(c.items) %>
${u'Fail sisaldab %d ülesannet' % cnt}
<table width="100%" class="table table-borderless table-striped singleselect" >
  <tr>
    ${h.th_sort('ylesanne.id', _("ID"))}
    ${h.th_sort('ylesanne.nimi', _("Nimetus"))}
    ${h.th_nosort('ylesandeteema.alateema_kood', _("Alateema"))}
    ${h.th_nosort('ylesandeteema.teema_kood', _("Teema"))}
    ${h.th_sort('ylesanne.arvutihinnatav', _("Arvutiga hinnatav"))}
    ${h.th_sort('ylesanne.max_pallid', _("Toorpunktid"))}
  </tr>
  % for item in c.items:
  <tr>
     <td>${item.id}
       ${h.hidden('y_id', item.id)}
     </td>
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
${h.submit_dlg()}
% if c.taidetud:
${h.checkbox('tyhjad', 1, label=_("Ära asenda juba valitud ülesandeid"),
onclick="$('.v-koik').toggle(!this.checked);$('.v-tyhi').toggle(this.checked);")}
% endif
<div style="height:2px"></div>
<%
  vyy = list(c.komplekt.valitudylesanded)
  cnt_vyy = len(vyy)
  vyy2 = [vy for vy in vyy if not vy.ylesanne_id]
  cnt_vyy2 = len(vyy2)
%>
% if cnt_vyy < cnt:
  <div class="v-koik">
    ${h.alert_notice(_("Failis olnud {d1} ülesandest valitakse ainult {d2}").format(d1=cnt, d2=cnt_vyy))}
  </div>
% endif               
% if cnt_vyy2 < cnt:
  <div class="v-tyhi" style="display:none">
    ${h.alert_notice(_("Failis olnud {d1} ülesandest valitakse ainult {d2}").format(d1=cnt, d2=cnt_vyy2))}
  </div>
% endif               
% endif
