${h.form_save(c.item.id, form_name='form_dlg')}
${h.hidden('sub', 'icons')}
${h.hidden('lang', c.lang)}
<%include file="/common/message.mako" />
<%
  data = c.item.get_json_sisu()
  c.icons = data and data.get('icons') or []
%>
% if c.is_edit:
<p>
${_("Vali hiirega klikkides nupud, mis kuvatakse lahendajale")}
</p>
% endif
<div class="border">
% for r in c.opt.get_ipunkt_icons():
<%
  icon = r['name']
  value = r['value']
  checked = not c.icons or icon in c.icons
%>

        <label class="custom-control custom-checkbox custom-control-inline icon-setting m-1 mx-2">
          <input type="checkbox" value="${icon}" class="custom-control-input" id="icon_${icon}" name="icon" ${checked and 'checked' or ''}/>
          <span class="custom-control-label bg-gray-50 py-1 px-2" for="icon_${icon}">
            ${value}
          </span>
        </label>

% endfor
</div>

<br/>
% if c.updated:
    <script>
    close_dialog();
    </script>
% endif
<div class="d-flex">
  <div class="flex-grow-1">
    ${h.button(_("Tagasi"), onclick="close_dialog();", level=2)}
  </div>
  % if c.is_edit:
  ${h.submit_dlg()}
  % endif
</div>
${h.end_form()}
