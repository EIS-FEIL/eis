<!DOCTYPE html>
<html lang="${request.locale_name}" translate="no">
<head>
  <meta charset="UTF-8"/>
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Cache-Control" content="no-cache"/>
  <meta http-equiv="Expires" content="0"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <link rel="shortcut icon" href="/static/favicon.ico"/>
  <%include file="include.mako"/>
  <title>${_("Tõrge")}</title>
  % if c.analytics:
  <%include file="analytics.mako"/>
  % endif
<!-- ${self.name} -->
</head>
<%
  app_cls = 'app-%s' % c.app_name
  inst_name = c.my_inst_name or c.inst_name
  if inst_name in ('clone', 'test', 'prelive'):
      wrap_cls = inst_cls = 'env-%s' % inst_name
  else: # live
      inst_cls = 'env-%s' % inst_name
      wrap_cls = inst_cls + ' env-eis'
%>
<body class="${inst_cls} ${app_cls}">
<div class="page-wrapper ${inst_cls} ${wrap_cls} d-flex flex-column">
% if c.google_gtm:
<%include file="google_gtm.body.mako"/>  
% endif
  <header class="page-header page-header-orange page-header-minimized">
    <nav class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <a class="sr-only sr-only-focusable position-absolute p-2" id="lnk_maincontent" href="#maincontent">
          ${_("Liigu põhisisu juurde")}
        </a>
        <a class="navbar-brand" href="${h.url('avaleht')}" title="${_("Avalehele")}">
          % if inst_name == 'clone':
          <img src="/static/images/eis-logo-clone.svg" alt="logo" width="237" height="54"/></a>
          % else:
          <img src="/static/images/eis-logo.svg" alt="logo" width="237" height="54"/></a>
          % endif
        <div class="mobile-header d-lg-none">
          <button
            class="navbar-toggler"
            data-toggle="collapse"
            data-target="#page-menu-7"
            aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span
              class="navbar-toggler-icon mdi mdi-menu"
              aria-hidden="true"
            ></span>
          </button>
        </div>
      </div>
    </nav>
  </header>
  ${self.page_main()}
  ${self.page_footer()}
</div>
</body>
</html>


<%def name="page_main()">
<main class="page-content flex-grow-1">
  <div class="container ${c.pagenw and 'container-nw' or c.pagexl and 'container-lg' or ''}">
    <div class="page ${c.pagenw and 'container-nw' or ''}" id="${h.page_id(self)}">
      <span id="maincontent"></span>
      ${_("Tõrge!")}
    </div>
  </div>
</main>
</%def>

<%def name="page_footer()">
  <footer class="page-footer">
    <div class="container">
      <div class="row">
        <div class="col-md-6 mb-md-4">
          % if c.inst_name == 'clone' or c.app_plank:
          <p><b>${_("Kasutajatugi")}</b></p>
          % else:
          <p><b>${_("EISi kasutajatugi")}</b></p>
          % endif
          <address>
                <% support_addr = request.registry.settings.get('smtp.tugi') %>
                % if support_addr:
                <p>${_("E-post")}: <a href="mailto:${support_addr}">${support_addr}</a></p>
                % endif
                <p>${_("Tel 7302 135 (E-R 9-17)")}</p>
          </address>
        </div>
      </div>
    </div>
  </footer>
</%def>

