<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'nimekirjad' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Nimekiri")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Nimekiri'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<% 
  c.can_update = True
  if not c.item and c.testiruum:
      c.item = c.testiruum.nimekiri
%>

<div class="gray-legend mb-2 p-3 border-base-radius">
  % if c.user.koht_id:
  <div class="row">
    ${h.flb(_("Õppeasutus"),None, 'col-md-2 text-md-right')}
    <div class="col">
      ${c.user.koht_nimi}
    </div>
  </div>
  % endif
  <div class="row">
    ${h.flb(c.test.on_jagatudtoo and _('Töö') or _('Test'), None, 'col-md-2 text-md-right')}
    <div class="col">
      % if c.user.has_permission('testid', const.BT_SHOW, c.test):
      ${h.link_to(c.test.nimi, h.url('test', id=c.test.id), class_="p-0 m-0")}
      % else:
      ${c.test.nimi}
      % endif
    </div>
  </div>
</div>

% if len(c.items) > 1 or len(c.items) == 1 and c.item not in c.items:
<div class="row content-wrapper flex-nowrap">
  ${self.aside_nimekirjad()}
  <section class="col-12 col-md-9">
    <div class="form-group d-md-hide">
      ${self.dropdown_nimekirjad()}
      <div class="flex-column flex-md-row">
        <%include file="nimekiri.mako"/>
      </div>
    </div>
  </section>
</div>
% else:
<%include file="nimekiri.mako"/>
  ${self.kuvapeidus()}
% endif

<%def name="aside_nimekirjad()">
  <aside class="sidebar-menu col-3 mr-0 d-none d-md-block">
    <nav aria-label="Külgmenüü" class="mb-5 mr-4">
      <ul class="nav level-1">
      % for item in c.items:
      <% url = h.url_current('show', id=item.id, testiruum_id=0, hidden=request.params.get('hidden')) %>
        <li class="nav-item dropdown show">
          <a href="${url}"
             class="nav-link ${c.item == item and 'active' or ''}"
             role="button">
            <span class="text-truncate pl-2">
              % if item.staatus == const.B_STAATUS_KEHTETU:
              <i class="mdi mdi-file-hidden mdi-18px mr-1"></i>
              % endif
              ${item.nimi}
            </span>
          </a>
        </li>
        % endfor
      </ul>
    </nav>
    ${self.kuvapeidus()}    
  </aside>
</%def>

<%def name="dropdown_nimekirjad()">
      <div class="d-md-none dropdown content-dropdown w-100 mb-7">
        <button class="btn btn-select dropdown-toggle"
                type="button"
                id="dropdownMenuButtonTK"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
          ${c.item and c.item.nimi}
          <i class="mdi mdi-chevron-down"></i>
        </button>
        <div class="dropdown-menu content-dropdown-menu"
             aria-labelledby="dropdownMenuButtonTK">
          % for item in c.items:
          <% url = h.url_current('show', id=item.id, testiruum_id=0, hidden=request.params.get('hidden')) %>
          <a class="dropdown-item ${c.item == item and 'active' or ''}"
             href="${url}">
              % if item.staatus == const.B_STAATUS_KEHTETU:
              <i class="mdi mdi-file-hidden mdi-18px mr-3"></i>
              % endif
              ${item.nimi}
          </a>
          % endfor
        </div>
      </div>
</%def>

<%def name="kuvapeidus()">
% if not c.hidden and c.on_peidus:
<%
  if c.item:
      url = h.url_current('show', id=c.item.id, hidden=1)
  else:
      url = h.url_current('index', hidden=1)
%>
<p>${h.link_to(_("Kuva peidus nimekirjad"), url, mdicls='mdi-file-hidden', level=2)}</p>
% elif c.hidden and c.item.staatus:
<%
  if c.item:
      url = h.url_current('show', id=c.item.id)
  else:
      url = h.url_current('index')
%>
<p>${h.link_to(_("Peida peidus nimekirjad"), url, mdicls='mdi-file-hidden', level=2)}</p>
% endif
</%def>
