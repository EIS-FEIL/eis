
${h.form_search(url=h.url('ylesanded_hulgi_isikud', ylesanded_id=c.ylesanded_id))}
<table class="table"  width="100%">
  <tr>
    <td class="fh">${_("Isikukood")}</td>
    <td>${h.text('isikukood', c.isikukood)}</td>
  </tr>
  <tr>
    <td class="fh">${_("Eesnimi")}</td>
    <td>${h.text('eesnimi', c.eesnimi)}</td>
  </tr>
  <tr>
    <td class="fh">${_("Perekonnanimi")}</td>
    <td>${h.text('perenimi', c.perenimi)}</td>
    <td>
      ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('ylesanded_hulgi_isikud', ylesanded_id=c.ylesanded_id))}
    </td>
  </tr>
</table>
${h.end_form()}

% if c.items:
${h.form(h.url('ylesanded_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'isik')}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th></th>
            ${h.th_sort('nimi', _("Nimi"))}
            <th></th>
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.isikukood, onclick="toggle_add()", class_="oigus", title=_("Vali rida"))}</td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
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
     $('table#add').toggle(visible);
  };
</script>

<table id="add" style="display:none">
  <tr>
    <td>
      ${h.submit(_("Salvesta"), id='add_isik')}
    </td>
    <td>
      <div style="margin:7px 0">      
        ${h.select('kasutajagrupp_id', '', c.opt.ylesandegrupp)}
      </div>
      <div>
        ${_("Kehtib kuni")} ${h.date_field('kehtib_kuni', '')}
      </div>
    </td>
  </tr>
</table>

${h.end_form()}
% endif
