## Kysimuse statistika, antud vastused ja hindamismaatriks
<%namespace name="choiceutils" file="/sisuplokk/choiceutils.mako"/>
<%include file="/common/message.mako"/>

## kui tullakse maatriksi muutmiselt
<script>dirty=false;</script>

<%
  if c.app_eis and c.user.has_permission('avylesanded', const.BT_UPDATE, obj=c.ylesanne):
      url_mx = h.url('test_analyys_vastused_kysimus_create_maatriksid', test_id=c.test.id, kysimus_id=c.kysimus.id, testiruum_id=c.testiruum_id)
      url_hm_list = h.url('test_analyys_vastused_kysimus_maatriksid', test_id=c.test.id, kysimus_id=c.kysimus.id, testiruum_id=c.testiruum_id)  
  elif c.app_ekk and c.toimumisaeg:
      url_mx = h.url('hindamine_analyys_vastused_kysimus_create_maatriksid', toimumisaeg_id=c.toimumisaeg.id, kysimus_id=c.kysimus.id)
      url_hm_list = h.url('hindamine_analyys_vastused_kysimus_maatriksid', toimumisaeg_id=c.toimumisaeg.id, kysimus_id=c.kysimus.id)
  elif c.app_ekk:
      url_mx = h.url('test_analyys_vastused_kysimus_create_maatriksid', test_id=c.test.id, kysimus_id=c.kysimus.id)
      url_hm_list = h.url('test_analyys_vastused_kysimus_maatriksid', test_id=c.test.id, kysimus_id=c.kysimus.id)
  else:
      url_mx = url_hm_list = None
%>
% if url_mx:
## vastuste standardiseerimie vorm
${h.form_save(c.kysimus.id, url_mx)}
% endif

${h.hidden('kvst_order', request.params.get('kvst_order'))}
<div class="analysis-k" id="stat_${c.kysimus.kood}">
  <% vy_id = c.komplektis and c.valitudylesanne_id or None %>
  <div class="mb-1">
    ${self.kysimus_statistika(c.kysimus, vy_id)}
  </div>
  % if url_hm_list:
  ${self.acc_hindamismaatriks(url_hm_list)}
  % endif           
</div>
% if url_mx:
${h.end_form()}
% endif

<%def name="acc_hindamismaatriks(url_hm_list)">
<% divid = f"hm{c.kysimus.id}" %>
<div class="accordion my-2" id="${divid}_acc">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="heading_${divid}">
      <div class="accordion-title" style="background-color:transparent">
        <button class="btn btn-link collapsed" type="button"
                data-toggle="collapse"
                data-target="#collapsedetail${divid}"
                aria-controls="collapsedetail${divid}"
                aria-expanded="true"
                id="bdetail${divid}"
                data-href="${url_hm_list}"
                style="background-color:transparent">
          <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
            ${_("Hindamismaatriks")}
          </span>
        </button>
      </div>
      <script>
        $('#bdetail${divid}').click(function(){
        var d = $('#detail_content${divid}');
        if(d.text()=='') dialog_load($(this).data('href'), '', 'GET', d);
        toggle_lisahm(this, true);
        });
        % if request.params.get('detail'):
        $(function(){ $('#bdetail${divid}').click(); });
        % endif
      </script>
    </div>
    <div id="collapsedetail${divid}" class="collapse" aria-labelledby="headingdetail${divid}">
      <div class="card-body">
        <div class="content hmxcontent listdiv-hm${c.kysimus.id}" id="detail_content${divid}"></div>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="kysimus_statistika(kysimus, vy_id)">
<%
   if c.toimumisaeg and c.toimumisaeg.testimiskord.analyys_eraldi:
      kst = c.toimumisaeg.get_kysimusestatistika(kysimus.id, vy_id)
   elif c.toimumisaeg:
      kst = c.toimumisaeg.testiosa.get_kysimusestatistika(kysimus.id, vy_id, True)
   elif c.nimekiri_id:
      kst = c.testiosa.get_kysimusestatistika(kysimus.id, vy_id, False, c.nimekiri_id)
   else:
      kst = c.testiosa.get_kysimusestatistika(kysimus.id, vy_id, False)  
%>
<!--k${kysimus.id} kst${kst and kst.id} vy${vy_id} nk${c.nimekiri_id}-->
% if not kst:
${h.alert_notice(_("Statistika arvutamata"))}
% else:
<div>
<% ch = h.colHelper('col-sm-3 text-md-right', 'col-sm-8') %>
<div class="form-group row mb-0">
  ${ch.flb(_("Sooritajate arv"))}
  <div class="${ch.col2}">
    ${kst.vastajate_arv}
      % if kysimus.max_vastus and kysimus.max_vastus > 1:
      (igalt kuni ${kysimus.max_vastus} vastust)
      % endif
      % if kst.test_hinnatud_arv and kst.test_hinnatud_arv != kst.vastajate_arv:
      (${_("test hinnatud {n} sooritajal").format(n=kst.test_hinnatud_arv)})
      % endif
  </div>
</div>
<div class="form-group row mb-0">
  ${ch.flb(_("Vastuste arv"))}
  <div class="${ch.col2}">
    ${kst.vastuste_arv}
  </div>
</div>
<div class="form-group row mb-0">
  ${ch.flb(_("Keskmine lahendusprotsent"))}
  <div class="${ch.col2}">
    ${h.fstr(kst.klahendusprotsent or 0)}%
  </div>
</div>
<div class="form-group row mb-0">
  ${ch.flb(_("Rit"))}
  <div class="${ch.col2}">
    ${h.fstr(kst.rit, 2)}
  </div>
</div>
<div class="form-group row mb-0">
  ${ch.flb(_("Rir"))}
  <div class="${ch.col2}">
    ${h.fstr(kst.rir, 2)}
  </div>
</div>
% if c.is_debug:
<div class="form-group row mb-0">
  ${ch.flb(_("Max toorpunktid"))}
  <div class="${ch.col2}">
    <% tulemus = kysimus.tulemus %>
    ${h.fstr(tulemus.get_max_pallid())}
  </div>
</div>
% endif

${self.kysimus_stat_resp(kysimus, kst)}

</div>

${self.kysimus_stat_point(kysimus, kst)}
% endif
</%def>

<%def name="kysimus_stat_resp(kysimus, kst)">
<%
  if c.app_ekk and c.toimumisaeg:
     from eis.handlers.ekk.hindamine.analyyskvstatistikad import AnalyyskvstatistikadController
  elif c.app_ekk:
     from eis.handlers.ekk.testid.analyyskvstatistikad import AnalyyskvstatistikadController
  else:
     from eis.handlers.avalik.testid.analyyskvstatistikad import AnalyyskvstatistikadController

  ctrl = AnalyyskvstatistikadController(request, True)  
  if c.toimumisaeg:
     ctrl.c.toimumisaeg = c.toimumisaeg
     ctrl.c.toimumisaeg_id = c.toimumisaeg.id
     ctrl.c.test = c.toimumisaeg.testiosa.test
  elif c.nimekiri:
     ctrl.c.nimekiri = c.nimekiri
     ctrl.c.test = c.test
  else:
     ctrl.c.test = c.test
  ctrl.c.kst = kst
  ctrl.c.kvst_order = c.kvst_order
  ctrl.get_items()
  c.is_edit = True
  list_resp = ctrl._showlist()
  is_list = False
  tulemus = kysimus.tulemus
  # vaikimisi antakse uue vastuse eest max pallid
  t_max_p = tulemus.max_pallid
  if t_max_p is None:
     # koostaja pole määranud max p arvu
     t_max_p = 1
  elif not (kysimus.max_vastus and kysimus.max_vastus == 1) and t_max_p > 1:
     # kysimusele on lubatud mitu vastust
     t_max_p = 1
%>
       <div class="listdiv listdiv-${kst.id}">
           % if not len(ctrl.c.kvstatistikad):
           ${h.alert_notice(_("Küsimuse vastuste statistika puudub"))}
           % elif c.sp_tyyp == const.INTER_DRAW:
           ${_("Vastuseid ei kuvata")}
           % else:
           <% is_list = True %>
           ${list_resp.ubody}
           % endif
       </div>
       % if is_list and ctrl.c.can_edit_hm:
           <div class="upd-hm lisahm show-hm mb-2" style="display:none">
            ${_("Punktid:")} ${h.float5("pallid", t_max_p)}           
            ${h.submit_dlg(value=_("Lisa hindamismaatriksisse..."),
            container="$(this).closest('.analysis-k').find('.hmxcontent')",
            onsuccess="function(hmxcontent){ dirty=false; hmxcontent.closest('.collapse').collapse('show');}",
            level=2)}
           </div>
       % endif
</%def>

<%def name="kysimus_stat_point(kysimus, kst)">
           <% 
              tulemus = kysimus.tulemus 
              t_max_pallid = tulemus.get_max_pallid() or 0
           %>
           % if not len(kst.khstatistikad):
           ${h.alert_notice(_("Saadud tulemuste statistika puudub"))}
           % else:
           <h3>${_("Saadud tulemused")}</h3>
           <table width="100%"  class="table table-bordered">
             <thead>
               ${h.th(_("Jrk"))}
               ${h.th(_("Toorpunktid"))}
               ${h.th(_("Punktid"))}
               ${h.th(_("Nulli põhjus"))}
               ${h.th(_("Esinemiste arv"))}
               ${h.th(_("Sagedus"))}
             </thead>
             <tbody>
               % for n_rcd, rcd in enumerate(kst.khstatistikad):
               <%
                  tp = rcd.toorpunktid
                  if rcd.nullipohj_kood:
                     color = '#FFF;'
                  elif tp is not None and (tp > t_max_pallid - .001):
                     # õige, roheline
                     color = '#DBFFE6;'
                  elif tp is not None and (tp > 0):
                     # osaliselt õige, kollane
                     color = '#FCFED5;'
                  else:
                     color = ''
                  td_att = color and f'style="background-color:{color}"' or ''
               %>
               <tr>
                 <td ${td_att} width="25">${n_rcd+1}</td>
                 <td ${td_att}>
                   ${h.fstr(tp)}
                   ##(${h.fstr(t_max_pallid)})
                 </td>
                 <td ${td_att}>
                   ${h.fstr(rcd.pallid)}
                 </td>
                 <td ${td_att}>${rcd.nullipohj_nimi}</td>
                 <td ${td_att}>${rcd.vastuste_arv}</td>
                 <td ${td_att}>
                   % if kst.vastajate_arv:
                   ${h.fstr(rcd.vastuste_arv*100./kst.vastajate_arv)}%
                   % endif
                 </td>
               </tr>
               % endfor
             </tbody>
           </table>
           % endif
</%def>
