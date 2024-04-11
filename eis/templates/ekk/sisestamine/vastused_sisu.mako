<%namespace name="hinne" file="hinne.mako"/>

<%def name="td_komplekt()">
## komplekti valiku sisestamine
## kontrolleris seatakse c.komplekt ja sisestamise parandamise resiimi korral c.komplekt_id1, c.komplekt_id2
    <td>
      % if len(c.opt_komplekt) == 1 and c.komplekt:
          ${c.komplekt.tahis}
      % else:
      <table cellpadding="0" cellspacing="0">
        <%
         err = c.komplekt_id1 and c.komplekt_id2 and c.komplekt_id1 != c.komplekt_id2 and ' id="entryerror"' or ''
        %>
      <tr>
        <td${err}>
          ${h.select('komplekt_id', c.komplekt and c.komplekt.id,
          c.opt_komplekt, wide=False, empty=True, onchange='this.form.submit()')}
        </td>
           % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <td${err}>
          ${h.select('komplekt_id2', c.komplekt_id2, c.opt_komplekt,
          wide=False, empty=True, onchange='this.form.submit()')}
        </td>
           % endif
      </tr>
      </table>
      % endif
    </td>
</%def>

<%def name="tr_hindaja(hkogum, vastvorm_kood, holek,
                       prefix1, hindamine, 
                       prefix2, hindamine2)">
  ## Hindamiskogumi hindaja sisestamine
  <div class="tr-hindaja d-flex">
    <div class="fh mr-3 p-2">
      ${_("Hindaja")}
    </div>
      <%
       if c.toimumisaeg.testiosa.test.testiliik_kood==const.TESTILIIK_TASE:
          # tasemeeksami hindaja ei pea olema eelnevalt läbiviijaks pandud
          grupp_id = const.GRUPP_HINDAJA_K
          opt_hindajad = c.sooritus.testikoht.opt_te_labiviijad(grupp_id, lisatud_labiviijad_id=c.lisatud_labiviijad_id, hindamiskogum_id=hkogum.id, liik=c.hindamine_liik)            
       else:
          hindajad = [lv for lv in hkogum.labiviijad if lv.liik == c.hindamine_liik and lv.toimumisaeg_id == c.toimumisaeg.id]         
          opt_hindajad = [(lv.id, '%s %s' % (lv.tahis, lv.kasutaja.nimi)) for lv in hindajad]

       # arvutihinnatava kogumi sisestamisel ei pea olema hindajat
       if hkogum.arvutihinnatav:
          empty = True
       else:
          empty = None
 
       eelmine_hindaja_id = eelmine_kontrollija_id = None
       if c.eelmine_sooritus:
         eelmine_holek = c.eelmine_sooritus.get_hindamisolek(hkogum)
         if eelmine_holek:
            eelmine_hindamine = eelmine_holek.get_hindamine(c.hindamine_liik, c.sisestus)
            if eelmine_hindamine:
                if len(opt_hindajad) and int(opt_hindajad[0][0]) < 0:
                   # hindajate määramine kasutaja.id järgi
                   e_h_k_id = eelmine_hindamine.hindaja_kasutaja_id
                   eelmine_hindaja_id = e_h_k_id and 0-e_h_k_id or None
                else:
                   eelmine_hindaja_id = eelmine_hindamine.labiviija_id
                   eelmine_kontrollija_id = eelmine_hindamine.kontroll_labiviija_id
      %>
    <div class="mr-3 p-2">
          ${hinne.labiviija(opt_hindajad, vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2, 
                      empty=empty,
                      jrg_labiviija_id=eelmine_hindaja_id)}
    </div>
    % if hkogum.kontrollijaga_hindamine:
    <div class="mr-3 p-2">
          ${hinne.kontroll_labiviija(opt_hindajad, vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2, 
                      empty=True,
                      jrg_labiviija_id=eelmine_kontrollija_id)}
    </div>
    % endif

    % if holek:
    <div class="p-2 flex-grow-1 text-right">
      <div>${_("hindamisolek")}: ${holek.staatus_nimi} (${holek.hindamistase})</div>
      % if holek.hindamisprobleem:
      <div>
        ${holek.selgitus or holek.hindamisprobleem_nimi or '-'}
      </div>
      % endif
    </div>
    % endif
  </div>
</%def>

<%def name="tr_testiylesanne(ty, valik_seq, valikute_arv, valitud,
                             prefix1, hindamine, vy,
                             prefix2, hindamine2, vy2)">
## yhe testiylesande sisestamine
    <%
      ## kontrollime, et pole märgitud seda ylesannet sisaldaval alatestil puudujaks
      atos = ty.alatest_id and c.sooritus.get_alatestisooritus(ty.alatest_id)
      is_entry = not (atos and atos.staatus != const.S_STAATUS_TEHTUD)
    %>
<div class="tr-sisestamine d-flex">
  <div class="td-sis-header" style="background: #fafafa;">
    <div>
      % if ty.nimi != ty.tahis:
      ${ty.tahis}
      % endif
      ${ty.nimi or _('ülesanne')}
      (${ty.sisestusviis_nimi.lower()})
    </div>
    % if is_entry:
      % if valikute_arv > 1:
      ${h.radio('%s.vy_seq' % prefix1, valik_seq, label=valik_seq, checked=valitud, class_='valikylesanne')}
      % if c.sisestus == 'p' and c.kahekordne_sisestamine:
      <span class="valikradio2" style="visibility:hidden">
        ${h.radio('%s.vy_seq' % prefix2, valik_seq)}
      </span>
      % endif
      % endif
      % if not ty.hyppamisviis:
      ## javascript failis window.js vaatab ja kui näeb seda elementi, siis teab, 
      ## et peale valikvälja sisestust automaatne hype järgmisele väljale on keelatud
      <span class="hyppamisviis">0</span>
      % endif
    % endif
    <!-- ty ${ty.id} vy ${vy and vy.id} y ${vy and vy.ylesanne_id} -->
  </div>
  <div class="td-sis-body flex-grow-1">
    <div>
      ## lai teadete div 
       % if not is_entry:
       ${atos.staatus_nimi}
       % else:
       ${h.hidden('%s.ty_id' % (prefix1), ty.id)}
       ${h.hidden('%s.vy_id' % (prefix1), vy and vy.id)}
       % if c.sisestus == 'p' and c.kahekordne_sisestamine:
       ${h.hidden('%s.ty_id' % (prefix2), ty.id)}
       ${h.hidden('%s.vy_id' % (prefix2), vy2 and vy2.id)}
       % endif
       ## ylesande veateadete koht (hidden toorpunktide väli)
       ${hinne.ty_hindamine_koond(prefix1, prefix2)}
      % endif
       
    </div>
    % if is_entry:
    <div class="td-sis-values d-flex flex-wrap">
      ## sõltuvalt määratud sisestusviisist sisestatakse kas
      ## vastuseid või hindepalle või vastuse õigsust
      % if ty.sisestusviis == const.SISESTUSVIIS_VASTUS or ty.sisestusviis == const.SISESTUSVIIS_OIGE:
      ${self.ty_vastused(ty,
                        prefix1, hindamine, vy,
                        prefix2, hindamine2, vy2)}

      % elif ty.sisestusviis == const.SISESTUSVIIS_PALLID:
      ${self.ty_pallid(ty, 
                      prefix1, hindamine, vy,
                      prefix2, hindamine2, vy2)}
      % else:
      ${h.alert_error(_("Testiülesande sisestusviis on määramata"), False)}
      % endif
    </div>
    % endif
  </div>
</div>
</%def>

<%def name="ty_pallid(ty, 
                      prefix1, hindamine, vy,
                      prefix2, hindamine2, vy2)">
<%
   ty_aspektid = ty.get_aspektid(c.toimumisaeg) 
   on_aspektid = bool(ty_aspektid)
   vy_on_aspektid = False
   vy2_on_aspektid = False
   hinne1 = hindamine and vy and hindamine.get_vy_ylesandehinne(vy.id) or None 
   hinne2 = hindamine2 and vy2 and hindamine2.get_vy_ylesandehinne(vy2.id) or None
%>
   % if on_aspektid:
      ## kui on aspektidega ylesanne, siis on punktid iga aspekti kohta

     % for ha_n, a in enumerate(ty_aspektid):
       <div class="td-sis-value">
         ${a.nimi}
             <% 
                ha = vy and a.y_hindamisaspektid.get(vy.id) or None
                ha2 = vy2 and a.y_hindamisaspektid.get(vy2.id) or None
                vy_on_aspektid |= bool(ha)
                vy2_on_aspektid |= bool(ha2)

                aspektihinne = aspektihinne2 = None
                if ha:
                   aspektihinne = hinne1 and hinne1.get_aspektihinne(ha.id)
                if ha2:
                   aspektihinne2 = hinne2 and hinne2.get_aspektihinne(ha2.id)

             %>
       ${hinne.aspekt_hindamine(c.sooritus, ty, ha.aspekt, 
                                   '%s.ha-%d' % (prefix1, ha_n), aspektihinne, vy, ha,
                                   '%s.ha-%d' % (prefix2, ha_n), aspektihinne2, vy2, ha2)}
                  
       </div>
     % endfor

   % else:

   ${self.ty_pallid_kysimused(ty,
                              prefix1, hindamine, vy, hinne1,
                              prefix2, hindamine2, vy2, hinne2)}
   

   % endif
</%def>

<%def name="ty_pallid_kysimused(ty, 
                                prefix1, hindamine, vy, hinne1,
                                prefix2, hindamine2, vy2, hinne2)">
## kui ei ole aspektidega ylesanne, siis on punktid iga kysimuse kohta
  <%
     ylesandevastus = c.sooritus.get_ylesandevastus(ty.id)
     k_n = 0
     ylesanne = vy and vy.ylesanne
  %>
##  % if ylesanne:
     % for block in ylesanne.sisuplokid:      
        % if not(block.staatus == const.B_STAATUS_KEHTETU or block.naide or not block.is_interaction):
  <!-- y ${block.ylesanne_id} plokk ${block.seq} (${block.tyyp_nimi}) ${h.url('ylesanne_sisuplokk', id=block.id, ylesanne_id=block.ylesanne_id)}  -->
           % for k in block.kysimused:
           <% tulemus = k.tulemus %>
           % if tulemus and not tulemus.oigsus_kysimus_id:
        <div class="td-sis-value">   
       ${hinne.ty_kysimus_hindamine(c.sooritus, ty, k, ylesandevastus,
                                   '%s.k-%d' % (prefix1, k_n), vy, hinne1,
                                   '%s.k-%d' % (prefix2, k_n), vy2, hinne2)}
        </div>
       <%
          k_n += 1
       %>
          % endif
          % endfor
        % endif
     % endfor
##  % endif
</%def>

<%def name="ty_vastused(ty,
                        prefix1, hindamine, vy,
                        prefix2, hindamine2, vy2)">
<%
  ## c.responses ja c.prefix on kasutusel sisuploki entry() sees
  ylesandevastus = c.sooritus.get_ylesandevastus(ty.id, komplekt_id=vy.komplekt_id, vy=vy)
  sisestus = c.sisestus == 'p' and 1 or int(c.sisestus)
  c.responses = ylesandevastus and ylesandevastus.get_responses(sisestus) or {}
  c.prefix = '%s.r' % prefix1

  if c.sisestus == 'p' and c.kahekordne_sisestamine:
     ## sisestuste parandamine
     c.responses2 = ylesandevastus and ylesandevastus.get_responses(2) or {}
     c.prefix2 = '%s.r' % prefix2
  else:
     c.responses2 = None
     c.prefix2 = None

  is_correct = ty.sisestusviis == const.SISESTUSVIIS_OIGE
  entries = c.assessment_entry(vy.ylesanne, c.lang, request.handler, is_correct)
%>
% if len(entries) == 0: 
   ${h.alert_error(_("Ülesanne pole sisestatav, sest selles pole küsimusi"), False)}
% endif
% for n, (block, html) in enumerate(entries):
  <!-- ty ${ty.id} vy ${vy and vy.id} yv ${ylesandevastus and ylesandevastus.id} y ${block.ylesanne_id} plokk ${block.seq} (${block.tyyp_nimi}) ${h.url('ylesanne_sisuplokk', id=block.id, ylesanne_id=block.ylesanne_id)}  -->
  ${html}
% endfor
</%def>
