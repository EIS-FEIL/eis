## Faili üleslaadimine
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% c.block.kysimus.give_kyslisa() %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'ul.mimetype' %>
  ${ch.flb(_("Laaditava faili MIME tüüp"), name)}
  <div class="col-md-9 col-xl-10">
    ${h.select('ul.mimetype', c.block.kysimus.kyslisa.mimetype, c.opt.mimetype_empty, wide=False)}
  </div>
</div>

<% tulemus = c.block.kysimus.tulemus or c.new_item(kood=c.block.kysimus.kood) %>
${h.hidden('am1.kysimus_id', c.block.kysimus.id)}

<div class="d-flex flex-wrap gbox hmtable overflow-auto mb-3">
  <div class="bg-gray-50 p-3">
    ${choiceutils.tulemus(c.block.kysimus, tulemus, 'am1.', maatriks=False)}
  </div>
  <div class="flex-grow-1 p-3">  
    ${choiceutils.naidisvastus(c.block.kysimus, tulemus, 'am1.', rows=9, naha=False)}
  </div>
</div>
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
${h.qcode(kysimus, nl=True)}
<div class="asblock asblock-iupload d-flex flex-wrap">
  <%
    files = []
    if c.prepare_response:
       kv = c.responses.get(kysimus.kood)
       if kv:
           for kvs in kv.kvsisud:
               if kvs.has_file:
                   fn = f'file.{kvs.fileext}'
                   filesize = kvs.filesize
                   files.append((kvs.url, fn, filesize))
  %>
  % if not c.block.read_only:
      <div>
        ${h.file(kysimus.result, value=_("Fail"),accept=kysimus.kyslisa.mimetype, files=files)}
      </div>
      <div class="save-status p-1">
        ${h.spinner(_("Salvestan..."), 'upload-spinner', True)}
        ${h.mdi_icon('mdi-check-circle-outline ml-1 mdi-green upload-saved', style="display:none")}
      </div>
  % else:
      % for url, fn, filesize in files:
      <a
        % if url:
        href="${kvs.url}"
        % endif
        % if fn.endswith('.htm') or fn.endswith('.html'):
        target="_blank"
        % endif
        class="p-2">
        ${fn}
      </a>
      % endfor
  % endif
</div>
</%def>

<%def name="block_view_js()">
</%def>

<%def name="block_print()">

</%def>


<%def name="block_entry()">
<div class="td-sis-value2">${_("Faili ei sisestata")}</div>
</%def>
