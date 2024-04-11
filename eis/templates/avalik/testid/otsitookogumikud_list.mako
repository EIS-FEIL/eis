% if not c.items:
${_("Otsingu tingimustele vastavat töökogumikku ei leitud")}
% else:
% for rcd in c.items:
<% c.tookogumik = rcd %>
<%include file="otsitookogumikud.tookogumik.mako"/>
% endfor
<span id="add" class="invisible">
${h.submit(_('Salvesta'))}
</span>
% endif

