<%
  all_data = [(_("Üldised funktsioonid"), c.data1),
              (_("Õpipädevustestide funktsioonid"), c.data2),
              (_("Loodusvaldkonna funktsioonid"), c.data3),
             ]
%>
<ul class="nav nav-pills" role="tablist">
  % for ind, (title, data) in enumerate(all_data):
  % if data:
  <% is_active = ind == 0 %>
  <li class="nav-item" role="tab" aria-controls="tab${ind}"
      aria-selected="${is_active and 'true' or 'false'}">
    <a class="nav-item nav-link ${is_active and 'active' or ''}"
      id="a_tab${ind}" data-toggle="tab" href="#tab${ind}">${title}</a>
  </li>
  % endif
  % endfor
</ul>
<div class="tab-content" id="ttabs">
  % for ind, (title, data) in enumerate(all_data):
  % if data:
  <% is_active = ind == 0 %>  
  <div class="tab-pane rounded-0 border-0 fade ${is_active and 'show active' or ''}"
    id="tab${ind}"
    role="tabpanel"
    aria-labelledby="a_tab${ind}">
    ${self.vartbl(data)}
  </div>
  % endif
  % endfor
</div>

<%def name="vartbl(opt_cmds)">
<table class="table">
  <thead>
    <tr>
      <th>${_("Muutuja või funktsioon")}</th>
      <th>${_("Selgitus")}</th>
      <th>${_("Andmetüüp")}</th>
      <th>${_("Funktsiooni parameetrid")}</th>
    </tr>
  </thead>
  <tbody>
    % for cmd in opt_cmds or []:
    <%
      buf = cmd[0]
      args = None
      if len(cmd) == 4:
         args = cmd[3]
         li = [r[0] for r in args]
         buf += '(' + ', '.join(li) + ')'
      buf = '${%s}' % buf
    %>
    <tr>
      <td>
        <a class="fb-cmd btn btn-link" style="text-decoration:underline">
          ${cmd[0]}
          <span style="display:none" class="fb-buf">${buf}</span>
        </a>
      </td>
      <td>
        ${cmd[2]}
      </td>
      <td>${cmd[1]}</td>
      % if args is not None:
      <td>
        <table class="table">
          <thead>
            <tr>
              <th>${_("Andmetüüp")}</th>
              <th>${_("Selgitus")}</th>
            </tr>
          </thead>
          <tbody>
            % for arg in args:
            <tr>
              <td>${arg[1]}</td>
              <td>${arg[2]}</td>
            </tr>
            % endfor
          </tbody>
        </table>
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
</%def>

<script>
  $('.fb-cmd').click(function(){
    var b = $(this).find('.fb-buf').text();
    CKEDITOR.plugins.feedbackdiagram.commands.feedbackvar.gap_update(b);
    close_dialog();  
  });
</script>
