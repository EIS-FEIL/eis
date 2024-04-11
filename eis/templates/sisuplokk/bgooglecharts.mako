## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">
<%
  mo = c.block.give_meediaobjekt()
  if not mo.laius:
     mo.laius = 500
  if not mo.korgus:
     mo.korgus = 400

  di = mo.unpickle_sisu()
  c.ggc = c.new_item.create_from_dict(di) or c.new_item()
  if not c.ggc.header:
     c.ggc.header = c.new_item()
  if not c.ggc.data:
     c.ggc.data = [c.new_item()]

  if c.lang:
    di_tr = mo.unpickle_sisu(c.lang) or di
    c.ggc_tr = c.new_item.create_from_dict(di_tr) or c.new_item()
    if not c.ggc_tr.header:
       c.ggc.header = c.new_item()
    if not c.ggc_tr.data:
       c.ggc.data = [c.new_item()]
     
  
  charttypes = c.opt.get_googlecharts_metadata()
  
  opt_charttype = [(r['name'], r['title']) for r in charttypes]
  if not c.item.alamtyyp:
      c.item.alamtyyp = 'BarChart'

  ## valitud diagrammi metaandmed
  for di in charttypes:
     if di['name'] == c.item.alamtyyp:
          c.typedata = di
          break

  ## andmehulga veerg mitme andmehulgaga diagrammi korral
  c.multi_col = ''
  if c.typedata:
     for ind, col in enumerate(c.typedata['cols']):
         if col.get('multi'):
             c.multi_col = ind
             break
  ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4')
%>
<div class="row mb-2">
  <% name = 'f_alamtyyp' %>
  ${ch.flb(_("Diagrammi tüüp"), name)}
  <div class="col-md-3 col-xl-4">
      ${h.select('f_alamtyyp', c.item.alamtyyp, opt_charttype, onchange="onchange_alamtyyp()")}
      % if c.is_tr:
      ${h.hidden('f_alamtyyp', c.item.alamtyyp)}
      % endif
  </div>

  <% name = 'ggc.datasetcnt' %>
  ${ch.flb(_("Andmehulkade arv"), name)}
  <div class="col-md-3 col-xl-4">
      % if c.multi_col != '':
      ${h.select('ggc.datasetcnt', c.ggc.datasetcnt, range(1,10), onchange="onchange_datasetcnt()", wide=False)}
      % if c.is_tr:
      ${h.hidden('ggc.datasetcnt', c.ggc.datasetcnt)}
      % endif
      % else:
      1
      % endif
  </div>

  <% name = 'mo.laius' %>
  ${ch.flb(_("Laius"), name)}
  <div class="col-md-3 col-xl-1">
      ${h.posint5('mo.laius', mo.laius, maxvalue=900)}
      % if c.lang:
      ${h.hidden('mo.laius', mo.laius)}
      % endif
  </div>
  <% name = 'mo.korgus' %>
  ${ch.flb(_("Kõrgus"), name)}
  <div class="col-md-3 col-xl-1">
      ${h.posint5('mo.korgus', mo.korgus)}
      % if c.lang:
      ${h.hidden('mo.korgus', mo.korgus)}
      % endif
  </div>
</div>

<div>
  <h3>${_("Diagrammi andmed")}</h3>
  ${self.edit_data_table()}
</div>

<div>
  <h3>${_("Diagrammi seadistused")}</h3>
  <span class="error" id="options_err"></span>
  % if c.lang:
  ${h.lang_orig('')}<br/>
  <pre id="options">${c.ggc.options}</pre>
  <br/>
  ${h.lang_tag()}
  ${h.textarea('ggc.options', c.ggc_tr.options or '', rows=5, onchange="$('#options_err').text('');", ronly=not c.is_tr)}
  % else:
  ${h.textarea('ggc.options', c.ggc.options or '{\n}', rows=5, onchange="$('#options_err').text('');")}
  % endif
</div>

<div class="linebreak"></div>

${h.button(_("Genereeri diagramm"), onclick="gen_chart()")}
${h.hidden('f_sisuvaade', c.block.tran(c.lang).sisuvaade)}
${h.hidden('png_file', '')} 
<script>
  ${self.block_edit_js()}
</script>

<div id="chart_${c.block.id}"></div>
</%def>

<%def name="block_view()">
<% mo = c.block.meediaobjekt %>
<div id="chart_${c.block.id}" style="${h.width(mo, True)} ${h.height(mo, True)}"></div>
</%def>

<%def name="block_print()">
<% mo2 = c.block.taustobjekt %>
<% png = mo2 and mo2.tran(c.lang).filedata %>
% if png:
## png_file
<img src="${png.decode('utf-8')}"/>
% else:
${c.block.alamtyyp.split('.')[0]}
% endif
</%def>

<%def name="edit_data_table()">
% if c.typedata:
<table id="datatable" class="table table-borderless table-striped" border="0" > 
  <thead>
    ${self.header_metadata_row()}
    ${self.header_title_row()}    
  </thead>
  <tbody>
    <% prefix = 'data' %>
    % if c._arrayindexes != '' and not c.is_tr:
      ## valideerimisvigade korral
      % for cnt in c._arrayindexes.get(prefix) or []:
        ${self.edit_data_row('ggc.data', '-%s' % cnt, c.new_item(), c.new_item())}
      % endfor
    % else:
      ## tavaline kuva
      % for cnt, item in enumerate(c.ggc.data):
         <% item_tr = c.lang and c.ggc_tr.data[cnt] or None %>
         ${self.edit_data_row('ggc.data', '-%s' % cnt, item, item_tr)}
      % endfor
    % endif
  </tbody>
</table>
<br/>
% if c.is_edit and not c.lang:
   ${h.button(value=_("Lisa"), class_='button1', onclick="addrow()")}
<div id="sample_datatable" class="invisible">
    <!--
     ${self.edit_data_row('ggc.data', '__cnt__', c.new_item(), c.new_item())}
    -->
</div>
% endif
% endif
</%def>

<%def name="header_metadata_row()">
## andmetabeli päis, mis kirjeldab veerge ja kus valitakse rolliveerud
    <tr class="metadata">
      <% cols = c.ggc.header.col %>
      % for ind, dcol in enumerate(c.typedata['cols']):
      <%
        cnt = dcol.get('multi') and c.ggc.datasetcnt or 1
        coltitle = dcol['title']
        col = len(cols) > ind and cols[ind] or c.new_item()
        instances = col.inst or []
      %>
      % for ind1 in range(cnt):
      <%
        icol_id = '%s_%s' % (ind, ind1)
        prefix = 'ggc.header.col-%d.inst-%d' % (ind, ind1)
        inst = len(instances) > ind1 and instances[ind1] or c.new_item()
      %>
      <th class="headcol col-${ind} icol-${icol_id}" data-icol="${icol_id}" valign="top">
        % if dcol.get('optional'):
        ## mittekohustuslik veerg
        ${h.checkbox(prefix + '.active', 1, checked=inst.active, class_="active", onchange="onchange_active(this)")}
        % endif
        
        % if dcol.get('multi'):
        ## andmehulga veerg, mille nimetus võib sisaldada andmehulga järjekorranumbrit
        <span class="coltitle-template" style="display:none">${coltitle}</span>
        % endif
        <span class="coltitle">${coltitle.replace('{n}', str(ind1+1))}</span>
        <br/>

        ## arvulise veeru korral kuvame andmetyybi
        % if dcol['datatype'] == 'number':
        (${_("arv")})
        <br/>
        % endif

        ## veergu täiendavate võimalike rolliveergude valik
        <div style="padding-left:20px">
          % for role in dcol.get('roles') or []:
          ${h.checkbox(prefix + '.roles', role, checkedif=inst.roles, label=role, class_="role", onchange="onchange_role(this)")}
          <br/>
          % endfor
        </div>
      </th>
      % endfor
      % endfor
      <th></th>
    </tr>
</%def>

<%def name="header_title_row()">
## andmetabeli päis, kus on veergude nimetuste sisestusväljad
    <tr class="datarow">
      <%
        cols = c.ggc.header.col
        if c.lang:
           cols_tr = c.ggc_tr.header.col
      %>  
      % for ind, dcol in enumerate(c.typedata['cols']):
      <%
        cnt = dcol.get('multi') and c.ggc.datasetcnt or 1
        col = len(cols) > ind and cols[ind] or c.new_item()
        instances = col.inst or []
        if c.lang:
           col_tr = len(cols_tr) > ind and cols_tr[ind] or c.new_item()
           instances_tr = col_tr.inst or []
      %>
      % for ind1 in range(cnt):
      <%
        icol_id = '%s_%s' % (ind, ind1)
        prefix = 'ggc.header.col-%d.inst-%d' % (ind, ind1)
        inst = len(instances) > ind1 and instances[ind1] or c.new_item()
        if c.lang:
          inst_tr = len(instances_tr) > ind1 and instances_tr[ind1] or c.new_item()
     
        disabled = dcol.get('optional') and not inst.active
        datatype = dcol.get('datatype')
      %>
      <th class="datacol col-${ind} icol-${icol_id}" data-icol="${icol_id}">
        % if datatype != 'rolesonly':
        ##${h.text(prefix + '.value', inst.value, class_="datainp", disabled=disabled)}

          % if c.lang:
             ${h.lang_orig(inst.value)}<br/>
             ${h.lang_tag()}
             ${h.text(prefix + '.value', inst_tr.value, class_="datainp", disabled=disabled, ronly=not c.is_tr)}
             % if disabled:
             ${h.hidden(prefix + '.value', inst_tr.value)}
             % endif
          % else:
             ${h.text(prefix + '.value', inst.value, class_="datainp", disabled=disabled, ronly=not c.is_tr and not c.is_edit)}        
             % if disabled:
             ${h.hidden(prefix + '.value', inst.value)}
             % endif
          % endif
        
        % endif
      </th>
      % endfor
      % endfor
      <th></th>
    </tr>
</%def>

<%def name="edit_data_row(baseprefix, cnt, item, item_tr)">
  <%
    rowprefix = '%s%s' % (baseprefix, cnt)
    cols = item.col or []
    if c.lang:
       cols_tr = item_tr.col or []
    hcols = c.ggc.header.col
  %>
<tr class="datarow" data-prefix="${rowprefix}">
  % for ind, dcol in enumerate(c.typedata['cols']):
  <%
    cnt = dcol.get('multi') and c.ggc.datasetcnt or 1
    col = len(cols) > ind and cols[ind] or c.new_item()
    instances = col.inst or []
    if c.lang:
       col_tr = len(cols_tr) > ind and cols_tr[ind] or c.new_item()
       instances_tr = col_tr.inst or []
    hcol = len(hcols) > ind and hcols[ind] or c.new_item()
    hinstances = hcol.inst or []
  
    valuecls = "datainp"
    datatype = dcol.get('datatype')
    if datatype == 'number':
       valuecls += " float"
  %>
  % for ind1 in range(cnt):
  <%
    icol_id = '%s_%s' % (ind, ind1)
    prefix = '%s.col-%d.inst-%d' % (rowprefix, ind, ind1)
    inst = len(instances) > ind1 and instances[ind1] or c.new_item()
    if c.lang:
       inst_tr = len(instances_tr) > ind1 and instances_tr[ind1] or c.new_item()
    hinst = len(hinstances) > ind1 and hinstances[ind1] or c.new_item()
    disabled = dcol.get('optional') and not hinst.active
  %>
  <td class="datacol col-${ind} icol-${icol_id}">
    % if datatype != 'rolesonly':
    ## veeru peamise andmevälja sisestamise koht

          % if c.lang:
             ${h.lang_orig(inst.value)}<br/>
             ${h.lang_tag()}
             ${h.text(prefix + '.value', inst_tr.value, class_=valuecls, disabled=disabled, ronly=not c.is_tr)}
             % if disabled:
             ${h.hidden(prefix + '.value', inst_tr.value)}
             % endif
          % else:
             ${h.text(prefix + '.value', inst.value, class_=valuecls, disabled=disabled, ronly=not c.is_tr and not c.is_edit)}        
             % if disabled:
             ${h.hidden(prefix + '.value', inst.value)}
             % endif
          % endif

    % endif
    <div style="padding-left:20px">
      <table width="100%" border="0">
      % for role in dcol.get('roles') or []:
          <%
            visible = role in hinst.roles
            value = inst.__getattr__(role)
            if c.lang:
               value_tr = inst_tr.__getattr__(role)
            name = '%s.%s' % (prefix, role)
            rolecls = 'roleinp'
            if role in ('interval', 'data'):
               rolecls += ' float'
               wide = False
               size = 8
            else:
               wide = True
               size = None
            ronly = not c.is_tr and not c.is_edit
            %>
            <tr class="roles_${role}" style="display: ${visible and 'table-row' or 'none'};">
              <td align="right">
                ${role}:
              </td>
              <td>
            % if role in ('certainty','emphasis','scope'):
             ${h.checkbox(name, 1, checked=value, disabled=not visible, class_=rolecls, ronly=ronly)}
            % elif role == 'interval':
            <% if not value: value = ['',''] %>
             ${h.text(name, value[0], disabled=not visible, size=size, wide=wide, class_=rolecls, ronly=ronly)}
             ${h.text(name, value[1], disabled=not visible, size=size, wide=wide, class_=rolecls, ronly=ronly)}
            % elif c.lang and role != 'data':
             ${h.lang_orig(value)}<br/>
             ${h.lang_tag()}
             ${h.text(name, value_tr, disabled=not visible, size=size, wide=wide, class_=rolecls, ronly=ronly)}
            % else:
              ${h.text(name, value, disabled=not visible, size=size, wide=wide, class_=rolecls, ronly=ronly)}
            % endif
              </td>
            </tr>
      % endfor
      </table>
    </div>
  </td>
  % endfor
  % endfor
  <td>
    % if c.is_edit:
    ${h.grid_remove()}
    % endif
  </td>
</tr>
</%def>

<%def name="draw_js(alamtyyp)">
<%
  charttype = alamtyyp.split('.')[0]
%>
function draw_chart_arg_${c.block.id}(rows, options)
{
## diagrammi joonistamine andmejadast
% if c.is_sp_edit:
  console.log(JSON.stringify(rows));
% endif
  var data = google.visualization.arrayToDataTable(rows);
  var chart = new google.visualization.${charttype}(document.getElementById('chart_${c.block.id}'));
  chart.draw(data, options);
% if c.is_sp_edit and charttype not in ('Map', 'GeoChart'):
  $('input[name="png_file"]').val(chart.getImageURI());
% endif
}
function draw_chart_${c.block.id}()
{
## diagrammi joonistamine andmebaasi põhjal (lahendaja vaates või kui koostaja sisuploki avab)
% if c.block.sisuvaade:
## var rows, options
${c.block.tran(c.lang).sisuvaade}
draw_chart_arg_${c.block.id}(rows, options);
% endif
}
</%def>

<%def name="block_view_js()">
${self.draw_js(c.block.alamtyyp)}
google.charts.setOnLoadCallback(draw_chart_${c.block.id});
</%def>

<%def name="block_edit_js()">

% if c.multi_col != '':
  function onchange_datasetcnt()
  {
    ## lisatakse/eemaldatakse andmehulkade veerge
    var cnt = parseInt($('select[name="ggc.datasetcnt"]').val());

    $('table#datatable tr').each(function(ind, tr){
        var col_cls = 'col-${c.multi_col}';
        var tds = $(tr).find('th,td').filter('.' + col_cls);
        var last_td = tds.last();

        ## vajadusel lisame veerge juurde viimast veergu kloonides
        for(var n=tds.length; n < cnt; n++)
          {
             var td = last_td.clone();
             ## asendame prefixi
             td.data("icol", "${c.multi_col}_" + n);
             td.removeClass('i' + col_cls + '_' + (n-1)).addClass('i' + col_cls + '_' + n);
             td.find('input').each(function(n1, inp){
                var name = $(inp).attr('name');
                name = name.replace(/\.inst-\d+\./gi, ".inst-" + n + ".");
                $(inp).attr('name', name);                  
             });
             ## asendame veeru pealkirjas veeru järjekorranumbri
             var title_temp = td.find('span.coltitle-template').text();                     
             td.find('span.coltitle').text(title_temp.replace('%d', n+1));
             td.insertAfter(last_td);
             last_td = td;
          }
        ## kustutame liigsed veerud                        
        for(var n=tds.length; n >= cnt; n--)
          {
             tds.eq(n).remove();
          }
    });
  }
% endif
    
  function gen_chart()
  {
    ## sisestustabelist genereeritakse diagrammi andmete jada
    var ftyyp = $('#f_alamtyyp');
    if(ftyyp.val() != "${c.item.alamtyyp}")
    {
       ## vale diagrammi tyyp, vaja lehte uuendada
       ftyyp.change();
       return;
    }
    var rows = [];
    var tr1 = $('table#datatable>thead>tr.metadata');
    var tr2 = $('table#datatable>thead>tr.datarow');    

    ## koostame tabeli esimese rea
    var cols = [];
    $.each(tr2.find('th.datacol'), function(n2, td){
       var inp = $(td).find('input.datainp:enabled');
       if(inp.length > 0)
          {
            ## veeru pealkiri
            var value = inp.val();
            if(inp.hasClass('float')) value = parseFloat(value.replace(',','.'));
            cols.push(value);
          }          
       ## lisame veeru rollide veerud
       var roles = tr1.find('th.headcol').eq(n2).find('input[type="checkbox"].role:checked');
       roles.each(function(n3, fld){
                var roleval = $(fld).val();
                value = {role: roleval};
                cols.push(value);
                if(roleval == 'interval')
                {
                   ## intervall koosneb kahest veerust
                   cols.push(value);
                }
       });
    });
    rows.push(cols);

    ## lisame tabeli andmeread
    $.each($('table#datatable>tbody>tr.datarow'), function(n1, tr){
       var cols = [];
       $.each($(tr).find('td.datacol'), function(n2, td){
          var inps = $(td).find('input.datainp:enabled,input.roleinp:enabled');
          inps.each(function()
          {
            var inp = $(this);
            if(inp.attr('type') == 'checkbox')
            {
              var value = inp.prop('checked');
            }
            else
            {
              var value = inp.val();
              if(inp.hasClass('float')) value = parseFloat(value.replace(',','.'));
            }
            cols.push(value);
          });
       });
       rows.push(cols);
    });
    var options = {};
    var s_options = $('textarea[name="ggc.options"]').val();
  % if c.is_tr:
    if(s_options=='') s_options = $('pre#options').text();
  % endif
    if(s_options)
    {
       try{
         options = JSON.parse(s_options);
       } catch(err) {
         $('span#options_err').text(err.message);
         return;
       } 
    }
    var width = parseInt($('input[name="mo.laius"]').val());
    if(width != NaN) options['width'] = width;
    var height = parseInt($('input[name="mo.korgus"]').val());
    if(height != NaN) options['height'] = height;    
       
##      title : 'Monthly Coffee Production by Country',
##      vAxis: {title: 'Cups'},
##      hAxis: {title: 'Month'},
##      seriesType: 'bars',
##      series: {5: {type: 'line'}}
##    };

    $('#f_sisuvaade').val('var rows=' + JSON.stringify(rows) +';\nvar options=' + JSON.stringify(options) + ';');
    draw_chart_arg_${c.block.id}(rows, options);
  }

  function check_lastrow()
  {
    ## peale tabelisse uue rea lisamist kontrollime, et aktiivsus vastaks päisele
    var tr = $('table#datatable>tbody>tr').last();
    $('input[type="checkbox"].active').each(function(ind, fld){
        onchange_active(fld, tr);
    });

    ## kontrollime, et rollid vastaks päisele
    $('input[type="checkbox"].role').each(function(ind, fld){
       onchange_role(fld, tr);
    });
  }

  function addrow()
  {
    ## andmetabelisse lisatakse uus rida
    grid_addrow('datatable',null,null,true);
    check_lastrow();
  }
      
  function onchange_role(fld, tr)
  {
  ## kuvame või peidame rolli väljad
  ## fld - rolli märkeruut (.role)
    var disabled = !fld.checked;
    var th = $(fld).closest('th.headcol');
    var icol_id = th.data('icol');
    var role = $(fld).val();
  console.log('icol_id='+icol_id+', role='+role);
  
    if(!disabled && (role == 'annotationText'))
    {
      ## annotationText eeldab, et on valitud annotation
      var role1 = th.find('.role[value="annotation"]');
      if(!role1.prop('checked'))
      {
         role1.prop('checked', true).change();
      }
    }
    if(!tr) tr = $('table#datatable');
    var td = tr.find('td.datacol.icol-' + icol_id);

    var div = td.find('.roles_' + role);
    div.toggle(!disabled);
    div.find('input').prop('disabled', disabled);
  }

  function onchange_active(fld, tr)
  {
    ## aktiveerime/deaktiveerime veeru väljad
    var disabled = !fld.checked;
    var th = $(fld).closest('th.headcol');
    if((tr==null) && fld.checked)
    {
      ## kui ka eelmine veerg on mittekohustuslik, siis
      ## selle veeru aktiveerimine eeldab, et ka eelmine oleks aktiivne
      var prev_active = th.prev().find('.active');
      if((prev_active.length > 0) && !prev_active.prop('checked'))
      {
         prev_active.prop('checked', true);
         onchange_active(prev_active[0], tr);
      }
    }
    var icol_id = th.data('icol');
    if(!tr) tr = $('table#datatable');
    var inps = tr.find('.icol-' + icol_id + ' input.datainp');

    inps.each(function(n, inp){
       inp = $(inp);
       inp.prop('disabled', disabled);
       ## disabled korral loome samanimelise hidden välja, et andmed salvestada saaks
       var name = inp.attr('name');
       var hidden = inp.siblings('input[name="' + name + '"][type="hidden"]');
       if(!disabled)
       {
          hidden.remove();
       }
       else if(hidden.length==0)
       {
          $('<input name="' + name + '" type="hidden"/>').val(inp.val()).insertAfter(inp);
       }
    });
  }

  function onchange_alamtyyp()
  {
      ## diagrammi tyybi muutmisel genereerime serveris vormi uuesti
      ## vastavalt valitud diagrammityybile
      var form = $('form#form_save');
      var data = $(form).serialize();
      var action = $(form).attr('action');
      ##% if c.item.id:
      ##var action = "${h.url_current('edit', id=c.item.id)}";
      ##% else:
      ##var action = "${h.url_current('new')}";
      ##% endif
      data += '&sub=change';
      dialog_load(action, data, 'post', $(form).parent());
  }
  
  ${self.draw_js(c.item.alamtyyp)}

  % if c.run_generate:
  google.charts.setOnLoadCallback(gen_chart);
  dirty = true;
  % else:
  google.charts.setOnLoadCallback(draw_chart_${c.block.id});
  % endif
</%def>

