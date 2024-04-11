<% 
   rc = True 
%>
<%include file="/common/message.mako"/>
<table class="table table-align-top">
<thead>
  <tr>
    <th>${_("Sisuplokk")}</th>
    <th>${_("Küsimus")}</th>
    <th>${_("Selgitus")}</th>
    <th>${_("Küsimuse punktid")}</th>
    <th>${_("Hindamine")}</th>
    <th>${_("Sisuploki punktid")}</th>
    <th>${_("Kontroll")}</th>
  </tr>
</thead>
<tbody>
  % for cnt, plokk in enumerate(c.item.sisuplokid):
  <%
    sp_pallid = 0
    plokk_kysimused = []
    for k in plokk.kysimused:
       if k.kood:
           t = k.tulemus
           if t in model.Session.deleted:
              t = None
           if t:
               tahised = set([hm.tahis for hm in t.hindamismaatriksid if hm.tahis])
               pallid = t.get_max_pallid()
               sp_pallid += pallid or 0
               plokk_kysimused.append((k, t, tahised, pallid))
           elif k.kood:
               # MP, mittehinnatav kuulamise järg
               plokk_kysimused.append((k, None, None, None))
    if not plokk_kysimused:
       plokk_kysimused = [None]
    rowspan = len(plokk_kysimused)
  %>
  % for ind_k, r in enumerate(plokk_kysimused):
  <tr>
    <%
      if r:
          k, t, tahised, t_pallid = r
      else:
          k = t = tahised = t_pallid = None
    %>
    % if ind_k == 0:
    <td rowspan="${rowspan}">
      <%
        title = str(cnt+1)
        if plokk.tahis:
            title += ' (%s)' % (plokk.tahis)
      %>
      ${h.link_to(title, h.url('ylesanne_edit_sisuplokk', ylesanne_id=c.item.id, id=plokk.id))}
    </td>
    % endif

    % if not k:
    <td colspan="4"></td>
    % else:
    <td>
        ${k.kood}
        % if t and t.yhisosa_kood:
        (${_("ühisosa kood")} ${t.yhisosa_kood})
        % endif
    </td>
    <td>
      % if k.selgitus:
      <div class="d-md-none d-xs-block text-truncate" style="width:80px">
        ${k.selgitus}
      </div>
      <div class="d-none d-md-block">
        ${k.selgitus}
      </div>
      % endif
      % for err in (c.k_errors.get(k.kood) or []):
      ${h.alert_error2(err)}
      % endfor
      % for err in (c.k_warnings.get(k.kood) or []):
      ${h.alert_error2(err)}
      % endfor
    </td>
    <td>
      % if t:
      % if t.naide:
      ${_("näide")}
      % else:
      ${h.fstr(t_pallid)} p
      % endif
      % endif
    </td>
    <td nowrap>
      % if t:
      % if t.arvutihinnatav:
      ${_("Arvutihinnatav")}
      % else:
      ${_("Pole arvutihinnatav")}
      % endif
      % for tahis in tahised:
      <div>${tahis}</div>
      % endfor
      % endif
    </td>
    % endif

    % if ind_k == 0:
    <td rowspan="${rowspan}">
      ${h.fstr(sp_pallid)} p
      % if plokk.max_pallid is not None and sp_pallid > plokk.max_pallid:
      <% sp_pallid = plokk.max_pallid %>
      ${_("max {p}p").format(p=h.fstr(sp_pallid))}
      % endif
      % if plokk.ymardamine and sp_pallid:
      ${_("ümardatakse {p}p").format(p=h.fstr(round(sp_pallid + .0001)))}
      % endif
    </td>
    <td rowspan="${rowspan}">
      <% rc_p = True %>
      % for err in (c.sp_errors.get(plokk.id) or []):
      ${h.alert_error2(err)}
      <% rc_p = False %>
      % endfor
      % if rc_p:
        ${_("Kontrollitud")}
      % endif
    </td>
    % endif
  </tr>
  % endfor
  % endfor
</tbody>
</table>


% if c.item.hindamisaspektid:
<% ha_pallid = sum([(ha.max_pallid or 0)*ha.kaal for ha in c.item.hindamisaspektid]) %>
${_("Ülesande hindamisaspektide punktide summa on {p}.").format(p=h.fstr(ha_pallid))}
<br/>
${_("Ülesanne annab kokku max {p} punkti.").format(p=h.fstr(c.item.max_pallid))}
% else:
${_("Ülesande sisuplokkide punktide summa on {p}.").format(p=h.fstr(c.item.max_pallid))}
% endif
<br/>
% if c.item.arvutihinnatav:
${_("Ülesanne on arvutihinnatav.")}
% else:
${_("Ülesanne ei ole arvutihinnatav.")}
% endif
<br/>
% for err in c.y_errors:
${h.alert_error(err)}
% endfor
% if c.rc:
${_("Ülesanne vastab nõuetele.")}
% else:
${_("Ülesanne ei vasta nõuetele.")}
% endif

