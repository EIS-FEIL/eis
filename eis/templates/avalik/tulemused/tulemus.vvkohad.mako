${h.not_top()}
<%include file="/common/message.mako"/>
<%
   testimiskord = c.sooritaja.testimiskord
%>
${h.form_save(c.sooritaja.id)}
${h.hidden('sub', 'vvk')}
<div class="mb-2">
          <% regkohad = list(testimiskord.regkohad) %>
          <div class="form-group row">
            ${h.flb3(_("Õppeasutused"))}
            <div class="col">
              <%
                opilane = c.sooritaja.kasutaja.opilane
                # oma kool
                koht_id = opilane and opilane.koht_id
                # kas oma koolil on luba tulemusi vaadata ilma, et sinna kandideeriks
                on_autom_kool = False
                # sisseastumiskohtade valik
                opt_vvk = [(k.id, k.nimi) for k in regkohad]
                # koolid, millel on lubatud vaadata tulemusi
                values = []
                for r in c.sooritaja.kandideerimiskohad:
                    if not r.automaatne:
                        values.append(r.koht_id)
                    if r.koht_id == koht_id:
                        on_autom_kool = True

                # kas oma kool on regkohtade seas?
                autom_kool = None
                if koht_id:
                    q = (model.Session.query(model.Testikoht.id)
                         .join(model.Testikoht.toimumisaeg)
                         .filter(model.Toimumisaeg.testimiskord_id==testimiskord.id)
                         .filter(model.Testikoht.koht_id==koht_id))
                    if q.count() > 0:
                       autom_kool = model.Koht.get(koht_id).nimi
              %>
              ${h.poserr(f"vvk")}
              % for k_id, k_nimi in opt_vvk:
              <div>
                ${h.checkbox(f'vvk', k_id, label=k_nimi, checkedif=values)}
              </div>
              % endfor
              % if autom_kool:
              <div class="mt-4">
                <%
                  label = _("Luban praegusel koolil ({nimi}) vaadata minu testitulemusi").format(nimi=autom_kool)
                %>
                ${h.checkbox1(f'vvk_oma', 1, checked=on_autom_kool, disabled=koht_id in values, label=label)}
                <script>
                  ## kui oma kool valitakse kandideeritavate koolide seas, siis teha märge ka oma kooli märkeruutu
                  $('#vvk_${koht_id}').click(function(){
                     if(this.checked) $('#vvk_oma').prop('checked', true);
                     $('#vvk_oma').prop('disabled', this.checked);
                  });
                </script>
              </div>
              % endif
            </div>
          </div>
</div>

${h.submit_dlg()}
