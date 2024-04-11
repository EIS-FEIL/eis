<%inherit file="/common/tabpage.mako"/>
<% c.r_tab = 'juhend' %>
<%include file="hindamine_r_tabs.mako"/>
<div id="hindamine_r_body">
<% c.found = False %>
% if c.on_kriteeriumid:
<% c.found = True %>
${self.hindamiskriteeriumid()}
% else:
${self.hindamisaspektid()}
${self.yksikkysimused()}
${self.hindamisfailid()}
% endif

% if not c.found:
${h.alert_notice(_("Hindamisjuhendit ei ole"), False)}
% endif
</div>

<%def name="hindamiskriteeriumid()">
<table width="100%" border="0"  class="table table-striped tablesorter table-align-top vertmar">
  <caption>${_("Hindamiskogumi {s} hindamiskriteeriumid").format(s=c.hindamiskogum.tahis)}</caption>
  <thead>
    <tr>
      <th>${_("Aspekt")}</th>
      <th>${_("Max pallid")}</th>
      <th>${_("Hindamisjuhend")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.hindamiskogum.hindamiskriteeriumid):
    <tr>
      <% aspekt = rcd.aspekt %>
      <td>${rcd.aspekt_nimi}</td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>
        <% pkirjeldused = list(rcd.kritkirjeldused) %>
        % if len(pkirjeldused):
        <table width="100%"  class="table table-borderless table-striped tablesorter">
          <col width="20"/>
          <col/>
          <thead>
            <tr>
              ${h.th(_("Punktid"), sorter="digit")}
              ${h.th(_("Kirjeldus"))}
            </tr>
          </thead>
          <tbody>
          % for r in pkirjeldused:
          <tr>
            <td>${h.fstr(r.punktid)}p</td>
            <td>${r.kirjeldus and r.kirjeldus.replace('\n','<br/>')}</td>
          </tr>
          % endfor
          </tbody>
        </table>
        % endif

        ${rcd.hindamisjuhis or aspekt and aspekt.ctran.kirjeldus or ''}
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
</%def>

<%def name="hindamisaspektid()">
<% items = list(c.ylesanne.hindamisaspektid) %>
% if len(items):
<% c.found = True %>
<table width="100%" border="0"  class="table table-striped tablesorter table-align-top vertmar">
  <caption>${_("Hindamisaspektid")}</caption>
  <thead>
    <tr>
      <th>${_("Aspekt")}</th>
      <th>${_("Max pallid")}</th>
      <th>${_("Hindamisjuhend")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(items):
    <tr>
      <% aspekt = rcd.aspekt %>
      <td>${rcd.aspekt_nimi}</td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>
        <% pkirjeldused = list(rcd.punktikirjeldused) %>
        % if len(pkirjeldused):
        <table width="100%"  class="table table-borderless table-striped">
          <col width="20"/>
          <col/>
          % for r in pkirjeldused:
          <tr>
            <td>${h.fstr(r.punktid)}p</td>
            <td>${r.kirjeldus and r.kirjeldus.replace('\n','<br/>')}</td>
          </tr>
          % endfor
        </table>
        % endif
        ${rcd.hindamisjuhis or aspekt and aspekt.ctran.kirjeldus or ''}
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
% endif
</%def>

<%def name="yksikkysimused()">
<%
  naidisvastused = []
  for sp in c.ylesanne.sisuplokid:
     for kysimus in sp.kysimused:
        tulemus = kysimus.tulemus
        naidisvastus = tulemus and tulemus.tran(c.lang).naidisvastus
        if naidisvastus:
           max_pallid = tulemus.get_max_pallid()
           naidisvastused.append((kysimus, max_pallid, naidisvastus))
           c.found = True
%>
% if len(naidisvastused):
<table width="100%" border="0"  class="table table-striped tablesorter table-align-top vertmar">
  <thead>
    <tr>
      <th>${_("Küsimuse kood")}</th>
      <th>${_("Max pallid")}</th>
      <th>${_("Näidisvastus või hindamisjuhend")}</th>      
    </tr>
  </thead>
  <tbody>
    % for (kysimus, max_pallid, naidisvastus) in naidisvastused:
    <tr>
      <td>${kysimus.kood}</td>
      <td>${h.fstr(max_pallid)}</td>
      <td>
        ${naidisvastus}
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
% endif
</%def>

<%def name="hindamisfailid()">
<%
  items = [o for o in c.ylesanne.ylesandefailid if o.row_type == const.OBJ_MARKING]
%>
% for item in items:
<div>
  <a href="${h.url_current('downloadfile', id=c.ylesanne.id,
           file_id=item.id, format=item.fileext or 'file')}">${item.filename}</a>
  <span class="mx-2">(${h.filesize(item.filesize)})</span>
</div>
% endfor
</%def>
