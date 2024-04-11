<%inherit file="/common/page.mako"/>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>
${next.body()}
