<h3>${_("Testide läbiviimisega seotud isikud")}</h3>
${h.rqexp()}
<table class="table table-striped tablesorter"  width="100%" id="tbl_labiviijad">
  <thead>
    <tr>
      ${h.th(_("Läbiviija tähis"))}
      ${h.th(_("Läbiviija"))}
      ${h.th(_("Roll"))}
      ${h.th(_("Olek"), rq=True)}
      ${h.th(_("Ruum"))}
      ${h.th(_("Maht/aeg"))}
    </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.labiviijad):
  <tr>
    <td>${rcd.tahis}</td>
    <td>
      % if rcd.kasutaja:
      ${rcd.kasutaja.nimi}
      % else:
      ${_("Määramata")}
      % endif
      ${h.hidden('lv-%d.id' % n, rcd.id)}
    </td>
    <td>
      ${rcd.kasutajagrupp.nimi}
    </td>
    <td>
      ##${h.select('lv-%d.staatus' % n, rcd.staatus, c.opt.klread_kood('S_STAATUS'))}
      ${h.radio('lv-%d.staatus' % n, const.L_STAATUS_OSALENUD,
      checkedif=rcd.staatus, label=_("Osales"))}
      ${h.radio('lv-%d.staatus' % n, const.L_STAATUS_PUUDUNUD,
      checkedif=rcd.staatus, label=_("Puudus"))}
    </td>
    <td>${rcd.testiruum and rcd.testiruum.tahis}</td>
    <td>
      % if rcd.kasutajagrupp_id in (const.GRUPP_VAATLEJA, const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES):
      ${h.checkbox('lv-%d.yleaja' % n, checked=rcd.yleaja, label=_("Üleaja"))}
      ${h.time('lv-%d.toolopp' % n, rcd.toolopp)}
      % else:
      ${rcd.toode_arv}
      % endif
    </td>
  </tr>
  % endfor
  </tbody>
</table>
<p>
% if c.is_edit:
${h.button(_("Märgi kõik läbiviijad osalenuks"),
onclick="$('#tbl_labiviijad input[name$=staatus][value=%s]').prop('checked',true)" % (const.L_STAATUS_OSALENUD), level=2)}
% endif
</p>
