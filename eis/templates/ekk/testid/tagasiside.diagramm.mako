<%include file="/common/message.mako"/>
${h.form_save(None, h.url('test_tagasiside_create_diagramm', test_id=c.test_id, testiosa_id=c.testiosa_id), form_name='form_dlg')}
${h.hidden('dname', c.dname)}
<% txt = c.opt.title_feedbackdgm(c.dname) %>
${h.hidden('name', txt)}
<h3>${txt}</h3>

<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Testimiskord"), 'tk_tahis')}
    <div class="col-md-4">
      ${h.text('tk_tahis', c.tk_tahis)}
    </div>
  </div>
</div>

% if c.dname == const.DGM_TUNNUSED1:
${self.d_tunnused1()}
% elif c.dname == const.DGM_BARNP:
${self.d_barnp()}
% elif c.dname == const.DGM_TUNNUSED2:
${self.d_tunnused2()}
% elif c.dname == const.DGM_TUNNUSED3:
${self.d_tunnused3()}
% elif c.dname == const.DGM_KLASSYL:
${self.d_klassyl()}
% elif c.dname == const.DGM_HINNANG:
${self.d_hinnang()}
% elif c.dname == const.DGM_GTBL:
${self.d_gtbl()}
% elif c.dname == const.DGM_KTBL:
${self.d_ktbl()}
% elif c.dname == const.DGM_OPYLTBL:
${self.d_opyltbl()}
% else:
${_("Diagrammi liik on valimata")}
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
  % if c.dname == 'gtbl':
  ${self.gtbl_btns()}
  % endif
  </div>
  ${h.submit_dlg()}
</div>
${h.end_form()}

<%def name="d_tunnused1()">
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 500)}
    </div>
  </div>

  <div class="form-group row">
    <div class="col-md-4 rounded border">
      ${h.flb(_("X-telg (tunnused)"))}

      <div class="form-group row">
        ${h.flb3(_("Nimetus"))}
        <div class="col-md-9">
          ${h.text('x_label', c.x_label)}
        </div>
      </div>
      <div class="form-group row">
        ${h.flb3(_("Tunnused"))}
        <div class="col-md-9">
          % for ind in range(12):
          <div class="d-flex">
            <div style="width:50px">${ind}</div>
            <%
              try:
                  label = c.npkoodid[ind]
              except:
                  label = ''
            %>
              ${h.text('npkoodid-%d' % ind, label, class_="npkood")}
          </div>
          % endfor
        </div>
      </div>
      % if c.koik_nptunnused:
      <div class="form-group row">
        <div class="col-12">
          ${_("Testis kirjeldatud tagasiside tunnused")}:<br/>
          ${', '.join(c.koik_nptunnused)}
        </div>
      </div>
      % endif
      
    </div>

    <div class="col-md-4 rounded border">
      ${h.flb(_("Y-telg (tasemed)"))}
      <div class="form-group row">
        ${h.flb3(_("Nimetus"))}
        <div class="col-md-9">
          ${h.text('y_label', c.y_label)}
        </div>
      </div>
    </div>

    <div class="col-md-4 rounded border">
      <div class="form-group row">
        ${h.flb3(_("Tasemed"))}
        <div class="col-md-9">
          % for ind in range(5):
          <div class="d-flex">
            <div style="width:50px">${ind}</div>
            <%
              try:
                  label = c.tasemed[ind]
              except:
                  label = ''
            %>
              ${h.text('tasemed-%d' % ind, label, class_="tase")}
          </div>
          % endfor
        </div>
      </div>
    </div>
   
  </div>
 
</div>
${self.colors()}
</%def>

<%def name="d_barnp()">
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 130)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Kõrgus"), 'height')}
    <div class="col-md-4">
      ${h.posint5('height', c.height or 20)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Viide tunnusele"))}
    <div class="col-md-4">
      ${h.text('np_kood', c.np_kood)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Värvid"), 'colors')}
    <div class="col-md-9" id="colors">
      <table>
        <thead>
          ${h.th(_("Lävi"))}
          ${h.th(_("Värv"))}
        </thead>
        <tbody>
          % for ind in range(5):
          <%
            niv = c.colornivs and len(c.colornivs) > ind and c.colornivs[ind] or None
            color = c.colors and len(c.colors) > ind and c.colors[ind] or None
          %>
          <tr>
            <td>
              ${h.posfloat('colornivs-%d' % ind, niv)}
            </td>
            <td>
              <div class="px-3 p-1 mr-2 samplecolor">
                ${h.text('color-%d' % ind, color, size=8, class_="color")}
              </div>
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </div>
  
</div>
</%def>

<%def name="d_tunnused2()">
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 600)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Sugu"), 'sex')}
    <div class="col-md-4">
      ${h.select_radio('sex', c.sex or '', c.opt_sugu)}
    </div>
  </div>

  <div class="form-group row">
    <div class="col-md-6 rounded border">
      ${h.flb(_("X-telg (tunnused)"))}

      <div class="form-group row">
        ${h.flb3(_("Nimetus"))}
        <div class="col-md-9">
          ${h.text('x_label', c.x_label)}
        </div>
      </div>
      
      <div class="form-group row">
        ${h.flb3(_("Tunnused"))}
        <div class="col-md-9">
          % for ind in range(12):
          <div class="d-flex">
            <div style="width:50px">${ind}</div>
            <%
              try:
                  label = c.npkoodid[ind]
              except:
                  label = ''
            %>
              ${h.text('npkoodid-%d' % ind, label, class_="npkood")}
          </div>
          % endfor
        </div>
      </div>
      % if c.koik_nptunnused:
      <div class="form-group row">
        <div class="col-12">
          ${_("Testis kirjeldatud tagasiside tunnused")}:<br/>
          ${', '.join(c.koik_nptunnused)}
        </div>
      </div>
      % endif
      
    </div>

    <div class="col-md-6 rounded border">
      ${h.flb(_("Y-telg (tasemed)"))}
      <div class="form-group row">
        ${h.flb3(_("Nimetus"))}
        <div class="col-md-9">
          ${h.text('y_label', c.y_label)}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Tasemed"))}
        <div class="col-md-9">
          % for ind in range(5):
          <div class="d-flex">
            <div style="width:50px">${ind}</div>
            <%
              try:
                  label = c.tasemed[ind]
              except:
                  label = ''
            %>
              ${h.text('tasemed-%d' % ind, label, class_="tase")}
          </div>
          % endfor
        </div>
      </div>
    </div>
   
  </div>

</div>
${self.colors()}
</%def>

<%def name="d_tunnused3()">
<div>
X-teljel on tasemed (iga taseme juures on iga klassi kohta eraldi tulp).
Y-teljel on taseme saanud õpilaste arv.
</div>
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 600)}
    </div>
  </div>

  <div class="form-group row">
    <div class="col-md-6 rounded border">
      <div class="form-group row">
        ${h.flb3(_("Tasemed"))}
        <div class="col-md-9">
          % for ind in range(5):
          <div class="d-flex">
            <div style="width:50px">${ind}</div>
            <%
              try:
                  label = c.tasemed[ind]
              except:
                  label = ''
            %>
              ${h.text('tasemed-%d' % ind, label, class_="tase")}
          </div>
          % endfor
        </div>
      </div>
    </div>

    <div class="col-md-6 rounded border">
      <div class="form-group row">
        ${h.flb3(_("Tunnus"))}
        <div class="col-md-9">
          ${h.text('np_kood', c.np_kood, class_="npkood")}
        </div>
      </div>
      % if c.koik_nptunnused:
      <div class="form-group row">
        <div class="col-12">
          ${_("Testis kirjeldatud tagasiside tunnused")}:<br/>
          ${', '.join(c.koik_nptunnused)}
        </div>
      </div>
      % endif
    </div>

  </div>
</div>
${self.colors()}
</%def>

<%def name="d_klassyl()">
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 500)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Ülesanded"), 'tykoodid')}
    <div class="col">
      <% is_all = c.tykoodid_all or not c.tykoodid %>
      ${h.checkbox1('tykoodid_all', 1, checked=is_all, label=_("Kõik ülesanded"))}
      % for (tykood, label) in c.opt_tykoodid:
      ${h.checkbox('tykoodid', tykood, checked=is_all or tykood in c.tykoodid, label=label)}
      % endfor
      <script>
        $('#tykoodid_all').change(function(){
        if(this.checked) $('input[name="tykoodid"]').prop('checked', true);
        });
        $('input[name="tykoodid"').change(function(){
        if(!this.checked) $('input#tykoodid_all').prop('checked', false);
        });        
      </script>
    </div>
  </div>
</div>
${self.colors()}
</%def>

<%def name="d_hinnang()">
<div class="mb-2">
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Laius"), 'width')}
    <div class="col-md-4">
      ${h.posint5('width', c.width or 600)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Viide küsimusele"))}
    <div class="col-md-4">
      ${h.text('ty_kood', c.ty_kood)}
    </div>
  </div>
  % if c.koik_kysimused:
  <div class="form-group row">
    <div class="col-12">
      ${_("Küsitluses esinevad küsimused")}:<br/>
      ${', '.join(c.koik_kysimused)}
    </div>
  </div>
  % endif

  <div class="form-group row">
    <div class="col">
      ${h.checkbox('reverse', '1', checked=c.reverse, label=_("Pööratud järjekord"))}
    </div>
  </div>
  
</div>
${self.colors()}
</%def>

<%def name="colors()">
<div>
  <div>
    ${h.checkbox1('colors_def', 1, checked=not c.colors, label=_("Kasuta vaikimisi värve"))}
  </div>
  <div id="colorway">
  <div class="d-flex flex-wrap">
    <div class="mr-4">${_("Värvid:")}</div>
       % for n in range(6):
        <% color = c.colors and len(c.colors) > n and c.colors[n] or '' %>
        <div class="px-3 p-1 mr-2 samplecolor">
          ${n+1}. ${h.text('color-%d' % n, color, size=8, class_="color")}
        </div>
        % endfor
      </div>
  </div>
  </div>
<script>
  $('#colorway').toggle(!$('#colors_def').prop('checked'));
  $('#colors_def').change(function(){
    $('#colorway').toggle(!$('#colors_def').prop('checked'));
  });
</script>
</div>
</%def>

<%def name="d_gtbl()">
<%
  grid_id = 'tbl_gtbl'
  prefix = 'tcol'
%>
${h.hidden('width', '')}
  <% ch = h.colHelper('col-md-3', 'col-md-9') %>
  <div class="form-group row">
    ${ch.flb(_("Pealkiri"), 'heading')}
    <div class="col">
      ${h.text('heading', c.heading)}
    </div>
  </div>

<div class="form-group row">
  ${ch.flb(_("Tabeli read"),'rows')}
  <div id="rows" class="d-flex flex-wrap">
    <div>
      ${h.checkbox('avg_row', const.FBR_SOORITAJA, checkedif=c.avg_row, label=_("iga sooritaja"))}
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_GRUPP, checkedif=c.avg_row, label=_("grupi keskmine"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_GRUPP_PR, checkedif=c.avg_row, label=_("grupi keskmine %"))}
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_KOOL, checkedif=c.avg_row, label=_("kooli keskmine"))}
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_MAAKOND, checkedif=c.avg_row, label=_("maakonna keskmine"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_LINN, checkedif=c.avg_row, label=_("omavalitsuse keskmine"))}    
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_RIIK, checkedif=c.avg_row, label=_("Eesti keskmine"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_RIIK_PR, checkedif=c.avg_row, label=_("Eesti keskmine %"))}
    </div>
  </div>
</div>

<table id="${grid_id}" class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th(_("Veeru nimetus"))}
      ${h.th(_("Veeru sisu"))}
      ${h.th(_("Kuvamine"))}
      % if c.is_edit and not c.is_tr:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_gtbl(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.tcol):
        ${self.row_gtbl(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
% if c.is_edit and not c.is_tr:
  <tfoot id="sample_${grid_id}" class="d-none sample">
   ${self.row_gtbl(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
% endif
</table>
<script>
  ## veeru sisu valikul pannakse vaikimisi veeru nimetus
  $('table#${grid_id}').on('change', 'select.tbl-expr', function(){
    var f = $(this).closest('tr').find('.tbl-name');
    if(f.val() == '') f.val($(this).find('option:selected').text());
  });

  function show_dtype(expr_fld, setdflt){
     var dtype_fld = $(expr_fld).closest('tr').find('.tbl-dtype'), expr = $(expr_fld).val() || '';
     ## ajakulu kuvamine on võimalik ainult testiosa korral
     dtype_fld.find('option[value="${const.FBD_AJAKULU}"]').toggle(expr.startsWith("${const.FBC_TESTIOSA}."));
     ## taseme kuvamine on võimalik ainult kogu testi korral
     dtype_fld.find('option[value="${const.FBD_TASE}"]').toggle(expr.startsWith("${const.FBC_TEST}."));
     ## tagasiside teksti kuvamine on võimalik ainult tagasisidetunnuse korral
     dtype_fld.find('option[value="${const.FBD_TEKST}"]').toggle(expr.startsWith("${const.FBC_NP}."));
     if(setdflt)
     {
       ## tagasiside tunnuse valimisel valime vaikimisi teksti
       if(expr.startsWith("${const.FBC_NP}")) dtype_fld.val("${const.FBD_TEKST}");
     }
     ## kui varem kehtinud valik peideti, siis valime midagi muud
     if(dtype_fld.find('option:selected').css('display') == 'none'){
        var dtype = dtype_fld.find('option').filter(function(){ return $(this).css('display') != 'none';}).eq(0).prop('value');
        dtype_fld.val(dtype);
     }
  }
  $('#tbl_gtbl').on('change', '.tbl-expr', function(){ show_dtype(this, true); });
  $('#tbl_gtbl .tbl-expr').each(function(){ show_dtype(this, false); });

</script>
</%def>

<%def name="gtbl_btns()">
<% grid_id = 'tbl_gtbl' %>
% if c.is_edit and not c.is_tr:
${h.button(_("Lisa"), onclick=f"grid_addrow('{grid_id}');", level=2, mdicls='mdi-plus')}
% endif
</%def>

<%def name="row_gtbl(item, prefix)">
<% item = c.new_item.create_from_dict(item) %>
<tr>
  <td>
    ${h.text('%s.name' % prefix, item.name, class_="tbl-name")}
  </td>
  <td>
    ${h.select('%s.expr' % prefix, item.expr, c.opt_expr, class_="tbl-expr")}
  </td>
  <td>
    ${h.select('%s.displaytype' % prefix, item.displaytype,
    c.opt_displaytype, class_="tbl-dtype")}
  </td>
  % if c.is_edit and not c.is_tr:
  <td>
    ${h.grid_remove()}
    <span class="glyphicon glyphicon-chevron-up tsg-up"></span>
    <span class="glyphicon glyphicon-chevron-down tsg-down"></span>
  </td>
  % endif
</tr>
</%def>              

<%def name="d_ktbl()">
<%
  grid_id = 'tbl_ktbl'
  prefix = 'tcol2'
%>
${h.hidden('width', '')}
<div class="form-group row">
  ${h.flb3(_("Tabeli read:"))}
  <div class="col-md-9 d-flex flex-wrap">
    <div>
      ${h.checkbox('avg_row', const.FBR_KOOL, checkedif=c.avg_row, label=_("kooli keskmine"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_KLASS, checkedif=c.avg_row, label=_("klasside keskmised"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_OPETAJA, checkedif=c.avg_row, label=_("aineõpetajate kaupa keskmised"))}      
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_LINN, checkedif=c.avg_row, label=_("omavalitsuse keskmine"))}
      <br/>
      ${h.checkbox('avg_row', const.FBR_MAAKOND, checkedif=c.avg_row, label=_("maakonna keskmine"))}
    </div>
    <div>
      ${h.checkbox('avg_row', const.FBR_RIIK, checkedif=c.avg_row, label=_("Eesti keskmine"))}
    </div>
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Tabeli veerud:"))}
  <div class="col-md-9 d-flex flex-wrap">
    % for key, label in c.opt_expr:
    <div style="width:250px">
      ${h.checkbox('tcol2', key, checkedif=c.tcol2, label=label)}
    </div>
    % endfor
  </div>
</div>
</%def>              

<%def name="d_opyltbl()">
${h.hidden('width', '')}
</%def>


<script>
  % if c.buf_params:
    var b = "${c.buf_params}";
    CKEDITOR.plugins.feedbackdiagram.commands.fbdiagram.gap_update(b);
    close_dialog();
  % endif
  
  function showcolor(fld)
  {
     $(fld).closest('.samplecolor').css('background-color', (fld.value ? fld.value : '#fff'));
  }
  $(function(){
    $('input.color').each(function(){ showcolor(this);});
    $('input.color').change(function() {showcolor(this);});
  });
</script>
