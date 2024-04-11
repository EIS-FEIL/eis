<!DOCTYPE html>
<html lang="${request.locale_name}" translate="no">
<head>
  <meta charset="UTF-8"/>
  ${self.require()}
  % if c.google_gtm:
  <%include file="google_gtm.head.mako"/>
  % endif
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Cache-Control" content="no-cache"/>
  <meta http-equiv="Expires" content="0"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <link rel="shortcut icon" href="/static/favicon.ico"/>
  <%include file="include.mako"/>
  ${self.page_headers()}
  <title>${self.page_title()}</title>
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
% if not c.hide_header_footer:
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
        <div class="collapse navbar-collapse" id="page-menu-7">
          <div class="navbar-top">
            ${self.header_languages()}
            ${self.header_help()}          
            ${self.header_login()}          
          </div>
          <div class="navbar-menu">
            ${self.active_menu()}
            ${self.menu()}
          </div>
        </div>
      </div>
    </nav>
    ${self.textbanner()}
    ${self.emergency()}
  </header>
% else:
  <header>
    ${self.emergency()}
  </header>
% endif
  ${self.page_main()}
% if not c.hide_header_footer:
  ${self.page_footer()}
% endif 
</div>
% if c.user.is_authenticated and request.session.get('chk.email') and not (c.is_devel and c.inst_name != 'dev'):
<div id="chk_email_div" style="display:none">
<%include file="/minu/kontaktuuendamine.mako"/>
</div>
<script>
$(function(){
  open_dialog({dialog_id: 'chkemaildlg',
               contents_html: $('#chk_email_div').html(),
               title: "${_("Kasutaja kontaktandmete uuendamine")}"});
});
</script>
% endif
% if c.no_cookies:
<%include file="cookieconsent.mako"/>
% endif
</body>
</html>

<%def name="page_headers()"></%def>
<%def name="page_title()">${c.inst_title}</%def>
<%def name="require()"></%def>
<%def name="requirenw()"><% c.pagenw = '' %></%def>
<%def name="breadcrumbs()"></%def>
<%def name="textbanner()"></%def>

<%def name="page_main()">
<main class="page-content flex-grow-1">
  ${self.requirenw()}
  <div class="container ${c.pagenw and 'container-nw' or c.pagexl and 'container-lg' or c.pagesm and 'container-sm' or ''}">
    <div class="float-right">
      <div id="${h.page_id(self)}" class="pagehelp">
        ${h.link_to(_("Juhend"), '', mdicls="mdi-information", target="_blank", rel="noopener",
        style="display:none", aria_hidden="true")}
      </div>
    </div>
    % if not c.hide_header_footer and not c.no_breadcrumbs:
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        ${self.breadcrumbs()}
      </ol>
    </nav>
    % endif

    <%include file="/common/message.mako" />
    <div class="page ${c.pagenw and 'container-nw' or ''}" id="${h.page_id(self)}">
      <span id="maincontent"></span>
      ${next.body()}
    </div>
  </div>
</main>
</%def>

<%def name="emergency()">
<%
  modified, sisu = c.user.get_emergency()
  em_url = h.url('emergency_close', modified='', pw_url=True)
%>
<div class="container container-emergency" data-action="${em_url}">
% if modified:
<div class="alert alert-danger alert-dismissable fade show" role="alert">
  <i class="mdi mdi-information-outline"></i>
  ${sisu}
  <button type="button" class="close" data-modified="${modified}" data-dismiss="alert" aria-label="${_("Sule")}"><i class="mdi mdi-close" aria-hidden="true"></i></button>
</div>
% endif
</div>
</%def>

<%def name="header_languages()">
<%
languages = (
   ('et','Eesti'),
   ('en','English'),
   ('es','Español'),
   ('hr','Hrvatski'),
   ('lt','Lietuvių'),
   ('nl','Nederlands'),
   ('ro','Română'),
   ('sl','Slovenščina'),
   ('fi','Suomi'),
   ('el','Ελληνικά'),
   ('ru','Русский'),
   )
curr_locale = request.locale_name
curr_title = 'language'
for locale, title in languages:
   if locale == curr_locale:
       curr_title = title
       break
available_languages = request.registry.settings.get('available_languages').split()
languages = [r for r in languages if r[0] in available_languages]
%>
% if len(languages) > 1:
            <div class="header-languages" aria-label="${_("Vali keel")}">
              <button
                class="btn btn-link dropdown-toggle"
                data-toggle="dropdown"
                id="languagePickerBtn"
                type="button"
                aria-expanded="false"
                title="${_("Vali keel")}">
                <span class="lang-title">${_("Keel")}</span>
                <span class="lang-name">${curr_title}</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-right" role="menu">
                % for locale, title in languages:
                <li role="menuitem" ${locale == curr_locale and 'class="active"' or ''} lang="${locale}"><a href="${h.url('locale', locale=locale)}" class="dropdown-item">
                    ${title} </a></li>
                % endfor
              </ul>
            </div>
% else:
            <div class="header-languages"></div>
% endif
</%def>            

<%def name="header_help()">
<%
  li = []
  if c.app_ekk:
     li.append((_("Kasutusjuhendid"), 'https://projektid.edu.ee/display/EK/EISi+kasutusjuhendid'))
     li.append((_("Ülesannete koostamise juhendid"), 'https://projektid.edu.ee/pages/viewpage.action?pageId=41683199'))
  elif c.app_plank:
     li.append((_("Õppeasutuste videojuhised"), "https://projektid.edu.ee/display/EKAV/Videojuhendid"))
     li.append((_("Kasutusjuhendid"), 'https://projektid.edu.ee/pages/viewpage.action?pageId=41708847'))
  elif c.inst_name == 'clone':
     li.append((_("Kasutusjuhendid"), 'https://projektid.edu.ee/pages/viewpage.action?pageId=51642534'))
  else:
     li.append((_("Kasutusjuhendid"), 'https://projektid.edu.ee/pages/viewpage.action?pageId=41683038'))
%>
            <div class="header-login" aria-label="${_("Abiinfo")}">
              <button
                class="btn btn-link dropdown-toggle"
                data-toggle="dropdown"
                id="helpPickerBtn"
                type="button"
                aria-expanded="false"
                title="${_("Abiinfo")}">
                <span class="text-uppercase">${_("Abi")}</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-right" role="menu">
                % for label, url in li:
                <li role="menuitem">
                  <a href="${url}" target="_blank" rel="noopener" class="dropdown-item">${label}</a>
                </li>
                % endfor
              </ul>
           </div>
</%def>            

<%def name="header_login()">
          % if not c.is_login_page:
            <div class="header-login">
              % if not c.user.is_authenticated:
              <div class="text-center w-100">
                <a href="${h.url('login', action='login')}" class="btn btn-primary">${_("Logi sisse")}</a>
              </div>
              % else:
              ${self.user_dropdown()}
              <div class="text-center d-lg-none w-100">
                ${h.btn_to(_("Välju"), h.url('login', action='signout'), level=2)}
              </div>
              % endif
            </div>
          % endif
</%def>

<%def name="user_dropdown()">              
<div class="user-dropdown">
  <button
    class="btn btn-link dropdown-toggle"
    data-toggle="dropdown"
    type="button"
    aria-expanded="false"
     data-bs-toggle="tooltip" 
    title="${_("Isiklikud andmed ja seaded")}">
    <span>
      % if c.user.cnt_new_msg:
      ${h.mdi_icon('mdi-email', title=_("Sul on lugemata teateid"))}
      % endif
      ${c.user.eesnimi} ${c.user.perenimi}
    </span>
  </button>
  <ul class="dropdown-menu dropdown-menu-right" role="menu">
    % if not c.app_ekk and c.user.auth_type != const.AUTH_TYPE_C and c.user.id and not c.user.testpw_id:
    <li role="menuitem">
      <a href="${h.url('minu_parool')}" class="dropdown-item">${_("Muuda parool")}</a>
    </li>
    % endif
    % if c.user.id and not c.user.testpw_id:
    <li role="menuitem">
      <a href="${h.url('minu_andmed')}" class="dropdown-item">${_("Minu andmed")}</a>
    </li>
    <li role="menuitem">
      <% s_new_msg = c.user.cnt_new_msg and ' (%d)' % c.user.cnt_new_msg  or '' %>
      <a href="${h.url('minu_teated')}" class="dropdown-item">${_("Minu teated") + s_new_msg}</a>
    </li>
    <li role="menuitem">
      <a href="${h.url('seaded')}" class="dropdown-item">${_("Seaded")}</a>
    </li>
    % if c.app_eis and c.user.has_permission('nousolekud', const.BT_SHOW):
    <li role="menuitem">
      <a href="${h.url('nousolekud_isikuandmed')}" class="dropdown-item">${_("Testide läbiviimise nõusolekud")}</a>
    </li>
    % endif
    % endif
    <li role="menuitem" class="d-none d-lg-block">
      <a href="${h.url('login', action='signout')}" class="dropdown-item">${_("Välju")}</a>
    </li>
  </ul>
</div>
<p class="my-0 ml-auto user-details">
  % if not c.app_ekk:                    
  <small>
    ${self.kool_dropdown()}
  </small>
  % endif
</p>
</%def>              

<%def name="kool_dropdown()">              
<%
  kohad = c.user.opt_kohad()
  has_ekk = c.user.has_ekk()
%>
% if not kohad and not c.user.on_adminkoht and not has_ekk:
<span style="font-size:1rem">${_("Avalik vaade")}</span>
% elif c.app_plank and len(kohad) == 1 and not c.user.on_adminkoht:
<span style="font-size:1rem;font-weight:500">${c.user.koht_nimi}</span>
% else:
<div class="user-dropdown">
  <button
    class="btn btn-link dropdown-toggle"
    data-toggle="dropdown"
    type="button"
    aria-expanded="false"
    title="${_("Vali esindatav kool")}">
    <span style="font-weight:500">
    % if c.app_eis:
      % if c.user.uiroll == const.UIROLL_S:
         ${_("Avalik vaade")}
      % else:
        %  if c.user.on_kohteelvaade:
         ${_("Administraatori eelvaade")}
        % elif c.user.on_avalikadmin:
         ${_("Administraator")}
        % else:
         ${_("Õpetaja")}
        % endif
        <span class="divider">|</span>                      
        ${c.user.koht_nimi}
      % endif
    % else:
      ${c.user.koht_nimi}    
    % endif
    </span>
  </button>
  <ul class="dropdown-menu dropdown-menu-right" role="menu">
    % if c.app_eis:
    <li role="menuitem">
      <a href="${h.url('login_role', role=const.UIROLL_S)}" class="dropdown-item">${_("Avalik vaade")}</a>
    </li>
    % endif    
    % for koht_id, koht_nimi in kohad:
    <li role="menuitem">
      <a href="${h.url('login_role', role=f'{const.UIROLL_K}.{koht_id}')}" class="dropdown-item">${koht_nimi}</a>
    </li>
    % endfor
    % if c.user.on_adminkoht:
    <li role="menuitem">
      <a href="${h.url('login_role', role=const.UIROLL_K)}" class="dropdown-item">${_("Mõni muu kool...")}</a>
    </li>
    % endif
    % if has_ekk:
    <li role="menuitem">
      <a href="/ekk" class="dropdown-item">${_("Siseveeb")}</a>
    </li>
    % endif
  </ul>
</div>
% endif
</%def>              

<%def name="active_menu()">
<% c.menu1 = '' %>
</%def>

<%def name="menu()">
<%
  c.user.get_menu()
  items = c.user.menu_left.subitems
%>
% if items:
           <ul class="nav navbar-nav">
             % for cnt, item in enumerate(items):
             <%
               subitems = item.subitems
               activecls = item.url == c.menu1 and 'active' or ''
             %>
             % if subitems:
              <li class="nav-item dropdown keep-open-sm">
                <a class="dropdown-toggle nav-link ${activecls}" data-toggle="dropdown" href="#">${item.title}</a>
                <ul class="dropdown-menu">
                  % for subitem in subitems:
                  <li><a href="${subitem.get_url()}" class="dropdown-item">${subitem.title}</a></li>
                  % endfor
                </ul>
              </li>
            % else:
             <li class="nav-item">
                <a class="nav-link ${activecls}" href="${item.get_url()}">${item.title}</a>
              </li>
            % endif
            % endfor
          </ul>
% endif
</%def>

<%def name="page_footer()">
  <footer class="page-footer">
    <div class="container">
      <div class="row">
        <div class="col-md-6 mb-md-4">
          % if c.inst_name == 'clone' or c.app_plank:
          <p><strong>${_("Kasutajatugi")}</strong></p>
          % else:
          <p><strong>${_("EISi kasutajatugi")}</strong></p>
          % endif
          <address>
                <% support_addr = request.registry.settings.get('smtp.tugi') %>
                % if support_addr:
                <p>${_("E-post")}: <a href="mailto:${support_addr}">${support_addr}</a></p>
                % endif
                <p>${_("Tel 7302 135 (E-R 9-17)")}</p>
          </address>
          % if c.app_eis:
          <p><strong>${_("E-eksamite sisulised küsimused")}: <a href="mailto:e-eksamid@harno.ee">e-eksamid@harno.ee</a></strong></p>
          % endif
        </div>
        <div class="col-md-6 mb-4">
          ${self.page_footer_links()}
          ${h.help_for(h.page_id(self), model)}
        </div>
        <div class="col-lg-6 mb-md-4">
          <div id="responsivevoice_licence">
            ## sisu lisab ylesanne.js vajaduse korral
          </div>
        </div>
      </div>
    </div>
  </footer>
</%def>

<%def name="page_footer_links()">
          <p><b>${_("Lingid")}</b></p>  
              <div>
              % if c.app_eis or c.app_plank:
                <div>
                ${h.link_to(_("Isikuandmete töötlemine"), h.url('kasutustingimused'), class_="pl-0")}
                </div>
                % if c.user.is_authenticated and c.inst_name != 'clone':
                <div>
                  ${h.link_to_dlg(_("Küsimused ja ettepanekud"), h.url('new_ettepanek'), title=_("Küsimused ja ettepanekud"), width=700, class_="pl-0")}
                </div>
                % endif
             % endif
                % if not c.no_cookies:
                <div>
                  ${h.link_to_dlg(_("Küpsiste nõusolek"), h.url('showcookieconsent'), class_="pl-0", title=_("Küpsiste sätted"), dialog_id='cconsentdlg')}
                </div>
                % endif
                % if c.app_ekk:
                <div>
                  ${h.link_to(_("Avalik vaade"), '/eis', target='_blank', class_="pl-0")}                  
                </div>
                % endif

             % if c.app_eis:
                <div>
                  <div class="pl-0 btn btn-link" id="korvaklappidekontroll">
                    <div class="mdi mdi-24px mdi-play-circle-outline" style="text-align: center;position:relative;"></div>
                    <span class="pl-1">${_("Kõrvaklappide kontroll")}</span>
                  </div>
                  <script>
                  </script>
                </div>
             % endif
              </div>
</%def>

<%def name="open_dialog(name, template, title, size='md')">
<div id="div_dialog_${name}">
  <%include file="${template}"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_${name}'), 'title':'${title}', 'size': '${size}'});
  });
</script>
</%def>
