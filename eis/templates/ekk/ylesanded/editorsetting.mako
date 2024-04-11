${h.form_save(c.item.id, form_name='form_dlg')}
${h.hidden('lang', c.lang)}
<%include file="/common/message.mako" />
<%
   c.icons = c.item.get_ckeditor_icons()
%>
% if c.is_edit:
<p>
${_("Vali hiirega klikkides nupud, mis kuvatakse lahendajale")}
</p>
% endif
<div class="border">
% for iconset in c.opt.ckeditor_iconsets:
% for icon, title, fname in iconset:
<% checked = icon in c.icons %>

        <label class="custom-control custom-checkbox custom-control-inline icon-setting m-1 mx-2">
          <input type="checkbox" value="${icon}" class="custom-control-input" id="icon_${icon}" name="icon" ${checked and 'checked' or ''}/>
          <span class="custom-control-label" for="icon_${icon}">
            % if fname:
            <img src="${fname}" border="1" alt="${title}" title="${title}"/>
            % else:
            ${title}
            % endif
          </span>
        </label>

% endfor
<br/>
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
