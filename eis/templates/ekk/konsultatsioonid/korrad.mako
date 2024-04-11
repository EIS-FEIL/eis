<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'korraldus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test:")} ${c.test.nimi or ''} | ${_("Testimiskorrad ja parameetrid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Konsultatsioonid'), h.url('konsultatsioonid'))} 
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Korraldus'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'konsultatsioonid' %>
</%def>

<%
c.can_update = c.user.has_permission('testimiskorrad', const.BT_UPDATE, c.test) and \
  c.test.staatus in (const.T_STAATUS_KOOSTAMISEL,const.T_STAATUS_KINNITATUD)
c.testimiskorrad = list(c.test.testimiskorrad)
%>

% if len(c.testimiskorrad) == 0:
${h.alert_notice(_("Ühtki toimumiskorda ei ole sisestatud"), False)}
% endif

% if c.testimiskorrad:
<div class="row content-wrapper flex-nowrap">
  ${self.aside_testimiskorrad()}
  <section class="col-12 col-md-9 col-lg-10">
    <div class="form-group d-md-hide">
      ${self.dropdown_testimiskorrad()}
      <div>
        % if c.item:
        ${next.body()}
        % endif
      </div>
    </div>
  </section>
</div>
% elif c.item:
      <div class="d-flex justify-content-between align-items-md-center flex-column flex-md-row">
        ${next.body()}
      </div>
% endif
${self.lisamine()}

<%def name="lisamine()">        
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    <% url_new = h.url('konsultatsioon_new_kord', test_id=c.test.id) %>
    <% c.opt_mall = c.opt.opt_konsmall(c.test.testiliik_kood) %>      
        % if c.can_update and c.opt_mall:
        <div style="display:inline-block">
          ${h.button(_("Lisa testimiskord malliga"), id="bnewm", level=2)}
          <div class="malliga" style="display:none">
            ${h.form(url_new, method='get', id="fnewm")}
            <p>
              ${_("Toimumiskorra mall")}
              ${h.select('mall_id', '', c.opt_mall, wide=False, empty=True, class_="nosave")}
            </p>
            ${h.submit_dlg(_("Lisa toimumiskord"))}
            ${h.end_form()}
          </div>
          <script>
            $('#bnewm').click(function(){ open_dialog({'contents_elem': $('.malliga')}); });
          </script>
        </div>
        % endif

        % if c.can_update:
        ${h.btn_to(_("Lisa testimiskord"), url_new, mdicls='mdi-plus', level=2)}
        % endif
  </div>
  <div class="text-right">
    ${self.buttons()}
  </div>
</div>
</%def>        
      
<%def name="aside_testimiskorrad()">
  <aside class="sidebar-menu col-3 col-lg-2 mr-0 d-none d-md-block">
    <nav aria-label="Külgmenüü" class="mb-5 mr-4">
      <ul class="nav level-1">
        % for rcd in c.testimiskorrad:
        <%
          url = h.url('konsultatsioon_edit_kord', test_id=c.test.id, id=rcd.id)
        %>
        <li class="nav-item dropdown show">
          <a href="${url}"
             class="nav-link ${c.item == rcd and 'active' or ''}"
             role="button">
            <span class="text-truncate">${rcd.tahis}</span>
          </a>
        </li>
        % endfor
      </ul>
    </nav>
  </aside>
</%def>

<%def name="dropdown_testimiskorrad()">
      <div class="d-md-none dropdown content-dropdown w-100 mb-7">
        <button class="btn btn-select dropdown-toggle"
                type="button"
                id="dropdownMenuButtonTK"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
          ${c.item and c.item.tahised}
          <i class="mdi mdi-chevron-down"></i>
        </button>
        <div class="dropdown-menu content-dropdown-menu"
             aria-labelledby="dropdownMenuButtonTK">
          % for rcd in c.testimiskorrad:
          <%
            url = h.url('konsultatsioon_edit_kord', test_id=c.test.id, id=rcd.id)
          %>
          <a class="dropdown-item ${c.item == rcd and 'active' or ''}"
             href="${url}">${rcd.tahis}</a>
          % endfor
        </div>
      </div>
</%def>

<%def name="buttons()">
</%def>

