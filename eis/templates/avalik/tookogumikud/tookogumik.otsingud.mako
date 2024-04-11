## -*- coding: utf-8 -*- 

<div class="d-flex justify-content-end m-1">
${h.btn_to(_("Uus ülesanne..."), h.url('new_ylesanne'), level=2)}
</div>
<%
  cur_tab = c.current_search_tab or 'tab_yk'
%>

<ul class="nav nav-tabs d-none d-md-flex" role="tablist">
  <% active = cur_tab == 'tab_yk' %>
  <li class="nav-item" role="tab" aria-selected="${active and 'true' or 'false'}">
    <a class="nav-link ${active and 'active' or ''}" href="#search_yk" id="tab_yk"
       data-toggle="tab">${_("E-kogud")}</a>
  </li>
  <% active = cur_tab == 'tab_t' %>
  <li class="nav-item" role="tab" aria-selected="${active and 'true' or 'false'}">
    <a class="nav-link ${active and 'active' or ''}" href="#search_t" id="tab_t"
            data-toggle="tab">${_("Testid")}</a>
  </li>
  <% active = cur_tab == 'tab_yl' %>
  <li class="nav-item" role="tab" aria-selected="${active and 'true' or 'false'}">
    <a class="nav-link ${active and 'active' or ''}" href="#search_yl" id="tab_yl"
            data-toggle="tab">${_("Detailotsing")}</a>
  </li>
</ul>
<div class="tab-content responsive-content">
  <% active = cur_tab == 'tab_yk' %>
  <div id="search_yk" class="tab-pane card responsive-card fade show ${active and 'active' or ''}"
       role="tabpanel" aria-labelledby="tab_yk">
    <%include file="tookogumik.ylesandekogud.mako"/>
  </div>
  <% active = cur_tab == 'tab_t' %>
  <div id="search_t" class="tab-pane card responsive-card fade show ${active and 'active' or ''}"
       role="tabpanel" aria-labelledby="tab_t">       
    <%include file="tookogumik.testiotsing.mako"/>
  </div>
  <% active = cur_tab == 'tab_yl' %>
  <div id="search_yl" class="tab-pane card responsive-card fade show ${active and 'active' or ''}"
       role="tabpanel" aria-labelledby="tab_yl">    
    <%include file="tookogumik.ylesandeotsing.mako"/>
  </div>
</div>
