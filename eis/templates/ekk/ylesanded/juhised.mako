<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<% c.includes['ckeditor'] = True %>
</%def>
<%def name="page_title()">
${c.item.nimi} | ${_("Juhised")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.item.nimi or c.item.id, h.url('ylesanne', id=c.item.id))}
${h.crumb(_("Juhised"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>
% if c.item.lukus:
${h.alert_warning(c.item.lukus_nimi, False)}
% endif

${h.form_save(c.item.id, multipart=True)}

<table class="table table-striped tablesorter">
  <caption>${_("Hindamisaspektid")}</caption>
  <col width="50"/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col width="30"/>
  <col width="30"/>
  <thead>
    <tr>
      <th>${_("Jrk")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Aspekti kood")}</th>
      <th>${_("Aspekt")}</th>
      <th>${_("Max toorpunktid")}</th>
      <th>${_("Kaal")}</th>
      <th>${_("Hindamisjuhend")}</th>
      <th colspan="2" sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % if len(c.item.hindamisaspektid) == 0:
    <tr>
      <td colspan="9">${_("Ühtegi hindamisaspekti pole lisatud")}</td>
    </tr>
    % endif

% for n, rcd in enumerate(c.item.hindamisaspektid):
    <tr>
      <td>${rcd.seq}</td>
      <td>${rcd.aine_nimi}</td>
      <td>${rcd.aspekt_kood}</td>
      <td>
        % if rcd.aspekt:
        ${rcd.aspekt_nimi}
        % else:
        <span class="error">
        ${_("Aspekt {s} on klassifikaatorist eemaldatud").format(s=rcd.aspekt_kood)}
        </span>
        % endif
      </td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>${h.fstr(rcd.kaal)}</td>
      <td>
        <%
          pkirjeldused = list(rcd.punktikirjeldused)
        %>
        % if len(pkirjeldused):
        <table width="100%"  class="table table-borderless table-striped tablesorter">
          <col width="40"/>
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
            <td>
              ${h.fstr(r.punktid)}p
            </td>
            <td>${r.kirjeldus and r.kirjeldus.replace('\n','<br/>')}</td>
          </tr>
          % endfor
          </tbody>
        </table>
        % endif

        ${rcd.hindamisjuhis or rcd.aspekt and rcd.aspekt.ctran.kirjeldus or ''}
      </td>
      % if c.user.has_permission('ylesanded', const.BT_UPDATE,c.item):
      <td>
        ${h.dlg_edit(h.url('ylesanded_edit_juhised', id=c.item.id, aspekt_id=rcd.id, 
        partial=True, sub='aspekt'),
        dlgtitle=_("Hindamisaspekti seadistamine"),
        title=_("Muuda"), size='lg')}
      </td>
      <td>
        % if not c.ylesanne.lukus:
        ${h.remove(h.url('ylesanded_delete_juhised', id=c.item.id,
        aspekt_id=rcd.id, sub='aspekt'))}
        % endif
      </td>
      % endif
    </tr>
% endfor    
  </tbody>
</table>
% if c.user.has_permission('ylesanded', const.BT_UPDATE,c.item) and not c.ylesanne.lukus:
${h.btn_to_dlg(_("Lisa"),
  h.url('ylesanded_edit_juhised', id=c.item.id, sub='aspekt', partial=True), level=2, size='lg',
  title=_("Hindamisaspektid"), width=800)}
% endif
<br/>

% if c.item.is_encrypted:
${h.alert_notice(_("Ülesande sisu on krüptitud"))}
% else:
<div class="d-flex flex-wrap">
  <div class="flex-grow-1 m-1">
      ${self.edit_files('a', _("Ülesande failid"), const.OBJ_ASSESSMENT)}
  </div>
  <div class="flex-grow-1 m-1">
      ${self.edit_files('s', _("Lahenduse failid"), const.OBJ_SOLUTION)}
  </div>
  <div class="flex-grow-1 m-1">
      ${self.edit_files('o', _("Lähtematerjalid"), const.OBJ_ORIGIN)}
  </div>
  <div class="flex-grow-1 m-1">
      ${self.edit_files('h', _("Hindamise failid"), const.OBJ_MARKING)}
  </div>
</div>
% endif

<div class="text-right">
% if c.user.has_permission('ylesanded-failid', const.BT_UPDATE,c.item):
${h.submit()}
% endif
</div>
${h.end_form()}


<%def name="edit_files(prefix, caption, tyyp)">

##  <div style="float:left">
      <table class="table table-borderless table-striped"  width="100%" style="margin-bottom:8px">
        <caption>${caption}</caption>
        <col width="30%"/>
        <col width="30%"/>
        <col width="30px"/>
        <col width="30%"/>
        <tbody>
          % if c.user.has_permission('ylesanded-failid',const.BT_UPDATE, c.item):
          <tr>
            <td nowrap colspan="4">
              ${_("Lisa")}
              ${h.file('%s-0.filedata' % prefix, value=_("Fail"))}
              ${h.hidden('%s-0.id' % prefix, '')}
            </td>
          </tr>
          % endif

          <% subitems = [o for o in c.item.ylesandefailid if o.row_type == tyyp] %>

          % if len(subitems) == 0:
          <tr>
            <td colspan="4">${_("Ühtegi faili pole lisatud")}</td>
          </tr>
          % endif

          % for cnt, subitem in enumerate(subitems):
          <tr>
            <td>
              <a href="${h.url('ylesanded_fail', id=c.item.id,
              ylesandefail_id=subitem.id, format=subitem.fileext or 'file')}">${subitem.filename}</a>
              <span class="mx-2">(${h.filesize(subitem.filesize)})</span>
            </td>
            <td>
              % if subitem.is_image:
                ${h.image(h.url('ylesanded_fail', id=c.item.id, ylesandefail_id=subitem.id, format=subitem.fileext or 'file'), 
                 _("Pilt"), width=subitem.laius or 50)}
              % endif
            </td>
            <td>
          % if c.user.has_permission('ylesanded-failid', const.BT_UPDATE,c.item):
          ${h.remove(h.url('ylesanded_delete_juhised', id=c.item.id, fail_id=subitem.id, sub='fail'))}
          % endif
            ${h.hidden('%s-%s.id' % (prefix, cnt+1), subitem.id)}
          </td>
            <td>
      % if len(subitem.ylesandefailimarkused):
      ${h.btn_to_dlg(_("Märked") + ' (%s)' % len(subitem.ylesandefailimarkused), 
      h.url('ylesanded_juhised', id=c.item.id, fail_id=subitem.id, sub='markus', partial=True), level=2,
      title=_("Märked"), width=600)}
      % elif c.can_update or c.user.has_permission('ylesanded-failid', const.BT_UPDATE,obj=c.item):

      ${h.btn_to_dlg(_("Lisa märge"), 
           h.url('ylesanded_edit_juhised', id=c.item.id, fail_id=subitem.id, sub='markus', partial=True), level=2,
      title=_("Märkus"), width=600)}
      % endif
        </tr>
  % endfor
        </tbody>
      </table>
##  </div>
</%def>

