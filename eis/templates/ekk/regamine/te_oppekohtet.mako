## -*- coding: utf-8 -*- 
## tasemeeksamile registreerimisel kysitakse eesti keele õppimise kohta
<%
        def leia_varasemad_oppekohad():
          q = model.SessionR.query(model.Oppekoht).\
              join(model.Oppekoht.sooritaja).\
              filter_by(kasutaja_id=c.kasutaja.id).\
              filter(model.Oppekoht.oppekohtet_kood!=None).\
              order_by(model.sa.desc(model.Sooritaja.id))
          j_id = None
          di = {}
          for rcd in q.all():
            if j_id is None:
               j_id = rcd.sooritaja_id
            if id == j_id:
               di[rcd.oppekohtet_kood] = rcd.oppekoht_muu
            else:
               break
          return di

        c.sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik) 
        oppekohad = {}
        for r in c.sooritajad:
          for rcd in r.oppekohad:
             if rcd.oppekohtet_kood:
                oppekohad[rcd.oppekohtet_kood] = rcd.oppekoht_muu
        if not oppekohad:
          oppekohad = leia_varasemad_oppekohad()
%>
<div>
% for ind, row in enumerate(c.opt.klread_kood('OPPEKOHTET')):
        <%
        prefix = 'oket-%d' % ind
        kood, title = row[:2]
        checked = kood in oppekohad
        muu_nimi = oppekohad.get(kood)
        %>
        <div class="row">
          <div class="col-md-4">
            ${h.checkbox('%s.oppekohtet_kood' % prefix, kood, checked=checked, label=title, class_="opkoht")}
            ## et index oleks õige, tuleb iga rea kohta midagi saata
            ${h.hidden('%s.tmp_kood' % prefix, kood)} 
          </div>
        % if kood == const.OPPEKOHTET_KEELTEKOOL:
          <div class="col-md-3 col-lg-2 text-md-right lisa">
            ${h.flb(_("nimeta, millises:"), rq=True)}
          </div>
          <div class="col-md-5 col-lg-6 lisa">
            ${h.text('%s.oppekoht_muu' % prefix, muu_nimi, maxlength=100)}
          </div>
        % elif kood == const.OPPEKOHTET_MUU:
          <div class="col-md-3 col-lg-2 text-md-right lisa">
            ${h.flb(_("nimeta, kus:"), rq=True)}
          </div>
          <div class="col-md-5 col-lg-6 lisa">
            ${h.text('%s.oppekoht_muu' % prefix, muu_nimi, maxlength=100)}
          </div>
        % endif        
        </div>
      % endfor
</div>
<script>
$(function(){
   $('input.opkoht[value="${const.OPPEKOHTET_KEELTEKOOL}"],input.opkoht[value="${const.OPPEKOHTET_MUU}"]').each(function(){
      $(this).closest('.row').find('.lisa').toggle(this.checked);
   });
   $('input.opkoht[value="${const.OPPEKOHTET_KEELTEKOOL}"],input.opkoht[value="${const.OPPEKOHTET_MUU}"]').change(function(){
      $(this).closest('.row').find('.lisa').toggle(this.checked);
   });
});
</script>
