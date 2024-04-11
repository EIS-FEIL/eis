${h.form_search(url=h.url('admin_kasutaja_nousolekud', kasutaja_id=c.kasutaja.id))}
${h.hidden('sub','testid')}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      ${h.flb(_("Testsessioon"), 'testsessioon_id')}
      ${h.select('testsessioon_id', c.testsessioon_id,
      c.opt.testsessioon, empty=True)}
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      ${h.flb(_("Vastamise vorm"),'vastvorm')}
      ${h.select('vastvorm', c.vastvorm, c.opt.klread_kood('VASTVORM', vaikimisi=c.vastvorm),
      empty=True)}
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.items != '' and not c.items:
${_("Otsingu tingimustele vastavaid toimumisaegu ei leitud")}
% elif c.items:
${h.form(h.url('admin_kasutaja_nousolekud', kasutaja_id=c.kasutaja.id))}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_testid" width="100%">
        <thead>
          <tr>
            ${h.th(_("Nimi"))}
            ${h.th(_("Toimumisaeg"))}
            ${h.th(_("Rollid"))}
          </tr>
        </thead>
        <tbody>
          % for n, (rcd, nousolek) in enumerate(c.items):
          <tr>
            <td>
              ${rcd.testimiskord.test.nimi}
              ${rcd.tahised}
            </td>
            <td>${rcd.millal}</td>
            <td>
              ${h.hidden('ta-%s.toimumisaeg_id' % n, rcd.id)}
              % if rcd.vaatleja_maaraja:
              ${h.checkbox('ta-%s.on_vaatleja' % n, 1, checked=nousolek and nousolek.on_vaatleja, label=_("Vaatleja"))}
              % endif
              % if rcd.hindaja1_maaraja or rcd.hindaja1_maaraja_valim:
              ${h.checkbox('ta-%s.on_hindaja' % n, 1, checked=nousolek and nousolek.on_hindaja, label=_("Hindaja"))}
              % endif
              % if rcd.intervjueerija_maaraja:
              ${h.checkbox('ta-%s.on_intervjueerija' % n, 1, checked=nousolek and nousolek.on_intervjueerija, label=_("Intervjueerija"))}
              % endif
            </td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(function(){
     $('table#table_testid').tablesorter();
  });
</script>

<div class="text-right">
${h.submit(_("Salvesta"), id='add_isik')}
</div>
${h.end_form()}

% endif
