<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.kasutaja.nimi, h.url('admin_kasutaja', id=c.kasutaja.id))}
${h.crumb(_("Nõusolekud"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="kasutaja.tabs.mako"/>
</%def>

<h3>${_("Piirkonnad, kus isik saab vaatlejana või hindajana osaleda")}</h3>
<div class="form-wrapper-lineborder d-flex flex-wrap mb-2">
  % if c.user.has_permission('kasutajad', const.BT_UPDATE):
  <div class="mr-5">
    ${h.btn_to_dlg(_("Muuda"), h.url('admin_kasutaja_new_nousolek',
    kasutaja_id=c.kasutaja.id, sub='prk', partial=True), title=_("Piirkondade valimine"), width=500, mdicls='mdi-file-edit')}
  </div>
  % endif
  <div>
    ${h.literal(', '.join(rcd.piirkond.nimi for rcd in c.kasutaja.kasutajapiirkonnad))}
  </div>
</div>

<h3>${_("Nõusolekud")}</h3>
<div class="form-wrapper-lineborder mb-2">
  % if c.opt_testsessioon:
  <div class="d-flex flex-wrap">
    ${h.flb(_("Testsessioon"), 'testsessioon_id', 'mr-5')}
    <div>
        ${h.form(h.url('admin_kasutaja_nousolekud', kasutaja_id=c.kasutaja.id), method='get')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        c.opt_testsessioon, empty=True, wide=False,
        onchange="$(this).parents('form').submit()")}
        ${h.end_form()}
    </div>
  </div>
  % endif
  <div>
    ${h.form_save(None)}
    ${h.hidden('testsessioon_id', c.testsessioon_id)}
    <%include file="kasutaja.nousolekud_list.mako"/>

    <div class="d-flex flex-wrap">
        % if c.user.has_permission('kasutajad', const.BT_UPDATE):
        ${h.btn_to_dlg(_("Lisa"), h.url('admin_kasutaja_new_nousolek',
        kasutaja_id=c.kasutaja.id, testsessioon_id=c.testsessioon_id, partial=True), title=_("Testi valimine"), size='lg', mdicls='mdi-plus', level=2)}        

        <div class="flex-grow-1 text-right">
          ${h.submit()}
        </div>
        % endif
    </div>
    ${h.end_form()}
  </div>
</div>
