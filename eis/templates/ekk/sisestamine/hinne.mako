## Hinnete sisestamine

<%def name="ty_pallid(tos, ty, ty_aspektid,
                      prefix1, hindamine, vy,
                      prefix2, hindamine2, vy2)">
## yhe soorituse yhe testiylesande hinded
## aspektidega ylesande korral on mitu hindelahtrit, iga aspekti jaoks oma
## aspektideta ylesande korral on yks lahter

## Parameetrid:
## tos - soorituse kirje
## ty - testiylesande kirje
## ty_aspektid - list antud ty valitudylesannetes kasutatud aspektidest,
##               millele on lisatud y_hindamisaspektid

## Parandamise korral esimese sisestamise andmed, 
## sisestamise korral käimasoleva sisestamise andmed: 
## prefix1 - väljade nimede prefiks
## hindamine - sisestamise kirje (tabel Hindamine)
## vy - valitudylesande kirje
##
## Parandamise korral teise sisestamise andmed, 
## sisestamise korral muu sisestamise andmed: 
## prefix2 - väljade nimede prefiks
## hindamine2 - sisestamise kirje (tabel Hindamine)
## vy2 - valitudylesande kirje
      <%
        vy_on_aspektid = False
        vy2_on_aspektid = False
        hinne = hindamine and vy and hindamine.get_vy_ylesandehinne(vy.id) or None 
        hinne2 = hindamine2 and vy2 and hindamine2.get_vy_ylesandehinne(vy2.id) or None
      %>
      % if ty_aspektid:
          ## aspektidega testiylesanne
          % for ha_n, a in enumerate(ty_aspektid):
             <% 
                ha = vy and a.y_hindamisaspektid.get(vy.id) or None
                ha2 = vy2 and a.y_hindamisaspektid.get(vy2.id) or None
                aspektihinne = aspektihinne2 = None
                if ha:
                   aspektihinne = hinne and hinne.get_aspektihinne(ha.id)
                   vy_on_aspektid = True
                if ha2:
                   aspektihinne2 = hinne2 and hinne2.get_aspektihinne(ha2.id)
                   vy2_on_aspektid = True

             %>
             <td>
               ${self.aspekt_hindamine(tos, ty, a, 
                                     '%s.ha-%d' % (prefix1, ha_n), aspektihinne, vy, ha, 
                                     '%s.ha-%d' % (prefix2, ha_n), aspektihinne2, vy2, ha2)}
             </td>
          % endfor
      % endif
      ## aspektidega või aspektideta testiylesande kogupallide lahter
      ## ja valikylesande korral ylesande valikuväli
      ${self.td_ty_hindamine(tos, ty, bool(ty_aspektid), True,
                             prefix1, hinne, vy, vy_on_aspektid,
                             prefix2, hinne2, vy, vy2_on_aspektid)}

</%def>


<%def name="aspekt_hindamine(tos, ty, a,
                             prefix1, ahinne, vy, ha,
                             prefix2, ahinne2, vy2, ha2)">
## yhe soorituse yhe aspektidega testiylesande yhe aspekti hindamine (suurest tabelist yks lahter)
##
## Parameetrid:
## tos - soorituse kirje
## ty - testiylesande kirje
## a - aspekti (tabel Klrida) kirje
##
## Parandamise korral esimese sisestamise andmed, 
## sisestamise korral käimasoleva sisestamise andmed: 
## prefix1 - väljade nimede prefiks
## ahinne - ty aspektihinde kirje 
## vy - testiylesande valitudylesanne, mille hindeid sisestatakse
## ha - ylesande hindamisaspekt, mille hindeid sisestatakse
##
## Parandamise korral teise sisestamise andmed, 
## sisestamise korral muu sisestamise andmed: 
## prefix2 - väljade nimede prefiks
## ahinne2 - ty aspektihinde kirje
## vy2 - testiylesande valitudylesanne, mille hindeid sisestatakse
## ha2 - ylesande hindamisaspekt, mille hindeid sisestatakse
           
         <%
         err = ahinne and ahinne2 and ahinne.toorpunktid is not None and ahinne2.toorpunktid is not None and (ahinne.toorpunktid != ahinne2.toorpunktid or ahinne.nullipohj_kood != ahinne2.nullipohj_kood) and 'error' or ''
         %>
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
           ${h.hidden('%s.a_kood' % (prefix1), a.kood)}
           ${h.float5('%s.toorpunktid' % (prefix1), 
                      ahinne and ahinne.s_toorpunktid, 
                      maxvalue=ha and ha.max_pallid or None,
                      disabled=not ha)}
           <!-- ah ${ahinne and ahinne.id} ha ${ha and ha.id} vy ${vy and vy.id}-->
        </td>
           % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <td>
           ${h.hidden('%s.a_kood' % (prefix2), a.kood)}
           ${h.float5('%s.toorpunktid' % (prefix2),
                      ahinne2 and ahinne2.s_toorpunktid, 
                      maxvalue=ha2 and ha2.max_pallid or None,
                      disabled=not ha2)}
           <!-- ah ${ahinne2 and ahinne2.id} -->
        </td>
           % endif
      </tr>
      </table>
</%def>


<%def name="ty_kysimus_hindamine(tos, ty, k, ylesandevastus,
                                prefix1, vy, yhinne,
                                prefix2, vy2, yhinne2)">
## yhe soorituse yhe ylesande yhe kysimuse hindamine (suurest tabelist yks lahter)
##
## Parameetrid:
## tos - soorituse kirje
## ty - testiylesande kirje
## k - ylesande kysimus, mille hindeid sisestatakse
## ylesandevastus - soorituse ylesandevastuse kirje
## seq - kysimuse järjekorranumber (kui kysimusel võib mitu vastust olla)
##
## Parandamise korral esimese sisestamise andmed, 
## sisestamise korral käimasoleva sisestamise andmed: 
## prefix1 - väljade nimede prefiks
## yhinne - ylesandehinde kirje 
## vy - testiylesande valitudylesanne, mille hindeid sisestatakse
##
## Parandamise korral teise sisestamise andmed, 
## sisestamise korral muu sisestamise andmed: 
## prefix2 - väljade nimede prefiks
## yhinne2 - ylesandehinde kirje
## vy2 - testiylesande valitudylesanne, mille hindeid sisestatakse

         <%
         if c.sisestus == 'p':
              sisestus1 = 1
              sisestus2 = c.kahekordne_sisestamine and 2 or None
         else:
              sisestus1 = c.sisestus
              sisestus2 = None
         max_vastus = k.max_vastus or 1
         kvastus = ylesandevastus and ylesandevastus.get_kysimusevastus(k.id, sisestus1)
         khinne = kvastus and yhinne and yhinne.get_kysimusehinne(kvastus)

         if yhinne2 and sisestus2:
            kvastus2 = ylesandevastus and ylesandevastus.get_kysimusevastus(k.id, sisestus2)
            khinne2 = kvastus and yhinne2 and yhinne2.get_kysimusehinne(kvastus2)
         else:
            kvastus2 = khinne2 = None

         err = khinne and khinne2 and khinne.toorpunktid is not None and khinne2.toorpunktid is not None and (khinne.toorpunktid != khinne2.toorpunktid or khinne.nullipohj_kood != khinne2.nullipohj_kood) and 'is-invalid' or ''
         tulemus = k.tulemus
         max_pallid = tulemus and tulemus.max_pallid or vy.ylesanne.max_pallid
         %>           
      <table cellpadding="0" cellspacing="0" border="0" class="${err}">
      <tr>
        <td>
          ${k.kood}
           ${h.hidden('%s.k_id' % (prefix1), k.id)}
           % if c.sisestus == 'p' and c.kahekordne_sisestamine:
           ${h.hidden('%s.k_id' % (prefix2), k.id)}
           % endif
        </td>
      </tr>
      <tr>
        <td>
           ${h.float5('%s.toorpunktid' % (prefix1), 
                      khinne and khinne.s_toorpunktid, 
                      maxvalue=max_pallid,
                      disabled=not k)}
        </td>
           % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <td>
           ${h.float5('%s.toorpunktid' % (prefix2),
                      khinne2 and khinne2.s_toorpunktid, 
                      maxvalue=max_pallid,
                      disabled=not k)}
        </td>
           % endif
      </tr>
      </table>
</%def>



<%def name="ty_hindamine_koond(prefix1, prefix2)">
## yhe soorituse yhe testiylesande hindamise koondväljad
## lai veerg, et mahutada ylesande kohta käiv veateade
<td colspan="20">
      ${h.hidden('%s.toorpunktid' % (prefix1), '')}
      % if c.sisestus == 'p' and c.kahekordne_sisestamine:
      ${h.hidden('%s.toorpunktid' % (prefix2), '')}
      % endif
</td>
</%def>

<%def name="td_ty_hindamine(tos, ty, ty_on_aspektid, ty_on_id,
                            prefix1, hinne, vy, vy_on_aspektid,
                            prefix2, hinne2, vy2, vy2_on_aspektid)">
## yhe soorituse yhe testiylesande hindamine, kui
## punkte antakse hindamisaspektide eest või terve ülesande eest
    <td>
    % if ty_on_id:
      ${h.hidden('%s.ty_id' % (prefix1), ty.id)}
      ${h.hidden('%s.vy_id' % (prefix1), vy and vy.id)}
      % if c.sisestus == 'p' and c.kahekordne_sisestamine:
      ${h.hidden('%s.ty_id' % (prefix2), ty.id)}
      ${h.hidden('%s.vy_id' % (prefix2), vy2 and vy2.id)}
      % endif
    % endif
      ## eeldame, et kui testiylesande mõnel valitudylesandel on aspektid,
      ## siis on kõigil selle testiylesande valitudylesannetel aspektid
      ## st vy_on_aspektid == vy2_on_aspektid == ty_on_aspektid

    % if ty_on_aspektid and not ty.on_valikylesanne:
        ${h.hidden('%s.toorpunktid' % (prefix1), '')}
        % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        ${h.hidden('%s.toorpunktid' % (prefix2), '')}
        % endif

    % else:
      <% 
         err = hinne and hinne2 and hinne.toorpunktid is not None and hinne2.toorpunktid is not None and (hinne.toorpunktid != hinne2.toorpunktid or hinne.nullipohj_kood != hinne2.nullipohj_kood) and ' is-invalid' or ''
         opt_ty_valik = [(n+1,n+1) for n in range(ty.valikute_arv)]
      %>
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
          % if ty.on_valikylesanne and ty_on_id:
          ${h.select('%s.vy_seq' % (prefix1), vy and vy.seq, opt_ty_valik, wide=False)}
          % endif
          ${h.float5('%s.toorpunktid' % (prefix1), 
                     hinne and hinne.s_toorpunktid, 
                     maxvalue=vy and vy.ylesanne.max_pallid or None,
                     disabled=vy_on_aspektid)}
        </td>
        % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <td>
          % if ty.on_valikylesanne and ty_on_id:
          ${h.select('%s.vy_seq' % (prefix2), vy2 and vy2.seq, opt_ty_valik, wide=False)}
          % endif
          ${h.float5('%s.toorpunktid' % (prefix2), 
                     hinne2 and hinne2.s_toorpunktid, 
                     maxvalue=vy2 and vy2.ylesanne.max_pallid or None,
                     disabled=vy2_on_aspektid)}
        </td>
        % endif
      </tr>
      </table>
    % endif
    </td>
</%def>

<%def name="labiviija(opt_hindajad, vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2,
                      empty=None, jrg_labiviija_id=None, tabindex=None)">
## hindaja sisestamine
      <%
         err = hindamine2 and hindamine2.labiviija_id and hindamine and hindamine.labiviija_id and hindamine.labiviija_id != hindamine2.labiviija_id and 'is-invalid' or  ''
         hindaja_id = hindamine and hindamine.labiviija_id or jrg_labiviija_id
         hindaja2_id = hindamine2 and hindamine2.labiviija_id

         # arvutihinnatavate vastuste sisestamisel ei pea hindaja olema
         # sisestatud, siis antakse parameetriks empty=True
         # muudel juhtudel peab hindaja olema ja kui valikus on üksainus,
         # siis tema ongi
         if empty is None:
            empty = len(opt_hindajad) != 1
      %>
     <table cellpadding="0" cellspacing="0" class="showerr"${err}>
        <tr>
          <td>
##${hindamine and hindamine.id} ${hindaja_id}
            ${h.select('%s.labiviija_id' % prefix1, hindaja_id, opt_hindajad,
            wide=False, empty=empty, class_='inp_hindaja', tabindex=tabindex)}
            ##${hindamine.staatus_nimi}
          </td>
        </tr>
          % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <tr>
          <td>
            ${h.select('%s.labiviija_id' % prefix2, hindaja2_id, opt_hindajad,
            wide=False, empty=empty, class_='inp_hindaja', tabindex=tabindex)}
          </td>
        </tr>
          % endif
      </table>
</%def>

<%def name="kontroll_labiviija(opt_hindajad, vastvorm_kood,
                      prefix1, hindamine,
                      prefix2, hindamine2,
                      empty=True, jrg_labiviija_id=None, tabindex=None)">
## teise ühekordse hindaja sisestamine
      <%
         err = hindamine2 and hindamine2.kontroll_labiviija_id and hindamine and hindamine.kontroll_labiviija_id and hindamine.kontroll_labiviija_id != hindamine2.kontroll_labiviija_id and 'is-invalid' or  ''
         kontroll_hindaja_id = hindamine and hindamine.kontroll_labiviija_id or jrg_labiviija_id
         kontroll_hindaja2_id = hindamine2 and hindamine2.kontroll_labiviija_id
      %>
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
        <tr>
          <td>
            ${h.select('%s.kontroll_labiviija_id' % prefix1, kontroll_hindaja_id, opt_hindajad,
            wide=False, empty=empty, class_='inp_kontroll_hindaja', tabindex=tabindex)}
          </td>
        </tr>
          % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <tr>
          <td>
            ${h.select('%s.kontroll_labiviija_id' % prefix2, kontroll_hindaja2_id, opt_hindajad,
            wide=False, empty=empty, class_='inp_kontroll_hindaja', tabindex=tabindex)}
          </td>
        </tr>
          % endif
      </table>
</%def>

<%def name="intervjueerija(opt_intervjueerijad,
                           prefix1, hindamine,
                           prefix2, hindamine2,
                           tabindex=None)">
      <%
         err = hindamine2 and hindamine2.intervjuu_labiviija_id and hindamine and hindamine.intervjuu_labiviija_id and hindamine.intervjuu_labiviija_id != hindamine2.intervjuu_labiviija_id and 'is-invalid' or  ''
      %>
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
        <tr>
          <td nowrap>
            ${h.select('%s.intervjuu_labiviija_id' % prefix1,
            hindamine and hindamine.intervjuu_labiviija_id, opt_intervjueerijad,
            wide=False, empty=len(opt_intervjueerijad) != 1,
            class_='inp_intervjueerija', tabindex=tabindex)}
          </td>
        </tr>
         % if c.sisestus == 'p' and c.kahekordne_sisestamine:
        <tr>
          <td nowrap>
            ${h.select('%s.intervjuu_labiviija_id' % prefix2,
            hindamine2 and hindamine2.intervjuu_labiviija_id, opt_intervjueerijad,
            wide=False, empty=len(opt_intervjueerijad) != 1,
            class_='inp_intervjueerija', tabindex=tabindex)}
          </td>
        </tr>
         % endif
      </table>
</%def>
