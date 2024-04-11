## Hindamisprotokolli yhe hindamiskogumi hindepallide sisestamine

<%namespace name="hinne" file="hinne.mako"/>

## antud on c.testiylesanded ja c.hindamiskogum ja c.sisestuskogum
<%
   c.hindamiskogum_id = c.hindamiskogum and c.hindamiskogum.id or '0'
   c.testikoht = c.protokoll.testipakett.testikoht
   opt_komplektid = c.hindamiskogum.get_komplektivalik().get_opt_komplektid(c.testikoht.toimumisaeg)

   c.vastvorm_kood = c.toimumisaeg.testiosa.vastvorm_kood

   if c.toimumisaeg.testiosa.test.testiliik_kood==const.TESTILIIK_TASE:
      # tasemeeksami hindaja ei pea olema eelnevalt läbiviijaks pandud
      if c.vastvorm_kood == const.VASTVORM_KP or c.hindamisprotokoll.liik >= const.HINDAJA3: 
         if c.vastvorm_kood == const.VASTVORM_KP:
            grupp_id = const.GRUPP_HINDAJA_K
         else:
            grupp_id = const.GRUPP_HINDAJA_S
         opt_hindajad = c.testikoht.opt_te_labiviijad(grupp_id, lisatud_labiviijad_id=c.lisatud_labiviijad_id, hindamiskogum_id=c.hindamiskogum_id, liik=c.hindamisprotokoll.liik)
      else:
         if c.hindamisprotokoll.liik == const.HINDAJA2:
            grupp_id = const.GRUPP_HINDAJA_S2
         else:
            grupp_id = const.GRUPP_HINDAJA_S
         opt_hindajad = c.testiruum.opt_te_labiviijad(grupp_id, lisatud_labiviijad_id=c.lisatud_labiviijad_id, liik=c.hindamisprotokoll.liik)

   elif c.vastvorm_kood == const.VASTVORM_KP or c.hindamisprotokoll.liik >= const.HINDAJA3:
      if c.hindamiskogum:
         hindajad = [lv for lv in c.hindamiskogum.labiviijad if lv.liik == c.hindamisprotokoll.liik and lv.toimumisaeg_id == c.toimumisaeg.id]
      else:
         hindajad = []
      opt_hindajad = [(lv.id, '%s %s' % (lv.tahis, lv.kasutaja.nimi)) for lv in hindajad]
   else:
      if c.hindamisprotokoll.liik == const.HINDAJA2:
         grupp_id = const.GRUPP_HINDAJA_S2
      else:
         grupp_id = const.GRUPP_HINDAJA_S
      opt_hindajad = c.testiruum.opt_labiviijad(grupp_id, c.lisatud_labiviijad_id, liik=c.hindamisprotokoll.liik)
      #hindajad = [lv for lv in c.testiruum.labiviijad if lv.kasutajagrupp_id==grupp_id and lv.kasutaja_id]

   if c.toimumisaeg.intervjueerija_maaraja:
      if c.toimumisaeg.testiosa.test.testiliik_kood==const.TESTILIIK_TASE:
         opt_intervjueerijad = [(lv.id, '%s %s' % (lv.tahis or '', lv.kasutaja.nimi)) for lv in c.testiruum.labiviijad if lv.kasutajagrupp_id==const.GRUPP_INTERVJUU and lv.kasutaja_id]
      else:
         opt_intervjueerijad = c.testiruum.opt_labiviijad(const.GRUPP_INTERVJUU, c.lisatud_labiviijad_id)
%>
<div id="hindamiskogum">
${h.hidden('hk-%d.hindamiskogum_id' % c.hk_n, c.hindamiskogum and c.hindamiskogum.id or None)}

<table class="table" width="100%">
  <tr>
    % if c.hindamiskogum:
    <td>
      ${c.hindamiskogum.tahis}
      ${c.hindamiskogum.nimi}
      <!--hk${c.hindamiskogum.id}-->
    </td>
    % endif
    % if c.sisestus != 'p':
    <td class="frh">${_("Ülesandekomplekt")}</td>
    <td>
      ${h.select('komplekt_id', '', opt_komplektid, empty=(len(opt_komplektid)!=1), wide=False)}
    </td>
    <td class="frh">${_("Hindaja")}</td>
    <td nowrap>
      ${h.select('hindaja_id',c.hindaja_id,opt_hindajad,wide=False,empty=(len(opt_hindajad)!=1))}

      % if c.hindamiskogum and c.hindamiskogum.kontrollijaga_hindamine:
      ${h.select('kontroll_hindaja_id', c.kontroll_hindaja_id, opt_hindajad, wide=False, empty=True)}
      % endif
    </td>

    % if c.toimumisaeg.intervjueerija_maaraja:
    <td class="frh">${_("Intervjueerija")}</td>
    <td>
      ${h.select('intervjueerija_id', c.intervjueerija_id, opt_intervjueerijad, wide=False, empty=(len(opt_intervjueerijad)!=1))}
    </td>
    % endif

    <td align="right">
      ${h.button(_('Kanna ridadele'), onclick="kanna(this)")}
      <script>
        function kanna(field)
        {
          var div = $(field).parents('div#hindamiskogum');

          var fld_k = div.find('.inp_komplekt').
             filter(function(){return $(this).val()=="";});
          $.each(fld_k, function(n, item){
             $(item).val(div.find('#komplekt_id').val());
             set_komplekt(item);
          });

          div.find('.inp_hindaja').
             filter(function(){return $(this).val()=="";}).
             val(div.find('#hindaja_id').val());

        % if c.hindamiskogum and c.hindamiskogum.kontrollijaga_hindamine:
          div.find('.inp_kontroll_hindaja').
             filter(function(){return $(this).val()=="";}).
             val(div.find('#kontroll_hindaja_id').val());
        % endif

        % if c.toimumisaeg.intervjueerija_maaraja:
          div.find('.inp_intervjueerija').
             filter(function(){return $(this).val()=="";}).
             val(div.find('#intervjueerija_id').val());
        % endif

          set_focus_to_next_input_field(field);
        }
      </script>
    </td>
    % endif
  </tr>
</table>
<%
   ## tabeli veergude arv
   col_cnt = 2
   ## dict, kus iga ty kohta on list selle aspektide loeteluga
   c.kogum_aspektid = {}
   ## dict, kus iga ty kohta on dict, milles iga komplekti kohta on list vy-de loeteluga
   c.valitudylesanded = {}
%>

<%include file="hprotokoll.hkogum_js.mako"/>

<table width="100%" class="table table-borderless table-striped tbl-sisestamine" id="tbl_hk_${c.hk_n}">
  ## tabeli päise esimene rida, kus on testiylesannete järjekorranumbrid
  <tr>
    <th rowspan="2">${_("Sooritaja")}</th>
    <th rowspan="2">${_("Ülesandekomplekt")}</th>
    % for ty in c.testiylesanded:
       <% 
          colspan = len(c.kogum_aspektid[ty.id]) + 1
          col_cnt += colspan
       %>
       % if colspan > 1:
       ## aspektidega ylesanne
    <th colspan="${colspan}" align="center">${ty.seq}
      <!--ty ${ty.id}-->
    </th>
       % else:
       ## aspektideta ylesanne
    <th rowspan="2" align="center">${ty.seq}
      <!--ty ${ty.id}-->
    </th>
       % endif
    % endfor

      <% col_cnt += 1 %>
    <th rowspan="2">${_("Hindaja")}</th>
    % if c.hindamiskogum and c.hindamiskogum.kontrollijaga_hindamine:
      <% col_cnt += 1 %>
    <th rowspan="2">${_("Hindaja")}</th>
    % endif
    % if c.toimumisaeg.intervjueerija_maaraja:
      <% col_cnt += 1 %>
    <th rowspan="2">${_("Intervjueerija")}</th>
    % endif
    % if c.sisestus == 'p':
      <% col_cnt += 1 %>
    <th rowspan="2">${_("Sisestajad")}</th>
    % endif
  </tr>

  ## tabeli päise teine rida, kus on aspektid
  <tr>
    % for ty in c.testiylesanded:
       % if len(c.kogum_aspektid[ty.id]):
          % for a in c.kogum_aspektid[ty.id]:
    <th>${a.nimi}
<!--
% for vy_id, ha in a.y_hindamisaspektid.items():
      vy${vy_id}=ha${ha.id}
% endfor
-->
    </th>
          % endfor
    <th></th>          
       % endif
    % endfor
  </tr>
<% n = 0 %>
% for rcd in c.items:
  <% 
     if c.sisestus == 'p' and c.kahekordne_sisestamine:
        ## parandamine
        tos, hindamine, hindamine2 = rcd
     else:
        tos, hindamine = rcd 
        hindamine2 = None
  %>
  % if tos.staatus != const.S_STAATUS_TEHTUD:
  <tr>
    <td>
      ${tos.tahised}
    </td>
    <td colspan="${col_cnt-1}">
      ${tos.staatus_nimi}
    </td>
  </tr> 
  % elif c.hindamisprotokoll.liik < const.HINDAJA3 or hindamine:
     ## kolmanda hindamise korral ei sisestata punkte kõigile testiprotokolli kantud
     ## sooritajatele, vaid ainult neile, kellele on loodud kolmanda hindamise kirje
     ## kolmanda hindamise kirje luuakse kolmandale hindajale töö hindamiseks määramisel.
     ${tr_tos_hindamine(n, tos, hindamine, hindamine2)}
     <% n += 1 %>
  % endif
  
% endfor
</table>
<br/>
</div>


<%def name="tr_tos_hindamine(n, tos, hindamine, hindamine2)">
  ## yhe testiosasoorituse hindamise rida
  <% 
     prefix1 = 'hk-%d.hmine-%d' % (c.hk_n, n) 
     prefix2 = 'hk-%d.hmine2-%d' % (c.hk_n, n) 
  %>
  <tr id="tos">
    <td>
      ${tos.tahised}
      ${h.hidden('%s.sooritus_id' % prefix1, tos.id)}
      % if c.sisestus == 'p' and c.kahekordne_sisestamine:
      ${h.hidden('%s.sooritus_id' % prefix2, tos.id)}
      % endif

      % if c.testimiskord.sisestus_isikukoodiga:
      ${tos.sooritaja.kasutaja.isikukood}
      % endif
    </td>
    <td>
      ## komplekt
      <%
         err = hindamine2 and hindamine2.komplekt_id and hindamine and hindamine.komplekt_id and hindamine.komplekt_id != hindamine2.komplekt_id and ' class="form-control is-invalid"' or  ''

         komplekt_id = hindamine and hindamine.komplekt_id
         komplekt2_id = c.sisestus == 'p' and hindamine2 and hindamine2.komplekt_id
         yks_komplekt = len(opt_komplektid) == 1
         if yks_komplekt:
             ## kui ainult üht komplekti saab valida, siis polegi vaja valida            
             komplekt_id = komplekt2_id = opt_komplektid[0][0]
             komplekt_tahis = opt_komplektid[0][1]
      %>
      <table cellpadding="0" cellspacing="0">
        <tr>
          <td${err}>
            % if yks_komplekt:
            ${komplekt_tahis}
            ${h.hidden('%s.komplekt_id' % prefix1, komplekt_id)}
            % else:
            ${h.select('%s.komplekt_id' % prefix1, komplekt_id, opt_komplektid,
            onchange='set_komplekt(this)',
            empty=True, wide=False, class_='inp_komplekt')}
            % endif
          </td>
          % if c.sisestus == 'p' and c.kahekordne_sisestamine:
          <td${err}>
            % if yks_komplekt:
            ${komplekt_tahis}
            ${h.hidden('%s.komplekt_id' % prefix2, komplekt2_id)}
            % else:
            ${h.select('%s.komplekt_id' % prefix2, komplekt2_id, opt_komplektid,
            onchange='set_komplekt(this)',
            empty=True, wide=False, class_='inp_komplekt')}
            % endif
          </td>
          % endif
        </tr>
      </table>
    </td>

    ## testiylesannete kaupa hindetoorpunktide sisestamine

    % for ty_n, ty in enumerate(c.testiylesanded):
       <%
        vy = komplekt_id and c.valitudylesanded[ty.id][komplekt_id][0] or None
        vy2 = komplekt2_id and c.valitudylesanded[ty.id][komplekt2_id][0] or None
        atos = ty.alatest_id and tos.get_alatestisooritus(ty.alatest_id) 
       %>
    % if atos and atos.staatus != const.S_STAATUS_TEHTUD:
      <td colspan="${len(c.kogum_aspektid[ty.id]) + 1}">${atos.staatus_nimi}</td>
    % else:
      ${hinne.ty_pallid(tos, ty, c.kogum_aspektid[ty.id],
                         '%s.ty-%d' % (prefix1, ty_n), hindamine, vy, 
                         '%s.ty-%d' % (prefix2, ty_n), hindamine2, vy2)}
    % endif
    % endfor


    ## läbiviija
     <td>
    ${hinne.labiviija(opt_hindajad, c.vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2,
                      tabindex=100)}
##      % endif
    </td>

    % if c.hindamiskogum and c.hindamiskogum.kontrollijaga_hindamine:
    <td>
    ${hinne.kontroll_labiviija(opt_hindajad, c.vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2,
                      tabindex=100)}
    </td>
    % endif
    
    ## intervjueerija
    % if c.toimumisaeg.intervjueerija_maaraja:   
    <td>
    ${hinne.intervjueerija(opt_intervjueerijad,
                           prefix1, hindamine,
                           prefix2, hindamine2,
                           tabindex=100)}
    </td>
    % endif

    ## sisestajad

    % if c.sisestus == 'p':
    <td nowrap>
      % if hindamine:
         1. ${hindamine.sisestaja_kasutaja and hindamine.sisestaja_kasutaja.nimi} 
         <a class="menu1" onclick="open_dialog({'title':'${_('Esimese sisestamise logi')}',
           'url':'${h.url('sisestamine_hindamine_logi', hindamine_id=hindamine.id, partial=True)}'});">${_("Parandused")}</a>
      % endif
      % if hindamine2:
         <br/>
         2. ${hindamine2 and hindamine2.sisestaja_kasutaja and hindamine2.sisestaja_kasutaja.nimi} 
         <a class="menu1" onclick="open_dialog({'title':'${_('Teise sisestamise logi')}',
         'url':'${h.url('sisestamine_hindamine_logi', hindamine_id=hindamine2.id, partial=True)}'});">${_("Parandused")}</a>
      % endif
    </td>
    % endif
  </tr>
</%def>
