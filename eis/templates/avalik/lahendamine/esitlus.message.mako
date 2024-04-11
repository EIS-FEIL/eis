<html>
  <head>
    <%include file="/common/include.mako"/>
  </head>
  <%
    bodykw = ''
    if c.ty:
       bodykw = f' data-tyid="{c.ty.id}"'
  %>
  <body ${bodykw}>
    <div class="esitlus-body"></div>
    <div>
      <div id="testtys1">
        <%include file="/common/message.mako"/>
        ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner mx-3', hide=True)}
      </div>
    </div>
  </body>
</html>
