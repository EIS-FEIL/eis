## Ühe lipiku joonistamine
<%def name="draw(name, url, title, current_tab=None, h1=False, onclick=None, disabled=False)">
<%
 if current_tab is None or current_tab == '':
     is_current_tab = c.controller == name
 else:
     is_current_tab = current_tab is True or current_tab == name
 if disabled == 'notcurrent' and is_current_tab:
     disabled = False 
%>
% if c.tabs_mode == 'accordion1':
  ## enne sisu kuni jooksva sakini
   % if not c.tabs_current1:
      <%
          if is_current_tab:
              c.tabs_current1 = True
      %>
     ${self.draw_sm(name, url, title, is_current_tab, h1, onclick, disabled)}
   % endif
% elif c.tabs_mode == 'accordion2':   
  ## peale jooksvat sakki
   % if not c.tabs_current2:
      <%
          if is_current_tab:
              c.tabs_current2 = True
      %>
   % else:
     ${self.draw_sm(name, url, title, is_current_tab, h1, onclick, disabled)}      
   % endif
% else:
     ## sakid laial ekraanil
     ${self.draw_md(name, url, title, is_current_tab, h1, onclick, disabled)}
% endif
</%def>

<%def name="draw_sm(name, url, title, is_current_tab, h1=False, onclick=None, disabled=False)">
     <div id="a-tab-${name}" class="card" role="tabpanel">
       <div class="accordion-card card parent-accordion-card">
         <div class="card-header" role="tab" id="a-heading-${name}">
           <div class="accordion-title">
             <button class="btn btn-link ${not is_current_tab and 'collapsed get' or ''} ${disabled and 'disabled' or ''}"
                     type="button" ${disabled and 'aria-disabled="true"' or ''}
                     % if not is_current_tab and not disabled:
                     href="${url}"
                     % endif
                     % if is_current_tab:
                     data-toggle="collapse"
                     data-target="#main_tab_content"
                     % endif
                     aria-expanded="${is_current_tab and 'true' or 'false'}"
                     aria-controls="a-heading-${name}">
               <span class="btn-label"><i class="mdi mdi-chevron-down"></i> ${title}
               </span>
             </button>
           </div>
         </div>
       </div>
     </div>
</%def>

<%def name="draw_md(name, url, title, is_current_tab, h1=False, onclick=None, disabled=False)">
## sakid laial ekraanil
<% vcls = c.tabs_mode == 'li' and 'd-none d-md-flex' or '' %>
<li class="nav-item ${vcls}" role="tab" aria-selected="${is_current_tab and 'true' or 'false'}" ${disabled and 'aria-disabled="true"' or ''}>
  <a class="nav-link ${is_current_tab and 'active' or ''} ${disabled and 'disabled' or ''}"
     ${url and 'href="%s"' % url or 'role="banner"'}
     ${url and url.startswith('#') and 'data-toggle="tab"' or ''}
     ${onclick and 'onclick="%s"' % onclick or ''} id="tab-${name}">
    % if h1:
    <b>${title}</b>
    % else:
    ${title}
    % endif
  </a>
</li>
</%def>

<%def name="subdraw(name, url, title, current_tab=None, onclick=None, disabled=False)">
<% c.tabs_mode = 'subli' %>
${self.draw(name,url,title,current_tab, onclick=onclick, disabled=disabled)}
</%def>
