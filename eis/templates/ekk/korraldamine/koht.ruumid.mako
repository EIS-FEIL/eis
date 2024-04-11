## Soorituskoha testiruumide valimine ja nende algusaegade määramine
<%
   c.vastvorm = c.toimumisaeg.testiosa.vastvorm_kood
   c.opt_toimumispaevad = c.toimumisaeg.get_toimumispaevad_opt(kell=c.toimumisaeg.kell_valik)
   c.opt_toimumispaevad_valim = c.toimumisaeg.get_toimumispaevad_opt(kell=c.toimumisaeg.kell_valik, valim=True)  
   c.algusajad = {}
   c.loppajad = {}
   for tpv in c.toimumisaeg.toimumispaevad:
      if not c.default_time:
         c.default_time = tpv.aeg
      c.algusajad[tpv.id] = h.str_time_from_datetime(tpv.aeg)
      if tpv.lopp:
         c.loppajad[tpv.id] = h.str_time_from_datetime(tpv.lopp)
   c.testiruumid = list(c.testikoht.testiruumid)
%>
<script>
var kellad = {
% for key, value in c.algusajad.items():
'${key}':'${value != "00.00" and value or ""}',
% endfor
'':''
};
var loppajad = {
% for key, value in c.loppajad.items():
'${key}':'${value}',
% endfor
'':''
};
</script>

<table  class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th(_("Ruum"))}
      ${h.th(_("Kohtade arv"))}
      ${h.th(_("E-kohtade arv"))}
      <th>
        <table width="100%" >
          % if c.toimumisaeg.kell_valik:
          <col width="80%"/>
          <col width="20%"/>
          % else:
          <col width="40%"/>
          <col width="40%"/>
          <col width="20%"/>
          % endif
          <thead>
            <tr>
              <th>${_("Kuupäev")}</th>
              % if not c.toimumisaeg.kell_valik:
              <th>${_("Aeg")}</th>
              % endif
              <th>${_("Sooritajate arv")}</th>
              <th></th>
            </tr>
          </thead>
        </table>
      </th>
    </tr>
  </thead>
  <tbody>
    ## määramata ruumiga ja ajutised ruumid
    <%
      cnt = -1
      ruumid = list(c.koht.ruumid)
      testiruumid = list(c.testikoht.testiruumid)
      r_testiruumid = [tr for tr in testiruumid if tr.ruum_id == None] 
    %>
    % if not c.toimumisaeg.ruum_noutud or r_testiruumid:
    <% cnt += 1 %>
    ${self.row_ruum(cnt, None, r_testiruumid, ruumid)}
    % endif
    ## püsiandmetes olevad ruumid
    % for r in ruumid:
       <%
         cnt += 1
         r_testiruumid = [tr for tr in testiruumid if tr.ruum_id == r.id]
       %>
        ${self.row_ruum(cnt, r, r_testiruumid)}
    % endfor
  </tbody>
</table>

<%def name="row_ruum(cnt, r, r_testiruumid, ruumid=None)">
        <tr>       
          <td>
            <% 
               prefix = 'ruum-%d' % cnt 
               ruum_id = r and r.id or None
               grid_id = ruum_id or 0
               possible = False
               if r and not r.ptestikohti and c.vastvorm == const.VASTVORM_KP:
                  err = _("Ruumis pole p-testikohti")
               elif r and not r.etestikohti and c.vastvorm in (const.VASTVORM_KE, const.VASTVORM_SE):
                  err = _("Ruumis pole e-testikohti")
               else:
                  possible = True
                  err = None
            %>
            % if r:
            ${r.tahis}
            % elif r_testiruumid:
            <%
              opt_ruumid = [('', _("Määramata"))] + [(r1.id, r1.tahis) for r1 in ruumid] 
            %>
            ${h.select('%s.uus_ruum_id' % prefix, '', opt_ruumid)}
            % else:
            ${_("Määramata")}
            % endif
          </td>         
          % if r:
          <td>${r.ptestikohti}</td>
          <td>${r.etestikohti}</td>
          % elif c.toimumisaeg.ruum_noutud:
          <td colspan="2"></td>
          % else:
          <td>${c.koht.ptestikohti}</td>
          <td>${c.koht.etestikohti}</td>
          % endif
          <td>
            ${err}
            ${self.testiruumid('%s.tr' % prefix, ruum_id, r_testiruumid, possible)}
            ${h.hidden('%s.id' % prefix, ruum_id)}
          </td>
        </tr>
</%def>

<%def name="testiruumid(prefix, ruum_id, testiruumid, possible)">
<% 
   grid_id = ruum_id or 0
   cnt = 0
%>
% if len(testiruumid) or c.is_edit and possible:
<table width="100%" class="tablesorter"
       id="choicetbl_${grid_id}">
  % if c.toimumisaeg.kell_valik:
  <col width="80%"/>
  <col width="20%"/>
  % else:
  <col width="40%"/>
  <col width="40%"/>
  <col width="20%"/>
  % endif
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        <%
           # et saaks sooritajate arvu, võtame kirje andmebaasist
           item_id = request.params.get('%s-%s.id' % (prefix, cnt))
           item = item_id and model.Testiruum.get(item_id)
        %>
        ${self.testiruum(item or c.new_item(), prefix, '-%s' % cnt, grid_id)}
  %   endfor
  % else:
## tavaline kuva
  <%  cnt = 0 %>
  %   for testiruum in testiruumid:
        ${self.testiruum(testiruum, prefix, '-%s' % cnt, grid_id)}
        <% cnt += 1 %>
  %   endfor
  % endif
  </tbody>
</table>
% endif

% if c.is_edit and possible:
<%
  voib_korduda = c.toimumisaeg.ruum_voib_korduda
  bcls = not voib_korduda and cnt >= len(c.opt_toimumispaevad) and 'd-none' or ''
  bid = f'lisa_{grid_id}'
  if not voib_korduda:
     onclick = f"grid_addrow('choicetbl_{grid_id}');toggle_table({grid_id});"
  else:
     onclick = f"grid_addrow('choicetbl_{grid_id}');"
 
%>
${h.button(_("Lisa"), onclick=onclick, id=bid, class_=bcls, level=2, mdicls='mdi-plus')}
<div id="sample_choicetbl_${grid_id}" class="invisible">
              <!--
                  ${self.testiruum(c.new_item(kood='__kood__'), prefix, '__cnt__', grid_id)}
                -->
</div>
% endif
</%def>

<%def name="testiruum(testiruum, baseprefix, cnt, grid_id)">
## Ühe ruumi rida tabelis
<%
  prefix = '%s%s' % (baseprefix, cnt)
%>
    <tr>
      <td>
        % if testiruum and testiruum.id and testiruum.fix_toimumispaev():
        ${h.select('tpv_id_ro', testiruum.toimumispaev_id, c.opt_toimumispaevad, ronly=True)}
        ${h.hidden('%s.toimumispaev_id' % prefix, testiruum.toimumispaev_id)}
        % else:
        <%
          # kas on valimi sooritajaid?
          q = (model.Session.query(model.sa.func.count(model.Sooritus.id))
               .filter(model.Sooritus.testiruum_id==testiruum.id)
               .join(model.Sooritus.sooritaja)
               .filter(model.Sooritaja.valimis==True))
          on_valim = testiruum.id and q.scalar() > 0
          if on_valim:
              # kuvame valikus ainult valimi ajad + ruumi praegune aeg
              tpv_valim = [r[0] for r in c.opt_toimumispaevad_valim]
              opt_tpv = [r for r in c.opt_toimumispaevad if r[0] in tpv_valim or r[0] == testiruum.toimumispaev_id]
          else:
              opt_tpv = c.opt_toimumispaevad
        %>
        ${h.select('%s.toimumispaev_id' % prefix, 
        testiruum and testiruum.toimumispaev_id, opt_tpv, 
        onchange=not c.toimumisaeg.ruum_voib_korduda and "ch_tpaev(this);" or "ch_kell(this);", wide=False, class_='truum')}
        % endif
        <%
          algus = testiruum and testiruum.algus or c.default_time
          lopp = testiruum and testiruum.lopp or ''
        %>
      </td>
      % if not c.toimumisaeg.kell_valik:
      <td>
        ${h.time('%s.kell' % prefix, algus, class_='tkell', wide=False)}
        % if c.loppajad:
        -
        ${h.time('%s.t_lopp' % prefix, lopp, class_='tlopp', wide=False)}
        % endif
      </td>
      % endif

      <td>
      % if testiruum.id:
        ${testiruum.sooritajate_arv}
      % endif
      </td>

      <td width="20px">
        % if c.is_edit and not testiruum.sooritajate_arv:
        % if c.toimumisaeg.ruum_voib_korduda:
        ${h.grid_remove()}
        % else:
        ${h.grid_remove("toggle_table(%s);" % grid_id)}
        % endif
        % endif
        ${h.hidden('%s.id' % prefix, testiruum.id)}
      </td>
    </tr>
</%def>

<script> 
% if not c.toimumisaeg.ruum_voib_korduda:
function toggle_table(grid_id)
{
  var t = $('table#choicetbl_' + grid_id);
  $('input#lisa_' + grid_id).toggleClass('invisible', (t.children('tbody').children('tr').length>=${len(c.opt_toimumispaevad)}));
  disable_used_id(t);
}
function ch_tpaev(fld)
{
   ch_kell(fld);
   disable_used_id($(fld).closest('table'));
}
function disable_used_id(tbl)
{
  tbl.find('select.truum option').removeProp('disabled');
  var selected = [];
  tbl.find('select.truum option:selected').each(function(){
    var o = $(this);
    ## kui on varasemal väljal sama valitud, siis liigutame siinset valikut edasi (esineb uue rea korral)
    while(selected.indexOf(o.val()) > -1)
    {
      o = o.next('option');
      if(o.length == 0) break;
      o.prop('selected', true);
    }
    selected.push(o.val());
    tbl.find('select.truum option[value="'+o.val()+'"]:not(:selected)').prop('disabled', true);
  });
}
% endif
function ch_kell(fld)
{
   var tr = $(fld).closest('tr');
   tr.find('input.tkell').val(kellad[$(fld).val()]);
   tr.find('input.tlopp').val(loppajad[$(fld).val()] || '');
}
</script>
