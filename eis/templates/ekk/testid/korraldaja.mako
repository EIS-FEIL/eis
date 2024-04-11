<%inherit file="/common/dlgpage.mako"/>

${h.form_search(url=h.url('test_korraldajad', test_id=c.test.id))}
${h.hidden('komplekt_id', c.komplekt_id)}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"))}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    % if c.user.has_permission('ylesanderoll', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    % endif
    <div class="col-12">
      <div class="form-group text-right">
        ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('test_korraldajad', test_id=c.test.id))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items != '':
${_("Otsingu tingimustele vastavaid isikuid ei leitud")}
% endif

% if c.items:
${h.form(h.url('test_eeltest', test_id=c.test.id, id=c.komplekt_id), method='put')}
${h.hidden('sub', 'korraldaja')}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th></th>
            ${h.th_sort('isikukood', _("Isikukood"))}
            ${h.th_sort('eesnimi perenimi', _("Nimi"))}
            <th>E-post</th>
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.id, onclick="toggle_add()", class_="oigus")}</td>
            <td>${rcd.isikukood}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
              ${h.hidden('i%s_eesnimi' % rcd.id, rcd.eesnimi)}
              ${h.hidden('i%s_perenimi' % rcd.id, rcd.perenimi)}
            </td>
            <td class="err-parent">
              % if rcd.epost:
                ${rcd.epost}
              % else:
                ${h.text('i%s_epost' % rcd.id, '')}
              % endif
            </td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add()
  {
         var visible = ($('input:checked.oigus').length > 0);
         $('#add').toggleClass('invisible', !visible);
  };
</script>

<div id="add" class="invisible text-right">
  ${h.submit(_("Salvesta"), id='add_isik')}
</div>

${h.end_form()}
% endif
