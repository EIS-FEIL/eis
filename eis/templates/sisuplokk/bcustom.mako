## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">

<div class="form-group row">
  <% name = 'mo.filedata' %>
  ${h.flb(_("Fail"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-9 col-xl-10">
    <%
      mo = c.block.taustobjekt
      if c.block_prefix and mo:
         files = [(mo.get_url(c.lang, c.url_no_sp), mo.filename, mo.filesize)]
      else:
         files = []
    %>
    ${h.file(name, value=_("Fail"), files=files)}
  </div>
</div>
</%def>

<%def name="block_view()">
  % if c.block.staatus and c.block.taustobjekt:
${h.link_to(c.block.taustobjekt.filename, c.block.taustobjekt.get_url(c.lang, c.url_no_sp), target='_blank')}
  % endif
</%def>

