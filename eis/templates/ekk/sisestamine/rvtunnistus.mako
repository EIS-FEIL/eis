<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvahelise eksami tunnistuse sisestamine")} | ${c.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Rahvusvahelise eksami tunnistuse sisestamine'), h.url('sisestamine_rvtunnistused'))}
${h.crumb('%s %s' % (c.kasutaja.isikukood, c.kasutaja.nimi))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


${h.form_save(c.item.id, autocomplete='off')}
${h.hidden('rveksam_id', c.rveksam.id)}
${h.hidden('kasutaja_id', c.kasutaja.id)}

<h1>${c.rveksam.nimi}</h1>


% if c.sooritajad:
<table width="100%">
  <tr>
    <td width="50%" align="right">Sooritatud test</td>
    <td>
      <%include file="rvtunnistus.sooritajad.mako"/>
    </td>
  </tr>
</table>
<br/>
% else:
${h.hidden('sooritaja_id', '0')}
% endif

<table width="100%" class="form border tbl-sisestamine" cellpadding="4">
  <col width="150px"/>
  <tbody>
    % if c.kasutaja.isikukood:
    <tr>
       <td class="fh">${_("Sooritaja isikukood")}</td>
       <td>${c.kasutaja.isikukood}</td>
    </tr>
    % else:
    <tr>
       <td class="fh">${_("Sooritaja sünniaeg")}</td>
       <td>${h.str_from_date(c.kasutaja.synnikpv)}</td>
    </tr>
    % endif
    <tr>
      <td class="fh">${_("Sooritaja eesnimi")}</td>
      <td>${h.text('t_eesnimi', c.tunnistus.eesnimi, maxlength=30)}</td>
    </tr>
    <tr>
      <td class="fh">${_("Sooritaja perekonnanimi")}</td>
      <td>${h.text('t_perenimi', c.tunnistus.perenimi, maxlength=30)}</td>
    </tr>
  </tbody>
</table>
<br/>

<table width="100%" class="form border tbl-sisestamine" cellpadding="4">
  <col width="150px"/>
  <tbody>

    % if c.rveksam.on_tunnistusenr:
    <tr>
      <td class="fh">${_("Tunnistuse nr")}</td>
      <td colspan=2>${h.text('t_tunnistusenr', c.tunnistus.tunnistusenr, maxlength=30, size=38)}</td>
    </tr>
    % endif

    <tr>
      <td class="fh">${_("Väljastatud")}</td>
      <td colspan=2 nowrap>
        ${h.date_field('t_valjastamisaeg', c.tunnistus.valjastamisaeg)}
      </td>
    </tr>

    % if c.rveksam.on_kehtivusaeg:
    <tr>
      <td class="fh">${_("Kehtib kuni")}</td>
      <td colspan=2 nowrap>
        ${h.date_field('f_kehtib_kuni', c.item.kehtib_kuni)}
      </td>
    </tr>
    % endif

    <tr id="osakokku">
      <td class="fh">
        Tulemus
      </td>

      <% 
         on_vahemikud = len(c.rveksam.rveksamitulemused) 
         on_autom_vahemikud = on_vahemikud
      %>
      % if c.rveksam.on_arvtulemus:
        % if on_vahemikud:
      <td width="120px">
        % else:
      <td>
        % endif
        <%
           vahemikud = []
           for r in c.rveksam.rveksamitulemused:
              vahemikud.append([r.alates, r.kuni, r.id])
              if r.alates is None or r.kuni is None:
                 on_autom_vahemikud = False
           if on_autom_vahemikud:
             onchange = "choose_vahemik(this, %s)" % (str(vahemikud).replace('None','null'))
           else:
             onchange = None
        %>

        ${h.posfloat('f_tulemus', c.item.tulemus, class_='tulemus', 
        minvalue=c.rveksam.alates, maxvalue=c.rveksam.kuni, onchange=onchange)}
        % if c.rveksam.kuni:
        /${h.fstr(c.rveksam.kuni)}
        % endif

        % if c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
        palli
        % elif c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
        protsenti
        % endif
      </td>
      % endif

      % if on_vahemikud:
      <td>
        <% 
           disabled = c.rveksam.on_arvtulemus and on_autom_vahemikud
           field_name = 'f_rveksamitulemus_id'
        %>
        % if disabled:
           ${h.hidden(field_name, c.item.rveksamitulemus_id, class_='vahemikh')}
           <% field_name += '_disabled' %>
        % endif

        % for r in c.rveksam.rveksamitulemused:
        ${h.radio(field_name, r.id, checkedif=c.item.rveksamitulemus_id, 
        label=r.tahis, class_='vahemik', disabled=disabled)}
           % if r.alates or r.kuni:
            ${h.fstr(r.alates)}-${h.fstr(r.kuni)}
           % endif
           % if r.tahis != r.keeletase_kood:
           ${r.keeletase_kood}
           % endif
        % endfor
      </td>
      % endif

    </tr>


    <tr>
      <td class="fh"></td>
      <td colspan=2>
        ${h.checkbox('f_arvest_lopetamisel', 1, checked=c.item.arvest_lopetamisel,
        label=_('Arvestatakse lõpetamise tingimusena'))}
      </td>
    </tr>

  </tbody>
</table>
<br/>

% if len(c.rveksam.rvosaoskused):
## and c.rveksam.on_osaoskused_tunnistusel:
<table width="100%" class="form border tbl-sisestamine" cellpadding="4">
  <caption>
  % if c.rveksam.on_osaoskused_tunnistusel and c.rveksam.on_osaoskused_sooritusteatel:
  ${_("Tunnistusel ja sooritusteatel märgitud osaoskused")}
  % elif c.rveksam.on_osaoskused_tunnistusel:
  ${_("Tunnistusel märgitud osaoskused")}
  % elif c.rveksam.on_osaoskused_sooritusteatel:
  ${_("Sooritusteatel märgitud osaoskused")}
  % else:
  ${_("Osaoskused")}
  % endif
  </caption>
  <col width="150px"/>
  <tbody>
    % for n, osa in enumerate(c.rveksam.rvosaoskused):
    <% 
       prefix = 'osa-%d' % n 
       rvs = c.item.get_rvsooritus(osa.id) or c.new_item()
       on_vahemikud = len(osa.rvosatulemused)
       on_autom_vahemikud = on_vahemikud

    %>
    <tr id="osa${osa.id}">
       <td class="fh">${osa.nimi}
         ${h.hidden('%s.rvosaoskus_id' % prefix, osa.id)}
       </td>

      % if c.rveksam.on_arvtulemus:
       % if on_vahemikud or c.rveksam.on_osaoskused_jahei:
      <td width="120px">
       % else:
      <td>
       % endif
        <%
           vahemikud = []
           for r in osa.rvosatulemused:
              vahemikud.append([r.alates, r.kuni, r.id])
              if r.alates is None or r.kuni is None:
                 on_autom_vahemikud = False
           if on_autom_vahemikud:
              onchange = "choose_vahemik(this, %s)" % (str(vahemikud).replace('None','null'))
           else:
              onchange = None
        %>
        ${h.posfloat('%s.tulemus' % prefix, rvs.tulemus, class_='tulemus',
        minvalue=osa.alates, maxvalue=osa.kuni, onchange=onchange)}

        % if osa.kuni:
        /${h.fstr(osa.kuni)}
        % endif

        % if c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
        palli
        % elif c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
        protsenti
        % endif
      </td>
      % endif

      % if on_vahemikud:
      <td>
        <% 
           disabled = c.rveksam.on_arvtulemus and on_autom_vahemikud
           field_name = '%s.rvosatulemus_id' % prefix
        %>
        % if disabled:
           ${h.hidden(field_name, rvs.rvosatulemus_id, class_='vahemikh')}
           <% field_name += '_disabled' %>
        % endif

        % for r in osa.rvosatulemused:
        ${h.radio(field_name, r.id, checkedif=rvs.rvosatulemus_id, 
        label=r.tahis, class_='vahemik', disabled=disabled)}
           % if r.alates or r.kuni:
            ${h.fstr(r.alates)}-${h.fstr(r.kuni)}
           % endif
        % endfor
      </td>
      % endif

      % if c.rveksam.on_osaoskused_jahei:
      <td>
        ${_("Vastab tasemele: ")} ${h.checkbox('%s.on_labinud' % prefix, 1, checked=rvs.on_labinud)}
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
<br/>
% endif

${h.submit(_('Salvesta'))}
% if c.item.id:
${h.btn_to(_('Lisa uus tunnistus'), h.url('sisestamine_new_rvtunnistus', rveksam_id=c.rveksam.id, kasutaja_id=c.kasutaja.id))}
${h.btn_remove()}
% endif
${h.end_form()}

<script>
function choose_vahemik(fld, vahemikud)
{
     var value = Number($(fld).val().replace(',','.'));
     if(value != NaN)
     {
       var row = $(fld).closest('tr');
       for(var i=0; i<vahemikud.length; i++)
          {
             var li = vahemikud[i];
             var d = .00001
             if(li[0] == null || li[0] <= value + d)
             if(li[1] == null || value - d <= li[1])
             {
                row.find('input.vahemik[value=' + li[2] + ']').prop('checked', true);
                row.find('input.vahemikh').val(li[2]);
                break;
             }
          }
     }
}
</script>
