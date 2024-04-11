## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
${_("Lahendajale antakse faili üles laadimise võimalus")}
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
${h.qcode(kysimus, nl=True)}
    % if not c.block.read_only:
      ${h.file(c.block_result, value=_("Fail"),accept=kysimus.kyslisa.mimetype)}
    % endif
    % if c.prepare_response and c.responded_files:
      <% vf = c.responded_files.get(c.block_result) %>
      % if vf:
      <%
        kv = c.responses.get(kysimus.kood)
        ks = kv and len(kv.kvsisud) and kv.kvsisud[0]
        if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
           corr_cls = model.ks_correct_cls(c.responses, kysimus.tulemus, kv, ks, False) or ''
        else:
           corr_cls = ''
      %>
      <div class="${corr_cls}">
        <a href="${vf.url}" target="_blank">Laadi vastus alla</a>
      </div>
      % endif
    % endif
</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Faili ei sisestata")}</div>
</%def>
