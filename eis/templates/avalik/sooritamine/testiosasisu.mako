## Testiosa sooritamine
##
## Seda malli kasutatakse erinevates olukordades:
## - õpilane sooritab testiosa 
##       
## - õpilane vaatab peale sooritust oma vastuseid
##       c.read_only and c.olen_sooritaja
## - õpetaja vaatab õpilase vastuseid
##       c.read_only and c.hindaja
## - eksamikeskuse töötaja vaatab õpilase vastuseid
##       c.read_only and c.hindaja
## - õpetaja katsetab testi koostamise ajal testi sooritamist
##       c.preview and c.avalik
## - eksamikeskuse töötaja katsetab testi koostamise ajal testi sooritamist
##       c.preview
## - c.show_pallid - kas näidata palle
##
## On antud:
## - c.alatest - kui on alatest valitud
## - c.komplekt_id - valitud komplekt
<div class="testinst">
% if not c.read_only:
<div class="in-write in-test"></div>
% endif
<%  
   c.is_edit = True # vaatamise korral on c.read_only
   c.user.handler.prf()
   c.saved_color = '#EDFAF3'
   c.unsaved_color = '#FCEBF3'
%>
${self.before_main_form()}
${self.main_form()}
${self.next_form()}
</div>

<%def name="before_main_form()">
</%def>

<%def name="main_form()">
${h.form(url=c.submit_url, id="form_save_responses", multipart=True, method='post', autocomplete='off')}
${h.hidden('sop', '')}
${h.hidden('alatest_id', c.alatest_id or '')}
${h.hidden('next_alatest_id', '')}
% if c.lang:
${h.hidden('lang', c.lang)}
% endif
## current_ty_id on kasutusel test.js sees
${h.hidden('current_ty_id', '')}
% if not c.on_testivaline:
${self.header_table()}
% endif
${self.main_table()}
% if not c.read_only:
${h.hidden('trace', '')}
% endif

${self.footer_buttons()}

${h.end_form()}
</%def>

<%def name="header_table()">
${self.time_limits()}
${self.status_table()}
${self.instructions()}
</%def>

<%def name="time_limits()">
% if not c.read_only:
${self.time_limit_osa(c.testiosa)}
% if c.alatest_id:
${self.time_limit_ala(c.alatest)}
% endif
% endif
</%def>

<%def name="time_limit_osa(osa)">
<% l_max, l_ajakulu, l_left_max = c.piiraeg, c.ajakulu, c.kasutamata %>
% if l_max:
<div class="form-group mr-3 d-flex justify-content-end align-items-center ml-auto" id="countdown_testiosa">
  <% 
    l_hoiatus = osa.hoiatusaeg or 0
    showsec = osa.piiraeg_sek and 'true' or 'false'    
  %>
  <label class="mr-3 mb-0">${_("Testiosa max aeg")}:
    <span class="countdown-max">${h.str2_from_timedelta(l_max)}</span>
  </label>
  % if not c.read_only:
  <div class="circle-wrap">
    <span class="countdown-warn-msg" style="display:none">
      ${_("Testiosa lõpuni on jäänud alla {0} minuti")}
    </span>
  </div>
  <script>
              $(function(){
              (new CountDownA($('div#countdown_testiosa'), {
                 on_expire: expire_test,
                 limit: ${l_max},
                 warntime: ${l_hoiatus or 0},
                 leftmax: ${l_left_max},
                 show_seconds: ${showsec},
                 circle: true }
              )).start();
              });
  </script>
  % endif
</div>
% endif
</%def>

<%def name="time_limit_ala(osa)">
<%
  atos = c.alatestisooritused.get(osa.id)
  l_max = atos and atos.piiraeg
  l_left_max = atos and atos.kasutamata
%>
% if l_max:
<div class="form-group mr-3 d-flex justify-content-end align-items-center ml-auto" id="countdown_alatest">
  <% 
    l_hoiatus = osa.hoiatusaeg or 0
    showsec = osa.piiraeg_sek and 'true' or 'false'        
  %>
  <label class="mr-3 mb-0">${_("Alatesti max aeg")}:
    <span class="countdown-max">${h.str2_from_timedelta(l_max)}</span>
  </label>
  % if not c.read_only:
  <div class="circle-wrap">
    <span class="countdown-warn-msg" style="display:none">
      ${_("Alatesti lõpuni on jäänud alla {0} minuti")}
    </span>
  </div>
  <script>
              $(function(){
              (new CountDownA($('div#countdown_alatest'), {
                 on_expire: expire_test,
                 limit: ${l_max},
                 warntime: ${l_hoiatus or 0},
                 leftmax: ${l_left_max},
                 show_seconds: ${showsec},
                 circle: true }
              )).start();
              });
  </script>
  % endif
</div>
% endif
</%def>


<%def name="status_table()">
% if c.read_only and not c.hide_header_footer or c.hindamine:
<div class="question-status d-flex mb-4 toggle-content">
% if c.read_only and not c.hide_header_footer:          
  % if c.testiosa.naita_max_p:
  <div class="item mr-5">
    ${_("Sooritamise olek")}:
    <b>${c.sooritus.staatus_nimi}</b>
  </div>
  <div class="item mr-5">
    ${_("Hindamise olek")}:
    <b>${c.sooritus.hindamine_staatus_nimi}</b>
  </div>
  % endif
  
  % if (c.sooritus.pallid is not None or c.test.arvutihinde_naitamine) and c.show_sooritus_tulemus:
  <div class="item mr-5">
    ${_("Testiosa tulemus")}:
    <b>${c.sooritus.get_tulemus_eraldi()}</b>
  </div>
  % elif c.testiosa.naita_max_p:
  <div class="item mr-5">
    ${_("Maksimaalne hindepallide arv")}:
    <b>${h.fstr(c.testiosa.max_pallid)}</b>
  </div>
  % endif
  % if c.read_only and c.sooritus_ajakulu:
  <div class="item mr-5">
    ${_("Kasutatud aeg")}:
    <b>
      ${h.str2_from_timedelta(c.sooritus_ajakulu)}
    </b>
  </div>
  % endif
% endif

% if c.read_only:
  <% solekud = [r for r in c.sooritus.sisestusolekud if r.skann] %>
  % if len(solekud):
  <div class="item mr-5">
    ${_("Skannitud testitöö")}: 
    % for r in solekud:
    ${h.link_to(r.sisestuskogum.nimi,
    h.url('tulemus_skskann', sooritus_id=c.sooritus.id, id=r.id))}
    % endfor
  </div>
  % endif

  % if c.hindamine:
  ## mcomments
  <div class="item mr-5 ksm-naeb" style="display:none">
    ${h.checkbox('ksm_naeb_hindaja', 1, checked=c.hindamine.ksm_naeb_hindaja,
    label=_("Teised hindajad näevad avatud vastusesse märgitud vigu"))}
    ${h.checkbox('ksm_naeb_sooritaja', 1, checked=c.hindamine.ksm_naeb_sooritaja,
    label=_("Sooritaja näeb avatud vastusesse märgitud vigu"))}
  </div>
  % endif
% endif
</div>
% endif
</%def>

<%def name="instructions()">
% if c.test.testiliik_kood not in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_DIAG2) and not c.hide_header_footer and not c.test.diagnoosiv:
<%
  alatestid = [r for r in c.alatestid if (c.read_only or not r.testivaline)]
  alatestide_arv = len(alatestid)

  msgs = []
  if c.preview or c.olen_sooritaja and not c.read_only:
     if alatestide_arv > 0 and not c.alatest:
         ## mitme alatestiga test, ükski pole veel valitud, kuvatakse alatestide indeks
         msgs.append(_("Ülesannete lahendamiseks vali alatest. Kui soovid testisooritamist lõpetada, vajuta nupule <i>{end}</i>.")
                     .format(end=c.mitu_osa and _("Lõpetan testiosa sooritamise") or _("Lõpetan testi sooritamise")))
     else:
         if (c.alatest and c.alatest.yhesuunaline) or (alatestide_arv == 0 and c.testiosa.yhesuunaline):
             msgs.append(_("Lahenda testis olevad ülesanded. Pea meeles, et järgmisele ülesandele minnes enam eelmisele ülesandele tagasi minna ei saa."))
            
         else:
              msgs.append(_("Lahenda testis olevad ülesanded. Ülesannete vahel liikumiseks vajuta ülesande all nuppu <i>Tagasi</i> või <i>Edasi</i> või vali ülesanne lehekülje vasakus servas olevast tulbast."))

         if c.alatest and alatestide_arv > 1:
             if not c.alatest.yhesuunaline and not c.alatest.on_yhekordne:
                 msgs.append(_("Kui soovid alatestist väljuda, vali vasakust tulbast teine alatest."))
                 if not c.alatest.piiraeg:
                     msgs.append(_("Kogu testisooritamise ajal on sul võimalus juba lahendatud alatest uuesti avada ja vastamist jätkata."))
                 else:
                     msgs.append(_("Kogu testisooritamise ajal on sul võimalus juba lahendatud alatest uuesti avada ja vastamist jätkata, kuni alatesti piiraeg täis saab (alatesti piiraega arvestatakse ilma pausideta alates alatesti esmasest avamisest)."))

         if not c.alatest or c.testiosa.lopetatav:
             msgs.append(_("Kui oled veendunud, et kõik ülesanded on vastatud, vajuta nupule <i>{end}</i>. Sellega on sinu testisooritus lõppenud.")
                         .format(end=c.mitu_osa and _("Lõpetan testiosa sooritamise") or _("Lõpetan testi sooritamise")))
  msg = ' '.join(msgs)
%>
% if msg:
${h.alert_notice(msg, False)}
% endif
% endif
        
<% testiosa_sooritajajuhend = c.testiosa.sooritajajuhend %>
% if testiosa_sooritajajuhend:
  ${h.alert_info(testiosa_sooritajajuhend, False)}
% endif
      
<% alatest_sooritajajuhend = c.alatest and c.alatest.sooritajajuhend %>
% if alatest_sooritajajuhend:
  ${h.alert_info(alatest_sooritajajuhend, False)}
% endif
</%def>

<%def name="choose_variant()">
% if c.saab_valida_komplekti:
<%
     if c.teised_alatestid:
         onchange = "confirm_dialog_html($('span.variant-confirm').html(), function(){spinner_dlg_footer(this);change_variant();});"
     else:
         onchange = "set_spinner($('#variant_spinner'));change_variant();"

     if c.y1alatest1_id:
         variant_attr = f'data-showvarianty1a1="A{c.y1alatest1_id}" style="display:none"'
     else:
         variant_attr = ''
%>
  <div id="variant_choice" ${variant_attr}>
      <div class="rounded border mb-3 p-2 d-flex flex-wrap">
        ${h.flb(_("Vali ülesandekomplekt"), 'komplekt_id', 'p-1')}
        <div class="mr-3">
            % if c.teised_alatestid:
            <span class="variant-confirm" style="display:none">
              ${_("Teise komplekti valimise korral tuleb uuesti sooritada ka varasemad alatestid:")}
              <ul>
              % for r in c.teised_alatestid:
              <li>${r}</li>
              % endfor
              </ul>
              ${_("Kas oled kindel, et soovid valida teise komplekti?")}
            </span>
            % endif
            ${h.select('komplekt_id', c.komplekt_id, c.opt_komplekt, wide=False, onchange=onchange)}
        </div>
        <div id="variant_spinner"></div>
      </div>
    </div>
% endif
</%def>          

<%def name="next_form()">
## seda vormi kasutatakse hindamisel järgmise töö valimise vormi jaoks
</%def>

<%def name="main_table()">
<%
  on_alatestid = bool(c.alatestid)
  y_alatestid = [r for r in c.alatestid if not r.testivaline]
  next_alatest_id = None

  # alatesti ei kuva siis, kui testis on 1 ülesannete alatest
  # ja 1 testiväline kysitluse alatest ning ülesannete alatest on jooksvalt valitud
  # ning käib sooritamine
  c.hide_curr_alatest_title = len(c.alatestid) == 2 and not c.read_only and c.alatest and len(y_alatestid) == 1 and y_alatestid[0].id == c.alatest.id
  horizontal = False
  if c.read_only or c.is_linear:
     is_taskbar = True
  elif c.alatest and c.alatest.testivaline:
     is_taskbar = False
  elif c.testiosa.pos_yl_list == const.POS_NAV_HIDDEN and (not on_alatestid or c.alatest):
     # yl riba ei ole ja seda pole vaja ka alatesti valimiseks
     is_taskbar = False
  else:
     is_taskbar = True
%>

${self.kogumid()}

% if not is_taskbar:
## alatestide ja ylesannete loetelu ei kuvata
<div style="display:none">
  ${self.nav_bar(False, c.alatestid, c.testiylesanded, c.komplekt_id, next_alatest_id)}
</div>
${self.task_contents()}
% else:
<div class="d-flex">
  <div class="wizard-vertical-taskbar">
    ${self.nav_bar(False, c.alatestid, c.testiylesanded, c.komplekt_id, next_alatest_id)}
  </div>
  <div class="ml-3 flex-grow-1">
    ${self.task_contents()}
  </div>
</div>
% endif
% if not c.ty:
${self.task_buttons()}
% endif
</%def>

<%def name="nav_bar(horizontal, alatestid, testiylesanded, komplekt_id, next_alatest_id=None)">
## ylesannete loetelu lehe päises
<%
  if horizontal:
     if alatestid:
        cls = 'wizard-nav'
     else:
        cls = 'wizard-nav-long'
     cls += ' wizard-horizontal'
     if testiylesanded:
        cls += ' toggle-content mb-4'
     else:
        cls += ' mb-0' 
  else:
     cls = 'wizard-vertical'
%>
<div class="wizard-nav ${cls} d-none d-md-block">
  <ul class="nav">
  % if alatestid:
    % for alatest in alatestid:
       % if c.alatest_id == alatest.id:
          ${self.nav_alatest(horizontal, alatest, testiylesanded, komplekt_id, next_alatest_id)}
       % elif c.read_only or not alatest.testivaline:
          ${self.nav_alatest(horizontal, alatest, [], komplekt_id, next_alatest_id)}
       % endif
    % endfor
  % else:
   % for ty in testiylesanded:
       ${self.nav_task(horizontal, ty, komplekt_id)}
   % endfor
  % endif
  </ul>
</div>
</%def>

<%def name="nav_alatest(horizontal, alatest, testiylesanded, komplekt_id, next_alatest_id)">
<% 
    permitted = False
    atos = c.alatestisooritused and c.alatestisooritused.get(alatest.id) or {}
    if c.sooritus_staatus == const.S_STAATUS_POOLELI:
        if atos and atos.piiraeg:
           kasutamata_aeg = atos.kasutamata or 0
           permitted = kasutamata_aeg > 0
        else:
           permitted = True
        if alatest.on_yhekordne and atos and atos.staatus == const.S_STAATUS_TEHTUD:
           permitted = False
        if c.testiosa.yhesuunaline and not c.preview and alatest.id != next_alatest_id:
           # yhesuunalises testis ei saa ise alatesti valida, need läbitakse järjest
           permitted = False
    elif c.read_only:
        # peale testi toimumist vaadatakse testi
        permitted = True

    is_title = not c.hide_curr_alatest_title

    status = atos and c.opt.S_STAATUS.get(atos.staatus) or ''
    if status:
        status = status.lower()
        if (c.alatest != alatest or c.read_only) and not alatest.testivaline and atos and atos.tehtud_yl_arv is not None and atos.yl_arv:
           status += ' %d/%d' % (atos.tehtud_yl_arv, atos.yl_arv)
    
    href = None
    msg = ''
    if is_title:
       if c.alatest != alatest and c.read_only:
          ## teise alatesti vaatamine
          href = c.url_to_alatest(alatest)
       elif c.alatest != alatest and permitted:
          href = c.url_to_alatest(alatest)
          ## teise alatesti sooritamine
          if c.alatest:
             ## salvestada jooksva alatesti vastus ning avada uus alatest
             msg = ''
             if alatest.on_yhekordne and c.testiosa.ala_lahk_hoiatus:
                   msg += _("Seda alatesti saab avada üheainsa korra.") + ' '
             if c.alatest.on_yhekordne and c.testiosa.ala_lahk_hoiatus:
                   msg += _("Peale järgmise alatesti avamist ei saa enam praegust alatesti uuesti avada.") + ' '
             if msg:
                   msg += _("Kas oled kindel, et soovid avada uue alatesti?")
          elif not c.read_only:
             ## avada uus alatest sooritamiseks
             if alatest.on_yhekordne and c.testiosa.ala_lahk_hoiatus:
                 msg = _("Seda alatesti saab avada üheainsa korra. Kas oled kindel, et soovid seda praegu teha?")
    if c.alatest_id == alatest.id:
        current_cls = 'current'
        active_cls = 'active'
    else:
        current_cls = active_cls = ''
        if not href:
           current_cls += ' disabled-click'
        if atos and atos.lopetatud_yl_arv is not None and atos.yl_arv is not None:
           if atos.lopetatud_yl_arv < atos.yl_arv:
               active_cls = 'responded'
           else:
               active_cls = 'rfinished'
    title = alatest.tahis and '%s %s' % (_("alatest"), alatest.tahis) or alatest.nimi
    if not c.read_only and href:
        # sooritamise ajal ei kasuta hrefi, vaid alatesti ID
        href = ''
%>
       <li class="nav-item ${current_cls} nav-alatest" role="presentation" id="ala_${alatest.id}">
         <a href="${href}" class="nav-link d-flex ${active_cls}" data-label="${title}">
            <span class="task-no">${alatest.tahis}</span>
            <span class="label">
              <span class="label-text">
                ${alatest.tran(c.lang).nimi}
                % if not horizontal and not alatest.testivaline:
                   % if atos and atos.pallid is not None and c.show_alatestitulemus:
                <small>${h.fstr(atos.pallid)}p
                </small>
                   % elif c.testiosa.naita_max_p and alatest.max_pallid:
                <small>${_("max {p}p").format(p=h.fstr(alatest.max_pallid))}</small>
                   % endif
                   % if status:
                <small>(${status})</small>
                   % endif
                % endif
              </span>
              % if msg:
              <span class="confirm" style="display:none">${msg}</span>
              % endif
            </span>
          </a>
          % if not horizontal and testiylesanded:
          <ul class="nav">
            % for ty in testiylesanded:
             ${self.nav_task(horizontal, ty, komplekt_id, alatest)}
            % endfor
          </ul>
          % endif
        </li>
</%def>

<%def name="nav_task(horizontal, ty, komplekt_id, alatest=None)">
<%
   ylesandevastus = c.ylesandevastused.get(ty.id)
   ty_tahis = c.sooritusjrk and c.sooritusjrk.get(ty.id) or ty.tahis
   ty_nimi = c.testiosa.kuva_yl_nimetus and ty.nimi or ty.liik_nimi
   navty_id = 'navty_%s' % (ty.id)
   yhesuunaline = (c.test.diagnoosiv or not alatest and c.testiosa.yhesuunaline or alatest and alatest.yhesuunaline) and not c.is_linear and not c.read_only
   vy_id = ylesandevastus and ylesandevastus.valitudylesanne_id
   vy = None
   for vy in ty.valitudylesanded:
      if vy.id == vy_id or not vy_id:
         vy_id = vy.id
         break

   resp_cls = ''
   if not vy:
      model.log.error(f'TESTI {c.test.id} KOMPLEKT {komplekt_id} EI SISALDA TY {ty.id}')
      resp_cls = 'error' 
   else:
      ylesanne_id = vy.ylesanne_id
      if ylesandevastus:
        if c.read_only and ylesandevastus.pallid is not None and c.show_yl_oige:
          if not ylesandevastus.valede_arv and ylesandevastus.pallid == ylesandevastus.max_pallid:
             resp_cls = 'responded-correct'
          else:
             resp_cls = 'responded-incorrect'
        else:
          if not ylesandevastus.vastuseta:
             resp_cls = 'responded'
          if ylesandevastus.lopetatud:
             resp_cls += ' rfinished'
   active_cls = current_cls = ''
   if yhesuunaline or not vy:
      current_cls += ' disabled-click'
   if c.read_only:
      task_url = h.url_current('showtask', ty_id=ty.id)
   else:
      task_url = h.url_current('edittask', ty_id=ty.id)

   # title väikese algustähega, sest neid kasutatakse vastamata jäänud ülesannete loetlemisel lauses
   if ty_tahis:
      title = _("ülesanne") + ' ' + ty_tahis
   else:
      map_l = {const.TY_LIIK_K: 'mdi-file-question', # kysimustik
               const.TY_LIIK_T: 'mdi-label', # tiitel 
               const.TY_LIIK_E: 'mdi-fruit-cherries', # näide (grapes?)
               const.TY_LIIK_G: 'mdi-information-variant'} # juhend
      icon = map_l.get(ty.liik) or 'mdi-fruit-pineapple'
      ## title on kasutusel testi lõpetamise nupul lõpetamata ylesannete viitamisel,
      ## vt test.js:list_unfinished()
      if ty.liik == const.TY_LIIK_K:
         title = _("küsimustik")
      else:
         title = ''
%>
        <li class="nav-item ${current_cls} tr_ylesanne nav-task" role="presentation" id="${navty_id}" data-href="${task_url}">
          <a href="#" class="nav-link d-flex ${active_cls} ${resp_cls}" data-label="${title}">
            <div class="task-no">
              ${ty_tahis or h.mdi_icon(icon)}
            </div>
            <div class="label">
              <span class="label-text">
                ${ty_nimi}
                % if not horizontal and c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and ty.liik == const.TY_LIIK_Y:
                <small>
                  % if ty.max_pallid:
                  % if ylesandevastus and ylesandevastus.pallid is not None and (c.show_ylesandetulemus or c.app_ekk and c.linear):
                  ${ylesandevastus.get_tulemus()}
                  % elif ty.naita_max_p:
                  ${_("max {p}p").format(p=h.fstr(ty.max_pallid))}
                  % endif
                  % endif
                </small>
                % endif
              </span>
            </div>
          </a>
        </li>
</%def>

<%def name="task_contents()">
<div>
  ${self.choose_variant()}
</div>

% if c.ty:
<div class="testtys tools-null">
  <div class="testtys-before">
  </div>
  <%
    if c.read_only:
       task_url = h.url_current('showtask', ty_id=c.ty.id)
    else:
       task_url = h.url_current('edittask', ty_id=c.ty.id)
  %>
  <iframe name="itask1" class="ylesanne" src="${task_url}"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>
  <iframe name="itask2" class="tmptask"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>
  <div class="testtys-after">
    ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner m-3', hide=False)}
  </div>
  ${self.task_buttons()}
</div>
% endif
</%def>

<%def name="footer_buttons()">
## üle laadimiseks
</%def>

<%def name="task_buttons()">
<%
  if c.test.diagnoosiv and not c.read_only and not c.is_linear:
     # eelmisele minna ei saa ja järgmise ID pole teada
     yhesuunaline = True
  else:
     # leiame eelmise ja järgmise ylesande ID 
     yhesuunaline = (not c.alatest and c.testiosa.yhesuunaline) or (c.alatest and c.alatest.yhesuunaline)
     
  div_cls = ''
  if c.testiosa.yl_lahendada_lopuni and not c.read_only:
     div_cls = 'finish-all-task finish-task'

  tylist = ','.join([str(ty.id) for ty in c.testiylesanded])

  ## kas jooksev alatest on viimane alatest testiosas
  is_last_alatest = False
  ## kas on võimalik minna eelmisele alatestile
  prev_alatest_id = None
  if c.alatest and not c.read_only and not c.on_testivaline:
         is_last_alatest = True
         for alatest in c.alatestid:
             if alatest.seq > c.alatest.seq and (c.read_only or not alatest.testivaline):
                is_last_alatest = False
                break
             if alatest.seq == c.alatest.seq - 1 and not alatest.on_yhekordne and not c.testiosa.yhesuunaline:
                # eelmisele alatestile on võimalik tagasi minna
                prev_alatest_id = alatest.id
%>

<div id="footerbuttonsdiv" data-tylist="${tylist}" class="d-flex flex-wrap mb-3">

## VASAKU SERVA NUPUD
% if c.ty:
% if c.read_only:
    <div class="iframe-loaded">
      ${h.button(_("Tagasi"), onclick="ty_show(null,null,{nfwd:-1})", id='bprev', level=2, mdicls='mdi-arrow-left-circle')}
    </div>
% elif not c.on_testivaline:
    ## iframe-loaded peita siis, kui pooleli ylesandelt ei lubata edasi minna ja ylesanne on pooleli
    <div class="iframe-loaded ${div_cls}" style="display:none">
      ## move-prev-next-task peita siis, kui:
      ## pooleli ylesandelt ei lubata edasi minna ja ylesanne on pooleli (iframe-loaded kaudu) või 
      ## pooleli ylesandelt ei lubata edasi minna ja lõpetamisel on automaatne edasiminek
      <span class="hide-ft-forcenext">
      % if not yhesuunaline:
        ${h.button(_("Tagasi"), onclick="ty_show(null,null,{nfwd:-1})", level=2, id='bprev', mdicls='mdi-arrow-left-circle')}

        % if (not c.test.diagnoosiv or c.is_linear) and c.alatest and not c.alatest.on_yhekordne and prev_alatest_id and not c.testiosa.yhesuunaline:
           ## on-first-task kuvada mitte-esimese alatesti esimese ylesande juures
           <span class="on-first-task" style="display:none">
              ${h.button(_("Tagasi"), onclick="end_alatest(%d)" % prev_alatest_id, level=2, mdicls='mdi-arrow-left-circle')}
           </span>
        % endif
      
      % endif
      </span>
     </div>
% endif
% endif
    
## KESKMINE OSA
    <div class="flex-grow-1">
    <div class="d-flex mx-3">
      ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner mx-3', hide=True)}
      <div class="taskloaderror mx-3" style="display:none" title="${_("Ühenduse viga, palun proovi uuesti")}">
        ${h.mdi_icon('mdi-information text-danger')}
      </div>
    </div>
    </div>
    
## PAREMA SERVA NUPUD
% if c.ty:
% if c.read_only:
    <div class="iframe-loaded">
      ${h.button(_("Edasi"), onclick="ty_show(null,null,{nfwd:1})", id='bnext', mdicls2='mdi-arrow-right-circle')}
    </div>
% elif c.on_testivaline:
    ${h.button(_("Lõpetan vastamise"), onclick="end_test();")}
% else:
    ## iframe-loaded peita siis, kui pooleli ylesandelt ei lubata edasi minna ja ylesanne on pooleli
    <div class="iframe-loaded ${div_cls}" style="display:none">
      ## move-prev-next-task peita siis, kui:
      ## pooleli ylesandelt ei lubata edasi minna ja ylesanne on pooleli (iframe-loaded kaudu) või 
      ## pooleli ylesandelt ei lubata edasi minna ja lõpetamisel on automaatne edasiminek
      <span class="hide-ft-forcenext">
              <%
                 onclick = onclick1 = "ty_show(null,null,{nfwd:1});"
                 if yhesuunaline and (c.testiosa.yl_lahk_hoiatus or c.testiosa.yl_pooleli_hoiatus):
                    msg = _("Kui sa liigud järgmisele ülesandele, siis sellele ülesandele enam tagasi minna ei saa. Kas soovid liikuda järgmisele ülesandele?")
                    onclick = "confirm_dialog_yesno('%s', function(){close_this_dialog(this);%s});return false;" % (msg, onclick1)      
                    if c.testiosa.yl_pooleli_hoiatus and not c.testiosa.yl_lahk_hoiatus:
                       onclick = "if($(this).closest('div.div_ty').attr('data-finished')=='true'){%s} else %s" % (onclick1, onclick)
              %>
           % if c.test.diagnoosiv and not c.is_linear:
              ## d-testis on järgmise yl nupp alati nähtav   
              ${h.button(_("Edasi"), onclick=onclick, mdicls2='mdi-arrow-right-circle')}
           % else:
              ## järgmise yl nupp nähtav ainult siis, kui pole viimane yl   
              ${h.button(_("Edasi"), onclick=onclick, id='bnext', mdicls2='mdi-arrow-right-circle')}
           % endif
      </span>
      % if not c.test.diagnoosiv or c.is_linear:
           ## on-last-task peita siis, kui:
           ## eesolev ylesanne pole viimane
           ## või kui pooleli ylesandelt ei lubata edasi minna ja ylesanne on pooleli (iframe-loaded kaudu)
           <span class="on-last-task" style="display:none">
              ## kuvada siis, kui järgmist ylesannet ei ole
              
           % if c.alatest and c.alatest.on_yhekordne and c.testiosa.ala_lahk_hoiatus:
              <%
                 onclick = "end_alatest('');"
                 msg = _("Seda alatesti ei saa peale lõpetamist uuesti avada. Kas oled kindel, et soovid alatesti praegu lõpetada?") 
                 onclick = "confirm_dialog('%s', function(){spinner_dlg_footer(this);%s});return false;" % (msg, onclick)      
              %>
              ${h.button(_("Lõpetan alatesti sooritamise"), onclick=onclick)}

           % elif c.alatest and not is_last_alatest:
              ${h.button(_("Edasi"), onclick="end_alatest('')", mdicls2='mdi-arrow-right-circle')}
           % endif
           </span>
        % endif
     </div>
% endif
## if c.ty lõpp
% endif    

## VEEL PAREMA SERVA NUPPE
    <div class="pr-3">
      % if c.read_only:
      % if c.url_back_post:
      ## testi eelvaade
      ${h.btn_to(_("Välju testist"), c.url_back_post, method='post', spinnerin=True, level=2)}
      % elif c.url_back:
      ${h.btn_to(_("Välju testist"), c.url_back, level=2)}
      % endif
      % elif not c.on_testivaline:

      % if c.testiosa.lopetatav or (not c.alatest and c.testiosa.on_alatestid):
      ## kui on lõpetatav või kui oleme alatestidega testi alatestide indeksis
      ${h.button(c.mitu_osa and _("Lõpetan testiosa sooritamise") or _("Lõpetan testi sooritamise"), 
                 onclick="end_test();", level=2)}
      % elif not c.test.diagnoosiv and (not c.alatest or (c.alatest and is_last_alatest)):
      <span class="on-last-task" style="display:none">
        ${h.button(c.mitu_osa and _("Lõpetan testiosa sooritamise") or _("Lõpetan testi sooritamise"), 
                   onclick='end_test();')}
      </span>
      % endif
      % if c.testiosa.katkestatav:
      ${h.button(c.mitu_osa and _("Katkestan testiosa sooritamise") or _("Katkestan testi sooritamise"), 
                 onclick="cancel_test();", level=2)}
      % endif
      % endif
    </div>

## footerbuttonsdiv lõpp
</div>
</%def>

<%def name="kogumid()">
## eksperthindamise korral kasutusel hindamiskogumite indeksi kuvamiseks
</%def>

% if c.test.diagnoosiv:
<div class="end-of-test" style="display:none;text-align:center;">
  <div class="end-of-test-title" style="display:none">${_("Testi lõpp")}</div>
  <p class="end-of-test-text">${_("Tubli! Oled jõudnud testi lõppu!")}</p>
  <span class="endbtn-text" style="display:none">
  % if c.tulemus_avaldet:
  ${_("Vaata tagasisidet")}
% else:
  ${_("Lõpeta test")}
  % endif
  </span>
</div>
% endif
