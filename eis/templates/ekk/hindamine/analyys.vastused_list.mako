## Vastuste statistika

% if c.item:
## yhe ylesande statistika
<div class="row">
  <div class="col-12 col-lg-3 bg-gray-50 text-truncate">
    ${self.ylesanded_index()}
  </div>
  <div id="itemdiv" class="col-12 col-lg-9">
    <%include file="analyys.vastus.mako"/>
  </div>
</div>

% else:
## ylesannete loetelu

% if c.app_ekk:
${self.resp_filter()}
% endif

<div class="d-flex flex-wrap">
  ${self.ylesanded_stat_index()}
  % if not c.testiosa_id or not c.toimumisaeg or int(c.testiosa_id) == c.testiosa.id:
  ${self.kysimused_index()}
  % endif
</div>
% endif

<%def name="ylesanded_index()">
<table class="table table-striped">
  <caption>${_("Ülesanded")}</caption>
  <tbody>
  % for items, osa_id, komplekt_id in c.data.values():
  % for rcd in items:
  <%
    ylesanne, vy, ty, yst = rcd
    active = c.item and c.item.id == vy.id
  %>
    % if active:
  <tr class="selected">
    % else:
  <tr>
    % endif
    <td>
      ${ty.tahis}
      <!-- y${ylesanne.id} ty${ty.id} vy${vy.id} yst${yst and yst.id}-->
    </td>
    <td class="${active and 'font-weight-bold' or ''}">
      ${h.link_to(ylesanne.nimi,h.url_current('show', id=vy.id, ryhmas=c.ryhmas, komplektis=c.komplektis), level=0)}
    </td>
  </tr>
  % endfor
  % endfor
  </tbody>
</table>
</%def>


<%def name="ylesanded_stat_index()">
<div class="mr-1">
  <div class="d-flex flex-wrap my-2">
    <h2 class="h3">${_("Ülesanded")}</h2>
    % if c.app_ekk:
      ${h.submit(_("Ülesannete statistika (Excel)"), id='csv_y', level=2, class_="ml-3")}
    % endif
  </div>
  % for items, osa_id, komplekt_id in c.data.values():
    % if len(c.osad) > 1:
    <div>Testiosa <b>${c.osad[osa_id]}</b>, komplekt <b>${c.komplektid[komplekt_id]}</b></div>
    % elif len(c.komplektid) > 1:
    <div>Komplekt <b>${c.komplektid[komplekt_id]}</b></div>
    % endif
    ${self.ylesanded_stat_index_komplekt(items)}
  % endfor
  ${self.ylesanded_stat_index_js()}
</div>
</%def>

<%def name="ylesanded_stat_index_js()">
<script>
function calc_mean(fld)
{
  var tbl = $(fld).closest('table.yl-index');
  var in_use = tbl.find('input.vy-id:checked');
  var total_mean = 0;
  var total_max = 0;

  for(var n=0; n<in_use.length; n++)
  {
     var tr = in_use.eq(n).closest('tr');
     var sy_mean = tr.find('input.vy-id').attr('data-kesk');
     if(sy_mean){                           
        var y_mean = parseFloat(sy_mean.replace(',','.'));
        if(!isNaN(y_mean)){  
          var y_max = parseFloat(tr.find('td.y-max').text().replace(',','.'));
          total_mean += y_mean;
          total_max += y_max;
       }
     }
  }
  if((total_max == 0) || isNaN(total_max))
  {
     tbl.find('.total-mean').text('');
     tbl.find('.total-max').text('');
  }
  else
  {
     var perc = total_mean*100/total_max;
     tbl.find('.total-mean').text(total_mean.toFixed(3) + ' (' + perc.toFixed(3) + '%)');
     tbl.find('.total-max').text(total_max);
  }
}
function checkvyall(fld)
{
   $(fld).closest('table.yl-index').find('input.vy-id').prop('checked', fld.checked);
   calc_mean(fld);                             
}
$('input.vy-id').click(function(){ calc_mean(this); });
$('input.vyall').click(function(){ checkvyall(this); });
</script>
</%def>

<%def name="ylesanded_stat_index_komplekt(items)">
  <table class="table table-striped yl-index">
  <thead>
    <tr>
      <th rowspan="2">${_("Jrk")}</th>
      <th colspan="2">${_("Toorpunktid")}</th>
      <th colspan="2">${_("Hindepallid")}</th>
      <th rowspan="2">${_("Keskmine lahendusprotsent")}
        <span class="helpable" id="y_lahendatavus"></span>
      </th>
      ${h.th(_("Rit"), rowspan=2)}
      ${h.th(_("Rir"), rowspan=2)}
      % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
      <th colspan="3">${_("Aeg")}</th>
      % endif
      <th rowspan="2">${_("Ülesande nimetus")}</th>
    </tr>
    <tr>
      ${h.th(_("Keskmine"))}
      ${h.th(_("Max"))}
      ${h.th(_("Keskmine"))}
      ${h.th(_("Max"))}
      % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
      ${h.th(_("Keskmine"))}
      ${h.th(_("Min"))}
      ${h.th(_("Max"))}
      % endif
    </tr>
  </thead>
  <%
    total_mean = total_max = 0
    prev_ty_id = None
  %>
  <tbody>
  % for rcd in items:
  <% 
     ylesanne, vy, ty, yst = rcd
     komplekt_id = vy.komplekt_id
     if yst:
        keskmine_p = yst.keskmine and yst.keskmine * (vy.koefitsient or 1) or 0
        total_mean += keskmine_p
        if ty.max_pallid is None:
           total_max = None
        elif total_max is not None:
           total_max += ty.max_pallid
     else:
        keskmine_p = None
  %>
  <tr>
    <td>
      ${ty.tahis}
      <!-- y${ylesanne.id} vy${vy.id} yst${yst and yst.id} -->
    </td>
    <td>${h.fstr(yst and yst.keskmine)}</td>
    <td>${h.fstr(ylesanne.max_pallid)}</td>
    <td>
      ${h.checkbox('vy_id', vy.id, checked=True, class_="vy-id mr-0", data_kesk=keskmine_p)}
      ${h.fstr(keskmine_p)}
    </td>
    <td class="y-max">${h.fstr(ty.max_pallid)}</td>
    <td>
      % if yst and yst.lahendatavus is not None:
      ${h.fstr(yst.lahendatavus)}%
      % endif
    </td>
    <td>
      % if yst:
      ${h.fstr(yst.rit, 2)}
      % endif
    </td>
    <td>
      % if yst:
      ${h.fstr(yst.rir, 2)}
      % endif
    </td>
    % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
    <td>${h.str_from_time_sec(yst and yst.aeg_avg)}</td>
    <td>${h.str_from_time_sec(yst and yst.aeg_min)}</td>
    <td>${h.str_from_time_sec(yst and yst.aeg_max)}</td>
    % endif
    <td>
      % if not c.toimumisaeg or ty.testiosa_id == c.testiosa.id:
      ${h.link_to(ylesanne.nimi,h.url_current('show', id=vy.id, komplekt_id=komplekt_id, komplektis=c.komplektis),
      class_=c.fblinks and 'fblink' or '', level=0)}
      % else:
      ${ylesanne.nimi}
      % endif
    </td>
  </tr>
  % endfor
  </tbody>

  <tfoot>
    <tr>
      <th colspan="3">${_("Kokku")}</th>
      <th>
        ${h.checkbox1('vyall', 1, class_="vyall")}
        <span class="total-mean">
        % if total_max:
        ${h.fstr(total_mean)} (${h.fstr(total_mean*100./total_max)}%)
        % endif
        </span>
      </th>
      <th class="total-max">${h.fstr(total_max)}</th>
      <th colspan="7">
      </th>
    </tr>
  </tfoot>

 </table>
</%def>

<%def name="resp_filter()">
<%
  if c.toimumisaeg:
      osa_id = c.testiosa_id or c.testiosa.id
      ta_id = c.toimumisaeg.id
  else:
      osa_id = c.testiosa_id or -1
      ta_id = None
  on_stat = model.Statvastus_t_seis.on_arvutatud(osa_id, ta_id)
  qts = (model.Session.query(model.Nptagasiside.id)
         .join(model.Nptagasiside.normipunkt)
         .join(model.Normipunkt.testiosa)
         .filter(model.Testiosa.test_id==c.test.id))
  on_ts = qts.first() is not None
%>
% if not on_stat:
${h.alert_notice(_("Statistika on arvutamata!"), False)}
% elif c.user.has_permission('vastustevaljavote', const.BT_SHOW, obj=c.test):
<div class="d-flex flex-wrap my-2">
  <div class="mr-4">
    <h2 class="h3">${_("Andmete väljavõte")}</h2>
  </div>
  <div class="mr-4 flex-grow-1" id="naita">
    ${h.hidden('naita', 1)}
    ${h.checkbox('ajakulu', 1, checked=c.ajakulu or not c.naita, label=_("Ajakulu"))}
    ${h.checkbox('ylp', 1, checked=c.ylp or not c.naita, label=_("Ülesannete punktid"))}
    ${h.checkbox('kysv', 1, checked=c.kysv or not c.naita, label=_("Vastused"))}
    ${h.checkbox('kysp', 1, checked=c.kysp or not c.naita, label=_("Küsimuste punktid"))}
    ${h.checkbox('oige', 1, checked=c.oige or not c.naita, label=_("Vastuste õigsus"))}
    % if on_ts:
    ${h.checkbox('tsopil', 1, checked=c.tsopil or not c.naita, label=_("Õpilase tagasiside"))}
    ${h.checkbox('tsopet', 1, checked=c.tsopet or not c.naita, label=_("Õpetaja tagasiside"))}
    % endif
  </div>
  <div>
    ${h.submit(_("Andmed (Excel)"), id='csv_v', level=2)}
  </div>
</div>
<div class="mb-3">
  ${_("Väljavõte moodustatakse allpool märgitud ülesannete andmetest.")}
</div>
% endif
</%def>

<%def name="kysimused_index()">
<div>
  <div class="d-flex flex-wrap my-2">
    <h2 class="h3">${_("Küsimused")}</h2>
    % if c.app_ekk:
    ${h.submit(_("Küsimuste statistika (Excel)"), id='csv_k', level=2, class_="ml-3")}
    % endif
  </div>

  <table class="table table-striped" >
  <thead>
    <tr>
      ${h.th(_("Ülesanne"))}
      ${h.th(_("Küsimus"))}
      ${h.th(_("Keskmine lahendusprotsent"))}
      % if c.app_ekk:
      ${h.th(_("Rit"))}
      ${h.th(_("Rir"))}
      % endif
    </tr>
  </thead>
  <tbody>
  <%
    analyys_eraldi = c.toimumisaeg and c.toimumisaeg.testimiskord.analyys_eraldi
    # näitame selle testiosa kysimusi
    items = []
    for rcd in c.data.values():
        k_items, osa_id, komplekt_id = rcd
        if not c.toimumisaeg or osa_id == c.testiosa.id:
           items.extend(k_items)
  %>
  % for n, rcd in enumerate(items):
  <% 
    ylesanne, vy, ty, yst = rcd
    vy_id = c.komplektis and vy.id or None
  %>
    % for sp in ylesanne.sisuplokid:
      % if sp.is_interaction:
        % for kysimus in sp.kysimused:
##          % if kysimus.tulemus_id or (sp.tyyp != const.INTER_MATCH2 and sp.tyyp != const.INTER_MATCH3):
          % if kysimus.tulemus_id and kysimus.kood:
             ## sobitamise korral on 2-3 kysimust, aga vastused on yhe kysimuse all, jätame muud välja
          <%
             if c.toimumisaeg and analyys_eraldi:
                kst = c.toimumisaeg.get_kysimusestatistika(kysimus.id, vy_id)
             elif c.toimumisaeg:
                kst = ty.testiosa.get_kysimusestatistika(kysimus.id, vy_id, True)
             else:
                kst = ty.testiosa.get_kysimusestatistika(kysimus.id, vy_id, False)
          %>
          % if kst:
  <tr class="${n % 2 and 'odd' or 'even'}">
    <td>
      ${ty.tahis}
      <!--kst ${kst.id}--></td>
    <td>
      ${h.link_to(kysimus.kood, h.url_current('show', id=vy.id, komplekt_id=c.komplekt_id, komplektis=c.komplektis)+'#stat_'+kysimus.kood,
      class_=c.fblinks and 'fblink' or '', level=0)}
    </td>
    <td>${h.fstr(kst.klahendusprotsent or 0)}%</td>
    % if c.app_ekk:
    <td>${h.fstr(kst.rit, 2)}</td>
    <td>${h.fstr(kst.rir, 2)}</td>
    % endif
  </tr>
          % endif
         % endif
        % endfor
      % endif
    % endfor
  % endfor
  </tbody>
  </table>
</div>  
</%def>
