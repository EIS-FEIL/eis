<!DOCTYPE html>
<html lang="${request.locale_name}">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Expires" content="-1"/>
  ${self.require()}
  <%include file="include.mako"/>
  ${self.page_headers()}
  <title>${self.page_title()}</title>
  <!-- ${next.name} -->
</head>
<body>
  <%include file="/common/message.mako" />
  ${next.body()} 
</body>
</html>

<%def name="page_headers()"></%def>
<%def name="page_title()">${c.inst_title}</%def>
<%def name="breadcrumbs()"></%def>
<%def name="require()"></%def>
