## Isikute otsimine ja uute kasutajarollide lisamine soorituskohale

<%include file="/common/message.mako" />
## tulles kohakasutajate kontrollerist, on seatud sub ('roll' või 'kasutaja')
## tulles isikute otsimise kontrollerist, on seatud savesub 
<% sub = c.params.get('sub') or c.params.get('savesub') %>
## kui otsitakse uut isikut, siis kuvame otsinguvormi

${h.form_search(url=h.url('admin_koht_isikud', koht_id=c.koht.id))}
${h.hidden('savesub', sub)}
${h.hidden('partial','true')}
${h.rqexp(True, _("Palun sisesta vähemalt isikukood või perekonnanimi"))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
          ${h.flb(_("Isikukood"),'isikukood')}
          ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
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
${_("Otsingu tingimustele vastavaid isikuid ei leitud")}
% elif c.items:
${h.form(h.url('admin_koht_kasutajad', koht_id=c.koht.id))}
${h.hidden('sub', sub)}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th></th>
            ${h.th_sort('isikukood', _("Isikukood"))}
            ${h.th_sort('nimi', _("Nimi"))}
            <th></th>
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.isikukood, class_="oigus")}
              % if not rcd.id:
              ## kasutajakontot veel pole olemas
              ${h.hidden('eesnimi',rcd.eesnimi)}
              ${h.hidden('perenimi',rcd.perenimi)}
              % endif
            </td>
            <td>${rcd.isikukood}</td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
     grupp_changed();
     toggle_add();
     $('input.oigus').click(toggle_add);
     $('button#add_isik').click(function(){
     % if c.app_eis:
        ## avalikus vaates on kohustuslik panna rollile kehtivuse kuupäev
        if(!$('#r_kuni').hasClass('d-none') && $('#kehtib_kuni').val() == ''){
          $('#kehtib_kuni_err').show();
          return;
        }
     % endif
        submit_dlg(this);
     });
  });
  function toggle_add()
  {
    var visible = ($('input:checked.oigus').length > 0);
    $('#add').toggleClass('invisible', !visible);
  };
  function grupp_changed()
  {
     var grupp_id = $('select#kasutajagrupp_id').val();
     var b = (grupp_id == '${const.GRUPP_AINEOPETAJA}');
     $('#r_aine').toggleClass('d-none', !b);
     ## seotud isikul pole kehtivust
     $('#r_kuni').toggleClass('d-none', (grupp_id == "1000"));
  }

</script>

<div id="add" class="invisible">
  % if sub == 'roll':
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.flb(_("Roll"), rq=True)}
        ${h.select('kasutajagrupp_id', c.item and c.item.kasutajagrupp_id, c.opt_grupid, onchange='grupp_changed()')}
      </div>
    </div>
    <div class="col-12 col-md-6" id="r_kuni">
      <div class="form-group">
        ${h.flb(_("Kehtib kuni"), rq=c.app_eis)}
        ${h.date_field('kehtib_kuni', c.item and c.item.kehtib_kuni_ui)}
        <div id="kehtib_kuni_err" class="error" style="display:none">
          ${_("Palun sisestada väärtus")}
        </div>
      </div>
    </div>
    <div class="d-none col-12 col-md-6" id="r_aine">
      <div class="form-group">
        ${h.flb(_("Õppeaine"))}
        ${h.select('aine_kood', c.item and c.item.aine_kood,
        c.opt.klread_kood('AINE', vaikimisi=c.item and c.item.aine_kood or None))}
      </div>
    </div>
  </div>
  % endif
  ${h.button(_("Salvesta"), id='add_isik')}
</div>
${h.end_form()}

% endif
