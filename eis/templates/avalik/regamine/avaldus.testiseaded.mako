<%
   # peavad olema: c.tsuffix, c.kasutaja, c.opilane, c.testimiskord, c.test
   # olemasoleva reg korral ka: c.sooritaja
   # vastavalt regajale kas c.reg_sooritaja=True või c.reg_kool=True
  
   suffix = c.tsuffix
   kasutaja = c.kasutaja
   testimiskord = c.testimiskord
   test = c.test
   opt_kursused = test.opt_kursused
   if c.sooritaja:
      koht_maaratud = (c.sooritaja.staatus > const.S_STAATUS_REGATUD) \
           and (len([tos.testiruum_id for tos in c.sooritaja.sooritused if tos.testiruum_id]) > 0)
      if c.reg_sooritaja:
           # sooritaja ise muudab oma andmeid
           voib_reg = c.sooritaja.voib_reg()
           voib_muuta = voib_reg
      elif c.reg_kool:
           # kool muudab
           on_kogused = len([r.id for r in c.testimiskord.toimumisajad if r.on_kogused])
           voib_muuta = c.sooritaja.muutmatu != const.MUUTMATU_MUUTMATU
           voib_reg = not on_kogused and voib_muuta
           if not voib_reg and voib_muuta and c.testimiskord and c.testimiskord.reg_kohavalik:
              # kui on kohavalikuga regamine ja regada enam ei või, siis ei või ka piirkonda muuta
              voib_muuta = False
   else:
      koht_maaratud = False
      voib_reg = voib_muuta = True

   # kas on midagi muuta ja peab tegema submit nupu
   c.voib_muuta = False
   vanus = kasutaja.vanus
   voib_vabastada_k = test.testiliik_kood == const.TESTILIIK_TASE and test.on_testitase(const.KEELETASE_B1) \
      and vanus and vanus >= 65 and kasutaja.kodakond_kood != const.RIIK_EST

   # piirkond valitakse siis, kui on TE/SE või kui varemlõpetanud regab end riigieksamile
   varemlopetanu = not c.opilane or c.opilane.on_lopetanud
   on_prk = test.testiliik_kood in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS) \
      or test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV) and varemlopetanu
%>
<div id="testiseaded${suffix}" class="my-1">
          % if testimiskord:
          <div class="form-group row">
            ${h.flb3(_("Soorituskeel"), rq=True)}
            <div class="col">
              <% opt_lang = testimiskord.opt_keeled %>
              % if len(opt_lang) > 1 and not koht_maaratud and voib_reg:
              ${h.select(f'lang{suffix}', c.sooritaja and c.sooritaja.lang or None, opt_lang)}
              <% c.voib_muuta = True %>
              % elif c.sooritaja:
              ${c.sooritaja.lang_nimi}
              ${h.hidden(f'lang{suffix}', c.sooritaja.lang)}
              % else:
              ${opt_lang[0][1]}
              ${h.hidden(f'lang{suffix}', opt_lang[0][0])}
              % endif
            </div>
          </div>
          % endif
          
          % if opt_kursused:
          <div class="form-group row">
            ${h.flb3(_("Kursus"), rq=True)}
            <div class="col">
              ${h.select(f'kursus{suffix}', c.sooritaja and c.sooritaja.kursus_kood or None, opt_kursused, readonly=not voib_reg)}
              <% c.voib_muuta |= len(opt_kursused) > 1 and voib_reg %>              
            </div>
          </div>
          % endif

          % if testimiskord and testimiskord.reg_kohavalik:
          ## gymn sisseastumistest, saab valida soorituskoha

          <%
          # kui o_koht_id on väärtustatud, siis on see ainus kool, mida saab soorituskohaks valida
          o_koht_id = o_koht_msg = None
          if voib_reg and c.reg_sooritaja and test.testiliik_kood == const.TESTILIIK_SISSE:
             # kohavalikuga sisseastumiseksamile võivad esimesel kahel päeval
             # kandideerida ainult oma õpilased
             reg_alates = testimiskord.reg_sooritaja_alates
             if reg_alates > model.date.today() - model.timedelta(days=2):
                o_koht_id = c.opilane and c.opilane.koht_id or -1
                o_koht_msg = _("{d1} - {d2} saab testi sooritamise kohaks valida ainult enda kooli. Alates {d3} saab valida kõiki koole, kus on vabu kohti.").format(
                   d1=h.str_from_date(reg_alates),
                   d2=h.str_from_date(reg_alates+model.timedelta(days=1)),
                   d3=h.str_from_date(reg_alates+model.timedelta(days=2)))
          
          # soorituskohtade ja -aegade valik
          opt_kohtaeg = c.regpiirang.get_kohtaeg_opt(request.handler, testimiskord.id, o_koht_id)

          ## kui saab valida soorituskohta ja soorituskohaks saab valida ainult oma kooli,
          ## siis ei ole vaja piirkonna valikut
          on_prk = False
          if not o_koht_id and not koht_maaratud and testimiskord and voib_muuta:
             c.piirkond_id = c.sooritaja and c.sooritaja.piirkond_id or None
             c.piirkond_field = f'piirkond_id{suffix}'
             c.piirkond_filtered = testimiskord.get_piirkonnad_id()
             if not c.piirkond_filtered and testimiskord.reg_kohavalik:
                 # piirame piirkondade valiku nendega, mis on soorituskohtade valikus olemas
                 li = []
                 for key, label, attrs in opt_kohtaeg:
                     sprk = attrs.get('data-piirkond') or ''
                     li.extend([int(n) for n in sprk.split(',') if n])
                 c.piirkond_filtered = list(set(li))
             on_prk = c.piirkond_filtered and len(c.piirkond_filtered) > 1
          %>

          % if on_prk:
          ## piirkonna valikut ei salvestata, see on ainult soorituskoha valiku lihtsustamiseks
          <div class="form-group row">
            ${h.flb3(_("Piirkond"))}
            <div class="col">
              <%
                c.piirkond_field = f'_piirkond_id{suffix}'
                c.piirkond_suffix = suffix
                c.piirkond_maxtase = 1
              %>
              <%include file="/admin/piirkonnavalik.mako"/>
            </div>
          </div>
          % endif

          <div class="form-group row">
            ${h.flb3(_("Soorituskoht"), rq=True)}
            <div class="col">
              % if voib_reg:
              <%             
                value = c.regpiirang.get_kohtaeg(request.handler, c.sooritaja)
                c.voib_muuta = True
                value1 = label1 = None

                opt_valitavad = [r for r in opt_kohtaeg if not r[2] or not r[2].get('disabled')]
                if len(opt_valitavad) == 1 and (not value or (value == opt_valitavad[0][0])):
                   value1 = opt_kohtaeg[0][0]
                   label1 = opt_kohtaeg[0][1]
              %>
              % if value1:
              ${h.hidden(f'kohtaeg{suffix}', value1)}
              ${label1}
              % else:
              ${h.select(f'kohtaeg{suffix}', value, opt_kohtaeg, empty=True, class_="kohtaeg")}
              % endif
              % if o_koht_id:
              <div>${o_koht_msg}</div>
              % endif
              <script>
                ## piirkonna valiku muutmisel peita need soorituskohad, mis pole valitud piirkonnas
                $('#testiseaded${suffix} .prk_id').change(function(){
                 if($(this).is(':visible')){
                    var options = $('#kohtaeg${suffix}').find('option'), prk_id = $(this).val();
                    options.each(function(){
                       var my_prk = $(this).attr('data-piirkond') || '';
                       $(this).toggle(this.value == ''||prk_id == ''||my_prk.indexOf(','+prk_id+',') > -1);
                    });
                  }
                });
                ## lehe avamisel peita need soorituskohad, mis pole algselt valitud piirkonnas
                $(function(){
                    var options = $('#kohtaeg${suffix}').find('option'), prk_id = $('#_piirkond_id${suffix}').val();
                    if(prk_id)
                    options.each(function(){
                       var my_prk = $(this).attr('data-piirkond') || '';
                       $(this).toggle(this.value == ''||prk_id == ''||my_prk.indexOf(','+prk_id+',') > -1);
                    });
                });
                % if value:
                  ## soorituskohad, kus enam pole vabu kohti, on disabled
                  ## kuid kui sooritaja on juba varem selle koha valinud, siis tema jaoks see pole disabled
                $('#kohtaeg${suffix}').find('option[value="${value}"]').prop('disabled', false);
                % endif
              </script>
              % else:
              <%
                try:
                   value, koht_nimi, aeg = c.regpiirang.get_kohtaeg(request.handler, c.sooritaja, True)
                except:
                   value = koht_nimi = aeg = ''
              %>
              <div>
                ${koht_nimi} ${aeg}
                ${h.hidden(f'kohtaeg{suffix}', value)}
              </div>
              % endif
            </div>
          </div>

          % elif on_prk:
          ## pole soorituskoha valikuga regamine ja peab valima piirkonna
          <div class="form-group row">
            ${h.flb3(_("Piirkond"), rq=True)}
            <div class="col">
            % if not koht_maaratud and testimiskord and voib_muuta:
            <%
               c.piirkond_id = c.sooritaja and c.sooritaja.piirkond_id or None
               c.piirkond_field = f'piirkond_id{suffix}'
               c.piirkond_suffix = suffix
               c.piirkond_filtered = testimiskord.get_piirkonnad_id()
               c.piirkond_maxtase = 1
               c.voib_muuta = True
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
            <script>
              ## konsultatsiooni võimalus sõltub piirkonna valikust
              $('input#${c.piirkond_field}').change(function(){
                var ts = $('#testiseaded${suffix}');
                var k = ts.find('.konsprk[data-prk="' + this.value + '"]');
                if(k.length){
                  ts.find('.konsprk').addClass('d-none');
                  k.removeClass('d-none');
                  ts.find('.kons').removeClass('d-none');
                } else {
                  ts.find('.soovib').prop('checked', false);
                  ts.find('.konst').hide();
                  ts.find('.kons').addClass('d-none');
                }
              });
            </script>
            % else:
            ${c.sooritaja.piirkond_nimi}
            % endif
            </div>
          </div>
          
          % endif
          
          % if test.testiliik_kood == const.TESTILIIK_SISSE and testimiskord.reg_kohavalik:
          ## gymn sisseastumistest
          <% regkohad = list(testimiskord.regkohad) %>
          % if regkohad:
          <div class="form-group row">
            % if c.reg_sooritaja:
            ${h.flb3(_("Õppeasutused, kuhu kandideerin ja millele avaldatakse testitulemused"), rq=True)}
            % else:
            ${h.flb3(_("Õppeasutused, kuhu kandideerib ja millele avaldatakse testitulemused"), rq=True)}
            % endif
            <div class="col">
              <%
                # oma kool
                koht_id = c.opilane and c.opilane.koht_id
                # kas oma koolil on luba tulemusi vaadata ilma, et sinna kandideeriks
                on_autom_kool = False
                # sisseastumiskohtade valik
                opt_vvk = [(k.id, k.nimi) for k in regkohad]
                # koolid, millel on luba vaadata tulemusi
                values = []
                if c.sooritaja:
                   for r in c.sooritaja.kandideerimiskohad:
                      if not r.automaatne:
                         values.append(r.koht_id)
                      if r.koht_id == koht_id:
                         on_autom_kool = True         

                # kas oma kool on soorituskohtade seas?
                autom_kool = None
                if koht_id:
                    q = (model.Session.query(model.Testikoht.id)
                         .join(model.Testikoht.toimumisaeg)
                         .filter(model.Toimumisaeg.testimiskord_id==testimiskord.id)
                         .filter(model.Testikoht.koht_id==koht_id))
                    if q.count() > 0:
                       autom_kool = model.Koht.get(koht_id).nimi

                c.voib_muuta = True # peab tegema Salvesta nupu
              %>
              ${h.poserr(f"vvk{suffix}")}
              % for k_id, k_nimi in opt_vvk:
              <%
                ## kool ei saa regamisel muuta teistele koolidele tulemuste vaatamise õiguse andmist
                disabled = c.reg_kool and k_id != c.user.koht_id
                checked = k_id in values
              %>
              <div>
                ${h.checkbox(f'vvk{suffix}', k_id, label=k_nimi, checked=checked, disabled=disabled)}
                % if disabled and checked:
                ## et vigade korral kuvataks ka disabled valikud
                ${h.hidden(f'vvk{suffix}', k_id)}
                % endif
              </div>
              % endfor
              % if autom_kool:
              <div class="mt-4">
                <%
                  if c.reg_sooritaja:
                     label = _("Luban praegusel koolil ({nimi}) vaadata minu testitulemusi").format(nimi=autom_kool)
                  else:
                     label = _("Praegusel koolil ({nimi}) on lubatud vaadata testitulemusi").format(nimi=autom_kool)
                %>
                ${h.checkbox1(f'vvk_oma{suffix}', 1, checked=on_autom_kool, disabled=koht_id in values, label=label)}
                <script>
                  ## kui oma kool valitakse kandideeritavate koolide seas, siis teha märge ka oma kooli märkeruutu
                  $('#vvk${suffix}_${koht_id}').click(function(){
                     if(this.checked) $('#vvk_oma${suffix}').prop('checked', true);
                     $('#vvk_oma${suffix}').prop('disabled', this.checked);
                  });
                </script>
              </div>
              % endif
            </div>
          </div>
          % endif
          % endif

      % if c.reg_sooritaja:
          ## ainult ise registreerimisel
          % if test.testiliik_kood in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
          <%
            soovib = c.sooritaja and c.sooritaja.soovib_konsultatsiooni
            konsid = testimiskord.get_kons_prk()
            if c.piirkond_id and konsid.get(c.piirkond_id):
               kcls = ''
            else:
               kcls = 'd-none'
            %>
          <div class="form-group ${kcls} kons">          
            <div class="d-flex flex-wrap">
              ${h.checkbox1(f'soovib_konsultatsiooni{suffix}', 1, class_="soovib",
              checked=soovib,
              label=_('Soovin konsultatsiooni'), disabled=not voib_muuta)}
              % if test.testiliik_kood == const.TESTILIIK_TASE:
              <div>${_("NB! Konsultatsioon kestab kuni 4,5 tundi.")}</div>
              % endif
            </div>
            <script>
              $('#soovib_konsultatsiooni${suffix}').change(function(){
                $(this).closest('.kons').find('.konst').toggle(this.checked);
              });
            </script>
            <div class="my-1 konst" style="${not soovib and 'display:none' or ''}">
              ${_("Konsultatsioon toimub:")}
              % for prk_id, li in konsid.items():
              <% dcls = prk_id != c.piirkond_id and 'd-none' or '' %>
              <ul class="konsprk ${dcls}" data-prk="${prk_id}">
                % for buf in li:
                <li>${buf}</li>
                % endfor
              </ul>
              % endfor
            </div>

          </div>
          % endif
          % if c.voib_vabastada_k and test.on_testitase(const.KEELETASE_B1) and voib_reg:
          <div class="form-group">
            ${h.checkbox(f'vabastet{suffix}', 1, checked=c.sooritaja and c.sooritaja.vabastet_kirjalikust,
          label=_("65a ja vanem kodakondsuse taotleja<br/> Vähemalt 65-aastane Eesti kodakondsust taotlev isik on keeleksamil vabastatud kodakondsuseseaduse §8 2. lõike punktis 4 sätestatud nõuete täitmisest, st kirjutamistestist (peab sooritama: kuulamis-, lugemis-ja rääkimisosa)."))}            
          </div>
          % endif
          
          % if test.testiliik_kood == const.TESTILIIK_TASE:
          <div class="form-group">
            ${h.flb(_("Märkused"))}
            ${h.text(f'reg_markus{suffix}', c.sooritaja and c.sooritaja.reg_markus, disabled=not voib_muuta)}
          </div>
          % endif
      % endif
</div>
