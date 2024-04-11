% if c.user.on_pedagoog:
<%
  tabs = (('search_yk', _('Ülesanded')),
          ('search_yl', _('Detailotsing')),
          ('search_tk', _('Töökogumik')),
         )
  if not c.active_href:
     c.active_href = 'search_yk'
%>
<ul class="nav nav-tabs" role="tablist">
  % for href, title in tabs:
  <% active_cls = href == c.active_href and 'active' or '' %>
  <li class="nav-item ${active_cls}">
    <a class="nav-link ${active_cls}" data-toggle="tab" href="#${href}">${title}</a>
  </li>
  % endfor
</ul>
<div class="tab-content">
  <div id="search_yk" class="tab-pane fade ${c.active_href=='search_yk' and 'show active' or ''}">
    ${c.body_yk}
  </div>
  <div id="search_yl" class="tab-pane fade ${c.active_href=='search_yl' and 'show active' or ''}">
    ${c.body_yl}
  </div>
  <div id="search_tk" class="tab-pane fade ${c.active_href=='search_tk' and 'show active' or ''}">
    ${c.body_tk}
  </div>
</div>
% else:
    ${c.body_yl}
% endif
