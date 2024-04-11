<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.ylesandekogu = c.item %>
<%include file="tabs.mako"/>
</%def>
<%def name="page_title()">
${c.item.nimi or _("E-kogu")} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("E-kogud"), h.url('ylesandekogud'))}
${h.crumb(c.item.nimi or _("E-kogu"), h.url('ylesandekogu', id=c.item.id))}
${h.crumb(_("Testid ja ülesanded"), h.url('ylesandekogu_kogusisu', kogu_id=c.item.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">  
        ${h.flb(_("Ajavahemik"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">  
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
  </div>
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
      ${h.submit(_("Testid (CSV)"), id='csvt', level=2)}
      ${h.submit(_("Testide kasutajad (CSV)"), id='csvtk', level=2)}
      ${h.submit(_("Ülesanded (CSV)"), id='csvy', level=2)}
      ${h.submit(_("Ülesannete kasutajad (CSV)"), id='csvyk', level=2)}            
    </div>
    ${h.btn_search()}
  </div>
</div>
${h.end_form()}

% if c.t_items:
<table class="table table-borderless table-striped tablesorter">
  <caption>${_("Testid")}</caption>
  <thead>
    <tr>
      % for value in c.t_header:
      ${h.th(value)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in c.t_items:
    <tr>
      <% test_id = item[0] %>
      % for ind, value in enumerate(item):
      <td>
        % if ind == 1:
        ${h.link_to(value, h.url('test', id=test_id))}
        % elif isinstance(value, list):
          % for (cnt, lang) in value:
          <%
            bubble_id = 'opetaja_t_%d_%s' % (test_id, lang)
            url = h.url_current('index', sub='opetaja', kogu_id=c.item.id, test_id=test_id, lang=lang,
                                alates=h.str_from_date(c.alates), kuni=h.str_from_date(c.kuni))
          %>
          % if cnt:
          <div>${h.link_to_bubble(cnt, url, bubble_id=bubble_id)}</div>
          % endif
          % endfor
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      % for ind, value in enumerate(c.t_footer):
      % if ind == 0:
      <td colspan="3" class="frh">${value}</td>
      % else:
      <td>${value}</td>
      % endif
      % endfor
    </tr>
  </tfoot>
</table>
% else:
${h.alert_notice(_("E-kogu ei sisalda ühtki testi"), False)}
% endif

% if c.y_items:
<table class="table table-borderless table-striped tablesorter">
  <caption>${_("Ülesanded")}</caption>
  <thead>
    <tr>
      % for value in c.y_header:
      ${h.th(value)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in c.y_items:
    <tr>
      <% y_id = item[0] %>
      % for ind, value in enumerate(item):
      <td>
        % if ind == 1:
        ${h.link_to(value, h.url('ylesanne', id=y_id))}
        % elif isinstance(value, list):
          % for (cnt, lang) in value:
          <%
            bubble_id = 'opetaja_y_%d_%s' % (y_id,lang)
            url = h.url_current('index', sub='opetaja', kogu_id=c.item.id, ylesanne_id=y_id, lang=lang,
                                alates=h.str_from_date(c.alates), kuni=h.str_from_date(c.kuni))
          %>
          % if cnt:
          <div>${h.link_to_bubble(cnt, url, bubble_id=bubble_id)}</div>
          % endif
          % endfor
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      % for ind, value in enumerate(c.y_footer):
      % if ind == 0:
      <td colspan="2" class="frh">${value}</td>
      % else:
      <td>${value}</td>
      % endif
      % endfor
    </tr>
  </tfoot>
</table>
% else:
${h.alert_notice(_("E-kogu ei sisalda ühtki ülesannet"), False)}
% endif
