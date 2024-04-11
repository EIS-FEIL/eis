<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kiirvalikud")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_('Testide kiirvalikud'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<% 
c.can_update = c.user.has_permission('kiirvalikud', const.BT_UPDATE)
%>
<h1>${_("Kiirvalikud")}</h1>
<table width="100%" >
  <tr>
    <td valign="top" width="250px">
      
      <table width="100%" class="table singleselect" >
        % for rcd in c.items:
          % if c.item and c.item.id == rcd.id:
        <tr class="selected">
          % else:
        <tr>
          % endif
          <td>
            ${h.link_to(rcd.nimi, h.url('admin_kiirvalik', id=rcd.id))}
          </td>
        </tr>
        % endfor
        % if not len(c.items):
        <tr>
          <td>${_("Ühtki kiirvalikut pole loodud")}</td>
        </tr>
        % endif
      </table>

    </td>

    % if c.item:
    <td valign="top">
      ${h.form_save(c.item.id)}

      <table width="100%" class="table" >

        <tr>
          <td class="fh" width="170px">${_("Testiliik")}</td>
          <td>${h.select('f_testiliik_kood', c.item.testiliik_kood, c.opt.testiliik)}</td>
        </tr>

        <tr>
          <td class="fh" width="170px">${_("Kiirvaliku nimetus")}</td>
          <td>${h.text('f_nimi', c.item.nimi, size=50)}</td>
        </tr>

        <tr>
          <td class="fh">${_("Aktiivne")}</td>
          <td>${h.checkbox('f_staatus', 1, checked=c.item.staatus) }</td>
        </tr>

        <tr>
          <td class="fh">${_("Selgitus")}</td>
          <td>
            ${h.textarea('f_selgitus', c.item.selgitus, cols=70, rows=5)}
          </td>
        </tr>

      </table>
      <br/>

      % if c.item.id:
      <table width="100%" class="table table-borderless table-striped" border="0" >
        <caption>${_("Kiirvalikusse kuuluvad testimiskorrad")}</caption>
        <tr>
          <th></th>
          ${h.th(_('Test'))}
          ${h.th(_('Testimiskord'))}
          ${h.th(_('Testsessioon'))}
        </tr>
        % for rcd in c.item.testimiskorrad:
        <tr>
          <td>
            ${h.remove(h.url('admin_delete_kiirvalik', id=c.item.id, sub='kord', testimiskord_id=rcd.id))}
          </td>
          <td>
            ${rcd.test.nimi}
          </td>
          <td>
            ${rcd.tahis}
            % if c.can_update:
            ${h.dlg_edit(h.url('admin_edit_kiirvalik', id=c.item.id, testimiskord_id=rcd.id, partial=True, sub='test'),
            width=500, title=_('Testi testimiskorra muutmine kiirvalikus'))}
            % endif
          </td>
          <td>
            ${rcd.testsessioon and rcd.testsessioon.nimi or ''}
          </td>
        </tr>
        % endfor
      </table>
      % if c.can_update:
      <br/>
      ${h.btn_to_dlg(_('Lisa testimiskord'), h.url('admin_edit_kiirvalik',id=c.item.id, sub='kord', partial=True), width=500,
      title=_('Kiirvalikusse kuuluvad testimiskorrad'), level=2)}
      % endif
    % endif

      ${h.end_form()}      
    </td>
    % endif
  </tr>
  <tr>
    <td colspan="2">
   % if c.can_update:
      ${h.btn_to(_('Lisa'), h.url('admin_new_kiirvalik'))}

      % if c.item:
        % if c.is_edit:
        ${h.submit(out_form=True)}
        % else:
        ${h.btn_to(_('Muuda'), h.url('admin_edit_kiirvalik', id=c.item.id))}
        % endif
      % endif
   % endif
    </td>
  </tr>
</table>


