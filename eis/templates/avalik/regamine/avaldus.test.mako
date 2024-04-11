## avaldus.testid.mako testide valimise tabelis ühe testimiskorra rida
<%
         rcd = c.testimiskord
         c.test = rcd.test
         inputstyle = not c.sooritaja and 'style="display:none"' or ''

         available = True
         disabled = False
         if c.sooritaja:
            disabled = not c.sooritaja.voib_reg()
         elif rcd.reg_kohavalik and c.test.testiliik_kood == const.TESTILIIK_SISSE \
            and rcd.reg_sooritaja_alates > model.date.today() - model.timedelta(days=2):
            # kohavalikuga sisseastumiseksamile võivad esimesel kahel päeval
            # kandideerida ainult oma õpilased
            o_koht_id = c.opilane and c.opilane.koht_id or None
            if not o_koht_id:
               # pole õpilane
               opt_kohtaeg = []
            else:
               opt_kohtaeg = c.regpiirang.get_kohtaeg_opt(request.handler, c.testimiskord.id, o_koht_id)
            if not opt_kohtaeg:
               # oma kool pole soorituskohtade seas
               available = False

%>
% if available:
<div class="bg-gray-50 px-3 py-2 my-2">
    <%include file="/common/message.mako"/>
    ## kogu testi kohta käiva vea kuvamise koht
    ${h.hidden(f'err_{rcd.id}', '')}

    <div class="row">
      <%
            valitud = c.sooritaja and c.sooritaja.staatus != const.S_STAATUS_TYHISTATUD
            kinnitatud = c.sooritaja and c.sooritaja.staatus >= const.S_STAATUS_TASUMATA
            checked = valitud or c.test_id and c.test.id == int(c.test_id)
            cls = 'valik_id'
            if valitud:
                delurl = h.url_current('delete', testiliik=c.testiliik, id=rcd.id, sooritaja_id=c.sooritaja.id)
            else:
                delurl = None
            if kinnitatud:
                cls += ' reg-kinnitatud'
      %>
      <div class="col-sm-12 col-md-12 col-lg-${rcd.reg_sooritaja and 6 or 9}">
        ## testi valimise märkeruut
        % if c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
        <% if valitud: cls += ' is-checked' %>
        ${h.radio('valik_id', rcd.id, class_=cls, checked=checked, href=delurl, label=c.test.nimi, disabled=disabled)}
        % else:
        ${h.checkbox('valik_id', rcd.id, class_=cls, checked=checked, href=delurl, label=c.test.nimi, disabled=disabled)}
        % endif
        % if disabled and checked:
        ${h.hidden('valik_id', rcd.id, id=f"_valik_id_{rcd.id}")}
        <script>
          ## et vigade kuvamisel jääks õige väärtus
          $('#_valik_id_${rcd.id}').val("${rcd.id}");
        </script>
        % endif
        % if c.sooritaja:
        <span class="pl-3">
          % if c.sooritaja.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
          ${h.badge_success(c.sooritaja.staatus_nimi)}
          % elif c.sooritaja.staatus == const.S_STAATUS_TYHISTATUD:
          ${h.badge_secondary(c.sooritaja.staatus_nimi)}
          % elif c.sooritaja.staatus < const.S_STAATUS_REGATUD:
          ${h.badge_danger(c.sooritaja.staatus_nimi)}
          % else:
          ${h.badge_primary(c.sooritaja.staatus_nimi)}                     
          % endif
         </span>
        % endif
      </div>
      % if rcd.reg_sooritaja:
      <div class="col-sm-6 col-md-6 col-lg-3 pl-5 pl-lg-1">
        ${h.flb(_("Registreerimise periood"))}
        <div>
          ${h.str_from_date(rcd.reg_sooritaja_alates)} - ${h.str_from_date(rcd.reg_sooritaja_kuni)}
        </div>
      </div>
      % endif
      <div class="col-sm-6 col-md-6 col-lg-3 pl-5 pl-lg-1">          
        ${h.flb(_("Toimumise aeg"))}
        <div>
          <% toimumisajad = list(c.testimiskord.toimumisajad) %>
          % for ta in toimumisajad:
          % if len(toimumisajad) > 1:
            <div>
              ${ta.testiosa.nimi}
              ${ta.millal}
            </div>
          % else:
            ${ta.millal}
          % endif
          % endfor
         </div>
      </div>
    </div>
    % if c.testimiskord.reg_piirang == const.REGPIIRANG_H:
    <div class="pl-4">
      <strong>NB! Sellele eksamile registreerimisega annan nõusoleku küsida Eesti Hariduse Infosüsteemist minu töötamise andmed.</strong>
    </div>
    % endif
    <div class="rowinput-${rcd.id} pl-4" ${inputstyle}>
      ${h.rqexp()}
      <div class="pl-1">
        <%
            c.tsuffix = f'_{rcd.id}'
            c.reg_sooritaja = True
        %>
        <%include file="/avalik/regamine/avaldus.testiseaded.mako"/>
      </div>
    </div>
</div>
% endif
