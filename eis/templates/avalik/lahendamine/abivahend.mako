<!DOCTYPE html>
<html lang="et">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Expires" content="-1"/>
  <% c.on_esitlus = True %>
  <%include file="/common/include.mako"/>
  <style>
    body, td {font-size:14px;}
    hr {
    margin: 7px 0;
    }
    h2 {
    margin-block-start: 0.83em;
    margin-block-end: 0.83em;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    }
    table {
    border-collapse: separate;
    }    
  </style>
  <% t_item = c.item.tran(request.locale_name) %>
  <title>${t_item.nimi}</title>
  ${t_item.pais}
</head>
<body>
${t_item.kirjeldus}
</body>
</html>
