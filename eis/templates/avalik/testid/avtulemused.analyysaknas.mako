<%inherit file="/common/page.mako"/>
<%def name="require()">
<%
  c.includes['math'] = True
  c.hide_header_footer = True
%>
</%def>
<%def name="page_headers()">
## et lingid avaneks suures aknas
<base target="_parent"/>
</%def>
<% c.fblinks = True %>
<%include file="/ekk/hindamine/analyys.vastus.mako"/>
