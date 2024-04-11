## PDFi trykkimise valikud, kuvatakse juhul, kui ymbrikud on arvutatud
<%
  srt = c.new_item()
  srt.JRK_Y = 'valjastusymbrikuliik.tahis'
  srt.JRK_L = 'testipakett.lang'
  srt.JRK_P = 'piirkond.nimi'
  srt.JRK_S = 'koht.nimi'
  srt.JRK_KY = 'valjastusymbrik.kursus_kood'
  on_paketid = c.toimumisaeg.on_paketid
%>

% if c.subtab:
${h.form_save(None, form_name='form_pdf')}
% if request.params.get('debug'):
${h.hidden('debug', 1)}
% endif

${h.hidden('sub', f'pr_{c.subtab}')}

% if c.subtab == 'valjastusymbrikud':
${self.valjastusymbrikud(srt)}
% elif c.subtab == 'tagastusymbrikud':
${self.tagastusymbrikud(srt)}
% elif c.subtab == 'protokollid':
${self.protokollid(srt, on_paketid)}
% elif c.subtab == 'turvakotikleebised':
${self.turvakotikleebised(srt)}
% elif c.subtab == 'turvakotiaktid':
${self.turvakotiaktid(srt)}
% elif c.subtab == 'lisatingimused':
${self.lisatingimused(srt)}
% endif

${h.end_form()}

% if c.arvutusprotsessid:
<%
  c.url_refresh = h.url_current('index', toimumisaeg_id=c.toimumisaeg.id, subtab=c.subtab, sub='progress')
  c.protsessid_no_pager = True
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif

<script>
   ## kerime avamisel alamsakkideni
   window.scroll(0,$('#subtabs_pos').offset().top);

   ## testikoha valikuvälja uuendamine piirkonna valimisel
        function change_by_piirkond(fld)
        {
           var url = "${h.url('pub_testikohad', toimumisaeg_id=c.toimumisaeg.id)}";
           var data = {piirkond_id: $(fld).val()};
           var target = $(fld).closest('form').find('select#testikoht_id');
           update_options(null, url, null, target, data, null, true);
        }

    $(function(){
        ## kui (nt page reload) korral on lehe laadimisel mõni dok liik valitud juba,
        ## siis teeme ka malli valiku nähtavaks
        $.each($('select[name$="_t"]'), function(n, item){
           var cb = $(item).closest('.row').find('input.tr-check');
           $(item).closest('div').toggle(cb.is(':checked'));
        });
        ## märkeruudu valiku muutmisel peita/kuvada malli valikväli
        $('input.tr-check').change(function(){
           $(this).closest('.row').find('div.opt').toggle(this.checked);
        });
    });
</script>
% endif

<%def name="valjastusymbrikud(srt)">
<h2>${_("Soorituskohta väljastatavad ümbrikud")}</h2>
% if len(c.toimumisaeg.valjastusymbrikuliigid) == 0:
${h.alert_notice(_("Väljastusümbrikuliike pole kirjeldatud."), False)}
% else:
<div>
  % for n, yliik in enumerate(c.toimumisaeg.valjastusymbrikuliigid):
  ${self.tr_check(u'%s. %s' % (yliik.tahis, yliik.nimi), 'valjastusymbrik', n, yliik.id, avamisaeg=True)}
  % endfor
  ${self.tr_piirkond_koht()}
  <div class="form-group row">
    ${h.flb3(_("Järjestamine"))}
    <div class="col" id="valjastusymbrik_jrk">
           <% 
               jrk = ((srt.JRK_Y, _("Ümbriku liik")), 
                      (srt.JRK_L, _("Keel")), 
                      (srt.JRK_P, _("Piirkond")),
                      (srt.JRK_S, _("Soorituskoht")),
                      (srt.JRK_KY, _("Kursus")))
               if c.y_jrk == '':
                  c.y_jrk = []
               for n, rcd in enumerate(jrk):
                  if len(c.y_jrk) == n:
                     c.y_jrk.append(rcd[0])
            %>
            1. ${h.select('y_jrk', c.y_jrk[0], jrk, wide=False)}
            2. ${h.select('y_jrk', c.y_jrk[1], jrk, wide=False)}
            3. ${h.select('y_jrk', c.y_jrk[2], jrk, wide=False)}
            4. ${h.select('y_jrk', c.y_jrk[3], jrk, wide=False)}
            5. ${h.select('y_jrk', c.y_jrk[4], jrk, wide=False)}            
            <script>
              $(document).ready(function(){
                order_select_setup($('#valjastusymbrik_jrk select#y_jrk'));
              });
            </script>
    </div>
  </div>
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail (C4)"), id='c4')}
  ${h.submit(_("Loo väljatrüki fail (kleeps)"), id='kleeps')}
</div>
% endif
</%def>

<%def name="tagastusymbrikud(srt)">
<h2>${_("Tagastusümbrikud")}</h2>
<div>
  ${self.tr_check(_("Peaümbrik (protokollide ümbrik)"), 'protokollideymbrik')}
  % if len(c.toimumisaeg.tagastusymbrikuliigid) == 0:
  <div class="m-3">
    ${_("Tagastusümbrikuliike pole kirjeldatud.")}
  </div>
  % endif
  ## tööde tagastamise ümbrikud
  % for n, yliik in enumerate(c.toimumisaeg.tagastusymbrikuliigid):
  ${self.tr_check(u'%s. %s' % (yliik.tahis, yliik.nimi), 'tagastusymbrik', n, yliik.id)}        
  % endfor
        
  ## tühjade tööde tagastamise ümbrikud
  % for n, yliik in enumerate(c.toimumisaeg.valjastusymbrikuliigid):
  ${self.tr_check(u'%s. %s' % (yliik.tahis, yliik.nimi), 'tyhjadeymbrik', n, yliik.id)}        
  % endfor
  
  ${self.tr_piirkond_koht()}
  <div class="form-group row">
    ${h.flb3(_("Järjestamine"))}
    <div class="col" id="tagastusymbrik_jrk">
            <% 
               jrk = ((srt.JRK_P, _("Piirkond")), 
                      (srt.JRK_L, _("Keel")), 
                      (srt.JRK_S, _("Soorituskoht")))
               if c.m_jrk == '':
                  c.m_jrk = []
               for n, rcd in enumerate(jrk):
                  if len(c.m_jrk) == n:
                     c.m_jrk.append(rcd[0])

            %>
            1. ${h.select('y_jrk', c.m_jrk[0], jrk, wide=False)}
            2. ${h.select('y_jrk', c.m_jrk[1], jrk, wide=False)}
            3. ${h.select('y_jrk', c.m_jrk[2], jrk, wide=False)}
            <script>
              $(document).ready(function(){
                order_select_setup($('#tagastusymbrik_jrk select#y_jrk'));
              });
            </script>

    </div>
  </div>
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail (C4)"))}
</div>
</%def>

<%def name="protokollid(srt, on_paketid)">
<h3>${_("Protokollid ja nimekirjad")}</h3>
<div>
  ${self.tr_check(_("Saatekirjad"), 'saatekiri', disabled=not on_paketid or not c.toimumisaeg.on_hindamisprotokollid)}
  ${self.tr_check(_("Testitööde avamise protokoll"), 'avamisprotokoll')}
  ${self.tr_check(_("Testi toimumise protokoll"), 'toimumisprotokoll')}
  % if c.toimumisaeg.testiosa.vastvorm_kood == const.VASTVORM_SP:
  ${self.tr_check(_("Hindajate ja intervjueerijate koodid"), 'shindajakoodid')}
  % endif
  ${self.tr_check(_("Testitööde üleandmise protokoll"), 'yleandmisprotokoll')}
  ${self.tr_check(_("I ja II hindamise protokoll"), 'hindamisprotokoll', disabled=not c.toimumisaeg.on_hindamisprotokollid)}
  ${self.tr_check(_("III hindamise protokoll"), 'hindamisprotokoll3', disabled=not c.toimumisaeg.on_hindamisprotokollid)}
  ${self.tr_check(_("Testisooritajate nimekiri"), 'nimekiri')}
  ${self.tr_check(_("Testisooritajate nimekiri rühmade kaupa"), 'ryhmanimekiri')}
  ${self.tr_check(_("Registreerimisnimekiri"), 'regnimekiri')}
  ${self.tr_piirkond_koht()}
  <div class="form-group row">
    ${h.flb3(_("Järjestamine"))}
    <div class="col" id="materjal_jrk">
            <% 
               jrk = ((srt.JRK_P, _("Piirkond")), 
                      (srt.JRK_L, _("Keel")), 
                      (srt.JRK_S, _("Soorituskoht")))
               if c.m_jrk == '':
                  c.m_jrk = []
               for n, rcd in enumerate(jrk):
                  if len(c.m_jrk) == n:
                     c.m_jrk.append(rcd[0])

            %>
            1. ${h.select('m_jrk', c.m_jrk[0], jrk, wide=False)}
            2. ${h.select('m_jrk', c.m_jrk[1], jrk, wide=False)}
            3. ${h.select('m_jrk', c.m_jrk[2], jrk, wide=False)}
            <script>
              $(document).ready(function(){
                order_select_setup($('#materjal_jrk select#m_jrk'));
              });
            </script>
    </div>
  </div>
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail"))}
</div>
</%def>

<%def name="turvakotikleebised(srt)">
<h3>${_("Turvakottide kleebised")}</h3>
<div>
  <% n_liik = c.toimumisaeg.testiosa.test.on_tseis and 'ts' or 'r' %>
  ${h.hidden('n_liik', n_liik)}
  ${self.tr_check(u'Testitööde väljastamise turvakotid',
  'vkotikleebis', n_liik=n_liik)}
  ${self.tr_check(u'Testitööde tagastamise turvakotid',
  'tkotikleebis', n_liik=n_liik)}
  ${self.tr_piirkond_koht()}
  <div class="form-group row">
    ${h.flb3(_("Järjestamine"))}
    <div class="col" id="kotid_jrk">
            <% 
               jrk = ((srt.JRK_P, _("Piirkond")), 
                      (srt.JRK_L, _("Keel")), 
                      (srt.JRK_S, _("Soorituskoht")))
               if c.k_jrk == '':
                  c.k_jrk = []
               for n, rcd in enumerate(jrk):
                  if len(c.k_jrk) == n:
                     c.k_jrk.append(rcd[0])
            %>
            1. ${h.select('k_jrk', c.k_jrk[0], jrk, wide=False)}
            2. ${h.select('k_jrk', c.k_jrk[1], jrk, wide=False)}
            3. ${h.select('k_jrk', c.k_jrk[2], jrk, wide=False)}
            <script>
              $(document).ready(function(){
                order_select_setup($('#kotid_jrk select#k_jrk'));
              });
            </script>
    </div>
  </div>
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail"))}
</div>
</%def>

<%def name="turvakotiaktid(srt)">
<h3>${_("Turvakottide aktid")}</h3>
<div>
  ${self.tr_check(_("Eksamikeskuselt kullerile üleandmise akt"), 'akt_ekk_kuller', kogus=2)}
  ${self.tr_check(_("Kullerilt maavalitsusele üleandmise akt"), 'akt_kuller_maavalitsus', kogus=2)}
  ${self.tr_check(_("Akt, kuhu maavalitsus kogub koolide allkirjad"), 'akt_maavalitsus_koolid', kogus=1)}
  ${self.tr_check(_("Akt iga kooli kohta"), 'akt_kool', kogus=1)}
  ${self.tr_check(_("Maavalitsuselt kullerile üleandmise akt"), 'akt_maavalitsus_kuller', kogus=2)}
  ${self.tr_check(_("Kullerilt eksamikeskusele üleandmise akt"), 'akt_kuller_ekk', kogus=2)}
  ${self.tr_piirkond_koht()}
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail"))}
</div>
</%def>

<%def name="lisatingimused(srt)">
<h3>${_("Lisatingimuste või eritingimustega isikute nimekiri")}</h3>
<div>
  ${self.tr_check(_("Nimekiri"), 'lisatingimused')}
</div>
<div class="mt-3 text-right">
  ${h.submit(_("Loo väljatrüki fail"))}
</div>
</%def>

<%def name="tr_piirkond_koht()">
  <div class="form-group row">
    ${h.flb3(_("Piirkond"))}
    <div class="col">
      ${h.select('piirkond_id', c.piirkond_id,
      c.toimumisaeg.get_piirkonnad_opt(), empty=True, onchange='change_by_piirkond(this)')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Soorituskoht"))}
    <div class="col">
      ${h.select('testikoht_id', c.testikoht_id,
      c.toimumisaeg.get_testikohad_opt(), empty=True)}
    </div>
  </div>
</%def>

<%def name="tr_check(title, name, cnt=0, yliik_id=None, kogus=False, disabled=False, avamisaeg=False, n_liik=None)">
<% 
   if yliik_id:
      # jadad
      prefix = '%s-%d' % (name, cnt) 
      ttype_name = '%s.ttype' % prefix
      tname_name = '%s.tname' % prefix
   else:
      ttype_name = name
      tname_name = '%s_t' % name

   if n_liik:
      opt_name = '%s_%s' % (name, n_liik)
   else:
      opt_name = name
   md_width = 8 - (kogus and 2 or 0) - (avamisaeg and 3 or 0)
   lg_width = 9 - (kogus and 1 or 0) - (avamisaeg and 3 or 0)
   tmpl_cls = f"col-md-{md_width} col-lg-{lg_width}"
%>
  <div class="form-group row">
    <div class="col-md-4 col-lg-3">
      ${h.checkbox(ttype_name, 1, label=title,
      checked=not disabled and c.__getattr__(ttype_name),
      disabled=disabled,
      class_="tr-check")}
      % if yliik_id:
      ${h.hidden('%s.liik_id' % prefix, yliik_id)}
      % endif
    </div>
    <div class="${tmpl_cls}">
      <div class="opt">
        ${h.select(tname_name, c.pdf_default.get(name), c.pdf_templates.get(opt_name) or [])}
      </div>
    </div>
    % if kogus:
    <div class="col-md-2 col-lg-1">
      <div class="opt">
        ${h.int5('%s_kogus' % name, kogus or 1)}
      </div>
    </div>
    % endif
    % if avamisaeg:
    <div class="col-md-3">
      <div class="opt">
        ${_("Avamise kellaaeg")}
        ${h.time('%s.avamisaeg' % prefix, '', wide=False)}
      </div>
    </div>
    % endif
  </div>
</%def>
