<%
  c.protsessid_no_empty = True
  c.protsessid_caption = _("Tulemuste ja statistika arvutamine")
%>
<%include file="/common/arvutusprotsessid.mako"/>
<div class="text-right mb-2">
    ${h.form_save(None)}
    % if c.testiruum_id:
    ${h.submit(_('Arvuta tulemused üle'))}
    % endif
    ${h.submit(_('Arvuta statistika'), id='stat')}
    ${h.hidden('debug', c.debug)}
    ${h.end_form()}
</div>
