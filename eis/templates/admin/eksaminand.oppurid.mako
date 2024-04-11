<%include file="/common/message.mako"/>
<%
  opilased = list(c.kasutaja.opilased)
%>
% if not opilased:
${h.alert_notice(_("EHISe õppimise andmed puuduvad"), False)}
% else:
<table class="table table-borderless table-striped" border="0" >
  <caption>${_("Õppimise andmed EHISest")}</caption>
  <thead>
    <tr>
      ${h.th(_("Kool"))}
      ${h.th(_("Klass"))}
      ${h.th(_("Paralleel"))}
      ${h.th(_("Kooli tüüp"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Lõpetamisaasta"))}
      ${h.th(_("Andmed seisuga"))}
    </tr>
  </thead>
  <tbody>
% for op in c.kasutaja.opilased:
<%
  koht = op.koht
%>
<tr>
  <td>
    % if koht:
    ${koht.nimi}
    % else:
    ${_("EHIS ID")} ${op.kool_id}
    % endif
  </td>
  <td>${op.klass}</td>
  <td>${op.paralleel}</td>
  <td>
    % if koht:
    ${koht.koolityyp_nimi}
    % endif
  </td>
  <td>${op.on_lopetanud and _("Lõpetanud") or _("Õpib")}</td>
  <td>${op.lopetamisaasta}</td>
  <td>${h.str_from_datetime(op.seisuga)}</td>
  % if c.is_debug or request.params.get('debug'):
  <td>${op.id} prioriteet ${op.prioriteet}</td>
  % endif
</tr>
% endfor
  </tbody>
</table>
% endif

## leiame varasemad koolid testisoorituste andmetest
<%
  koolid_id = [o.koht_id for o in opilased]
  q = (model.Session.query(model.Koolinimi.nimi).distinct()
       .join(model.Sooritaja.koolinimi)
       .filter(model.Sooritaja.kasutaja_id==c.kasutaja.id)
       )
  if koolid_id:
      q = q.filter(~ model.Koolinimi.koht_id.in_(koolid_id))
  q = q.order_by(model.Koolinimi.nimi)
  vanad_koolid = [nimi for nimi, in q.all()]
%>
% if vanad_koolid:
<div class="my-2">
  ${_("Varasemad õppeasutused EISi andmetel")}: ${', '.join(vanad_koolid)}
</div>
% endif

<% pooleli = [op for op in opilased if not op.on_lopetanud] %>
% if len(pooleli) > 1:
<%
  opilane = c.kasutaja.opilane
  opt_pooleli = []
  for op in pooleli:
     koht = op.koht
     label = '%s %s%s' % (koht and koht.nimi or op.kool_id, op.klass or '', op.paralleel or '')
     opt_pooleli.append((op.id, label))
%>
<div>
  ${_("Registreeringutega seotakse")}
  ${h.select('prioriteet_op_id', opilane.id, opt_pooleli, wide=False)}
</div>
% endif
% if c.kasutaja.isikukood:
${h.button(_("Uuenda andmed EHISest"),
onclick="ajax_url('%s','get','#oppurid')" % h.url_current('show', id=c.kasutaja.id, sub='oppurid'), level=2)}
% endif
% if c.kasutaja.opilane_seisuga:
(${_("Isiku EHISe andmed seisuga")} ${h.str_from_datetime(c.kasutaja.opilane_seisuga)})
% endif

