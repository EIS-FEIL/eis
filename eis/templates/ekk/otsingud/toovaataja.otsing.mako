## Isiku otsimine töövaataja rolli andmiseks
${h.form_search()}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"), 'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col d-flex align-content-end">
      <div class="form-group">
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<%include file="/common/message.mako"/>

% if c.items:
${h.form(url=h.url_current('create'))}
<div class="listdiv">
      <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <col width="100"/>
        <thead>
          <tr>
            <th></th>
            ${h.th(_("Isik"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <tr>
            <td>
              ${h.button(_("Vali"), id=f'vali_{rcd.id}', class_="vali")}
            </td>
            <td>${rcd.nimi}</td>
          </tr>
          % endfor
        </tbody>
      </table>
</div>

<div class="p-1">
${_("Kehtib kuni")}
${h.date_field('kehtib_kuni', '', wide=False)}
</div>

${h.end_form()}

<script>
  $('button.vali').click(function(){
  var f = $(this.form), url = f.attr('action'),
      data = f.serialize() + '&kasutaja_id=' + this.id.substr(5);
  dialog_load(url, data, 'POST', f.parent());
  });
</script>

% endif


