      <% found = False %>
      % for p in c.kasutaja.pedagoogid:
      % if not p.kehtib_kuni or p.kehtib_kuni >= h.date.today():
      <%
        found = True
        if p.on_ehisest:
           info = 'EHIS'
        else:
           info = 'EIS'
           if p.kehtib_kuni:
              info += ', ' + _("kuni {dt}").format(dt=h.str_from_date(p.kehtib_kuni))
      %>
      ${p.koht and p.koht.nimi} (${info})
      % if p.kasutajagrupp:
      ${p.kasutajagrupp.nimi.lower()}
      <%
        koodid = set([r.ehis_aine_kood for r in p.ainepedagoogid])
        nimed = [model.Klrida.get_str('EHIS_AINE', r) for r in koodid]
        ained = sorted([r.lower() for r in nimed if r])
      %>
      % if ained:
      (${', '.join(ained)})
      % endif
      % endif

      % if c.controller=='kasutajad':
      % if not p.on_ehisest and c.user.has_permission('kasutajad', const.BT_UPDATE):
      ${h.remove(h.url('admin_kasutaja_delete_amet', kasutaja_id=c.kasutaja.id, id=p.id))}
      % endif
      % endif
      <br/>
      % endif
      % endfor
      % if not found:
      ${_("Ametikohti ei leitud")}
      % endif

      % if request.is_ext():
      % if c.kasutaja.ametikoht_seisuga:
      (${_("EHISe andmed seisuga")} ${h.str_from_datetime(c.kasutaja.ametikoht_seisuga)})
      % else:
      (${_("EHISest pole kunagi kontrollitud")})
      % endif
      % endif
      <%include file="/common/message.mako"/>
