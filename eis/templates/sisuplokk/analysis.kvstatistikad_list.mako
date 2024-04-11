<%
  items = c.kvstatistikad
  n_offset = 0
  if c.page and c.page == '0':
      items = c.kvstatistikad.items
  elif c.page:
      n_offset = (int(c.page) - 1) * c.kvstatistikad.items_per_page
%>
% if items:
<h3>${_("Antud vastused")}</h3>
% if c.kvstatistikad_list_url:
${h.pager(c.kvstatistikad, listdiv='.listdiv-%d' % c.kst.id, form='', list_url=c.kvstatistikad_list_url, is_all='kvstall')}
% endif
         <table class="table table-bordered">
             <thead>
% if c.can_edit_hm:
               <th class="upd-hm" width="20"></th>
% endif
               ${h.th(_("Jrk"), width=20)}
               % if c.basetype in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
               ${h.th(_("Kood 1"))}
               ${h.th(_("Kood 2"))}
               % elif c.sp_tyyp == const.INTER_GAP and c.kysimus.seq == 0:
               ${h.th(_("Vastus"))}
               ${h.th(_("Positsioon"))}                              
               % else:
               ${h.th(_("Vastus"))}
               % endif
               ${h.th(_("Selgitus"))}
               ${h.th(_("Esinemiste arv"))}
               ${h.th(_("Sagedus"))}
               ${h.th(_("Õige"))}
               % if c.is_debug:
               ${h.th("kvst ID")}
               % endif
             </thead>
             <tbody>
               <% di_vv = {} %>
               % for n_rcd, rcd in enumerate(items):
               <%
                  if rcd.oige == const.C_OIGE:
                     color = '#DBFFE6;'
                  elif rcd.oige == const.C_OSAOIGE:
                     color = '#FCFED5;'                 
                  elif rcd.oige == const.C_VALE:
                     color = '#FFF2F2;'
                  else:
                     color = '#FFF;'
                  td_att = color and f'style="background-color:{color}"' or ''
               %>
               <tr>
% if c.can_edit_hm:
                 <td class="upd-hm" ${td_att}>
                   % if rcd.tyyp in (const.RTYPE_STRING, const.RTYPE_IDENTIFIER, const.RTYPE_PAIR, const.RTYPE_POINT):
                   ${h.checkbox('kst_id', rcd.id)}
                   % endif
                 </td>
                 % endif
                 <td ${td_att} width="25">${n_rcd+1+n_offset}</td>
                 <td ${td_att} style="overflow-wrap:break-word;word-wrap:break-word;word-break:break-all;">
                   % if rcd.tyyp == const.RTYPE_CORRECT:
                   <i>${_("Vastuseid pole sisestatud")}</i>
                   % elif c.basetype == const.BASETYPE_MATH:
                   <div style="max-width:900px;overflow:auto">
                     <span class="math-view">${rcd.sisu}</span>
                     % if rcd.sisu:
                     <div class="math-hidden" style="float:right">
                       <span class="math-hidden-latex" style="display:none">${rcd.sisu}</span>
                       <u style="cursor:pointer" onclick="$(this).prev('.math-hidden-latex').toggle()"><img src="/static/images/latex.png"/></u>
                     </div>
                     % endif
                   </div>
                   % elif rcd.kood1:
                   ${rcd.kood1}
                   % elif c.kysimus.rtf:
                   <iframe class="rtfresp" height="30px" width="99%">
                    ${rcd.sisu}
                   </iframe>
                   % else:
                   ${rcd.sisu}
                   % endif
                   <!--kvst ${rcd.id}: kood1=${rcd.kood1},kood2=${rcd.kood2},oige=${rcd.oige},tyyp=${rcd.tyyp}-->
                 </td>
                 % if c.basetype in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):  
                 <td ${td_att}>
                   % if rcd.tyyp == const.RTYPE_CORRECT:
                   <i>${_("Vastuseid pole sisestatud")}</i>
                   % else:
                   ${rcd.kood2}
                   % endif
                 </td>
                 % elif c.sp_tyyp == const.INTER_GAP and c.kysimus.seq == 0:                 
                 <td ${td_att}>
                   % if rcd.tyyp == const.RTYPE_CORRECT:
                   <i>${_("Vastuseid pole sisestatud")}</i>
                   % else:
                   ${rcd.sisu}
                   % endif
                 </td>
                 % endif
                 <td ${td_att}>
                   <%
                     vv = di_vv.get(rcd.maatriks)
                     if not vv:
                        vv = di_vv[rcd.maatriks] = model.Valikvastus.get_by_tulemus(c.kysimus.tulemus_id, rcd.maatriks)
                     selgitus = vv and vv.get_selgitus(rcd) or None
                   %>
                   ${selgitus}
                 </td>
                 <td ${td_att}>
                   <%
                     url = None
                     if rcd.vastuste_arv and c.app_ekk and c.toimumisaeg_id:
                         url = h.url('hindamine_analyys_kvstatistika', toimumisaeg_id=c.toimumisaeg_id, kst_id=c.kst.id, id=rcd.id)
                     elif rcd.vastuste_arv and c.app_eis and c.testiruum_id:
                         url = h.url('test_analyys_kvstatistika', test_id=c.test.id, testiruum_id=c.testiruum_id, kst_id=c.kst.id, id=rcd.id)
                   %>
                   % if url:
                   ${h.link_to_dlg(str(rcd.vastuste_arv), url, title=_("Vastajad"), level=2)}
                   % else:
                   ${rcd.vastuste_arv}
                   % endif
                 </td>
                 <td ${td_att}>
                   % if c.kst.vastuste_arv:
                   ${h.fstr(rcd.vastuste_arv*100./c.kst.vastuste_arv)}%
                   % endif
                 </td>
                 <td ${td_att}>
                   ${c.opt.C_CORRECT.get(rcd.oige)}
                 </td>
                 % if c.is_debug:
                 <td ${td_att}>
                   ${rcd.id}
                 </td>
                 % endif
               </tr>
               % endfor
             </tbody>
           </table>
% endif
% if c.kysimus.rtf:
<script>
$(function(){
 $('iframe.rtfresp').on('load', function(){
   var ibody = this.contentWindow.document.body;
   this.height = (parseFloat(ibody.scrollHeight) + 20) + 'px';
 });
 $('iframe.rtfresp').each(function(n,iframe){
   iframe.srcdoc = $(iframe).html();
 });
})
</script>
% endif         
