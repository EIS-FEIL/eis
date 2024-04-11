<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${c.item and c.item.nimi or _("Õpilaste rühmad")} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Minu töölaud"), h.url('tookogumikud'))}
${h.crumb(_("Õpilaste rühmad"), h.url('opperyhmad'))}
% if c.item:
${h.crumb(c.item.nimi or _("Uus rühm"))}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<div class="row content-wrapper flex-nowrap">
  ${self.aside_ryhmad()}
  <section class="col-12 col-md-9">
    <div class="form-group d-md-hide">
      ${self.dropdown_ryhmad()}
      <div class="flex-column flex-md-row">
        % if c.item:
        <%include file="opperyhm.mako"/>
        % endif
      </div>
    </div>
  </section>
</div>

<%def name="aside_ryhmad()">
  <aside class="sidebar-menu col-3 mr-0 d-none d-md-block">
    ${h.btn_to_dlg(_('Lisa uus rühm'), h.url_current('new'), dlgtitle=_('Rühma lisamine'), mdicls="mdi-plus")}

    <nav aria-label="Külgmenüü" class="mb-5 mr-4 mt-4">
      <ul class="nav level-1">
      % for item in c.items:
      <% url = h.url('edit_opperyhm', id=item.id) %>
        <li class="nav-item dropdown show">
          <a href="${url}"
             class="nav-link ${c.item == item and 'active' or ''}"
             role="button">
            <span class="text-truncate pl-2">
              ${item.nimi}
            </span>
          </a>
        </li>
        % endfor
      </ul>
    </nav>
  </aside>
</%def>

<%def name="dropdown_ryhmad()">
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
          <% url = h.url('edit_opperyhm', id=item.id) %>          
          <a class="dropdown-item ${c.item == item and 'active' or ''}"
             href="${url}">
              ${item.nimi}
          </a>
          % endfor
        </div>
      </div>
</%def>
