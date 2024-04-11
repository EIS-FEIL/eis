<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
<table  class="table">
         <%
            alatestid = list(c.item.testiosa.alatestid)
            n_ty = 0
         %>
         % if alatestid:
         % for alatest in alatestid:
         <%
           atos = c.item.get_alatestisooritus(alatest.id) 
           cnt_ty = len([ty for ty in alatest.testiylesanded if ty.max_pallid])
         %>
         % for ind_ty, ty in enumerate(alatest.testiylesanded):
         ${self.ty_row(alatest, atos, ind_ty, n_ty, ty, cnt_ty)}
         <% n_ty += 1 %>
         % endfor
         % endfor
         % else:
         <%
           testiylesanded = list(c.item.testiosa.testiylesanded)
           cnt_ty = len([ty for ty in testiylesanded if ty.max_pallid])
         %>
         % for ty in testiylesanded:
         ${self.ty_row(None, None, None, n_ty, ty, cnt_ty)}
         <% n_ty += 1 %>
         % endfor
         % endif
</table>
<div class="d-flex">
  ${h.button(_("Katkesta"), onclick="close_dialog()", level=2)}
  <div class="flex-grow-1 text-right">
    % if c.is_edit:
    ${h.submit_dlg(clicked=True)}
    % endif
  </div>
</div>
${h.end_form()}
       
<%def name="ty_row(alatest, atos, ind_ty, n_ty, ty, cnt_ty)">
         <%
            yv = c.item.get_ylesandevastus(ty.id)
            if yv:
               pallid = yv.pallid
            else:
               pallid = ''
            vy = yv and yv.valitudylesanne or None
            vy_seq = vy and vy.seq or None
         %>
         <tr>
           % if ind_ty == 0 and alatest and cnt_ty:
           <td rowspan="${len(alatest.testiylesanded)}">${alatest.nimi}</td>
           % endif
       % if not ty.max_pallid:
           <td colspan="${cnt_ty and 3 or 4}">
             ${h.hidden('ty-%d.pallid' % (n_ty), '0')}
             ${h.hidden('ty-%d.id' % (n_ty), ty.id)}
           </td>
       % else:
           <td>${ty.nimi or ty.tahis}</td>
           % if atos and atos.staatus == const.S_STAATUS_VABASTATUD:
           <td colspan="2">
             ${atos.staatus_nimi}
           </td>
           % else:
           <td>
             ${h.float5('ty-%d.pallid' % (n_ty), pallid, maxvalue=ty.max_pallid, class_='val-ty')}
             ${h.hidden('ty-%d.id' % (n_ty), ty.id)}
           </td>
           <td>
             % if ty.on_valikylesanne:
             <% pealkirjad = (ty.pealkiri or '').split('\n') %>
             % for seq in range(1, ty.valikute_arv+1):
             <%
               pealkiri = len(pealkirjad) >= seq and pealkirjad[seq-1] or 'valik %d' % (seq)
               checked = vy_seq == seq
             %>
             ${h.radio('ty-%d.vy_seq' % n_ty, seq, checked=checked, label=pealkiri)}<br/>
             % endfor
             % endif
           </td>
           % endif
       % endif
         </tr>
</%def>
