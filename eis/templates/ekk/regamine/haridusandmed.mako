<h2>${_("Õppimine")}</h2>

${h.rqexp()}
<div class="form-wrapper mb-3">

  <% 
     opilane = c.kasutaja.any_opilane 
  %>
  % if opilane and opilane.koht:
   ## EHISest saadi õppeasutuse andmed
  <div class="form-group row">
    ${h.flb3(_("Õppeasutus"),'koht_nimi')}
    <div class="col-md-9" id="koht_nimi">
      ${h.roxt(opilane.koht and opilane.koht.nimi or '')}
    </div>
  </div>
  % else:
    ## EHISest ei saadud õppimisandmeid või saadi õppimisandmed tundmatu kooliga
    % if c.is_edit:
  <div class="form-group row">  
    ${h.flb3(_("Õppeasutus"),'ko_kool_koht_id', rq=True)}
    <div class="col-md-9">
      ${h.select('ko_kool_koht_id', c.kasutaja.kool_koht_id,
      model.Koht.get_soorituskoht_opt(), empty=True)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("või sisesta õppeasutuse nimetus"),'ko_kool_nimi')}
    <div class="col-md-9">
      ${h.text('ko_kool_nimi',c.kasutaja.kool_nimi)}
    </div>      
  </div>
    % else:
  <div class="form-group row">  
    ${h.flb3(_("Õppeasutus"),'kool_nimi')}
    <div class="col-md-9" id="kool_nimi">
      ${h.roxt(c.kasutaja.kool_nimi or c.kasutaja.kool_koht and c.kasutaja.kool_koht.nimi)}
    </div>
  </div>
    % endif
  % endif

  % if opilane:
  ## õppimisandmed saadi EHISest
  <div class="form-group row">  
    ${h.flb3(_("Õppekeel"),'oppekeel')}
    <div class="col-md-9" id="oppekeel">
      ${h.roxt(const.EHIS_LANG_NIMI.get(opilane.oppekeel))}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Õppevorm"),'oppevorm')}
    <div class="col-md-9" id="oppevorm">
      ${h.roxt(opilane.oppevorm_nimi)}
    </div>
  </div>
   % if c.kasutaja.lopetamisaasta:
  <div class="form-group row">  
    ${h.flb3(_("Lõpetamise aasta"),'lopetamisaasta')}
    <div class="col-md-9" id="lopetamisaasta">
      ${h.roxt(c.kasutaja.lopetamisaasta)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Haridust tõendava dokumendi number"),'tunnistus_nr')}
    <div class="col-md-9" id="tunnistus_nr">
      ${h.roxt(c.kasutaja.tunnistus_nr)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("väljastamise kuupäev"), 'tunnistus_kp')}
    <div class="col-md-9" id="tunnistus_kp">
      ${h.roxt(h.str_from_date(c.kasutaja.tunnistus_kp))}
    </div>
  </div>
   % endif
  % else:
   ## Andmeid polnud EHISes
  <div class="form-group row">  
    ${h.flb3(_("Õppekeel"),'ko_oppekeel', rq=True)}
    <div class="col-md-9">
      ${h.select('ko_oppekeel', c.kasutaja.oppekeel, const.EHIS_LANG_OPT)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Lõpetamise aasta"),'ko_lopetamisaasta', rq=True)}
    <div class="col-md-9">
      ${h.posint('ko_lopetamisaasta',c.kasutaja.lopetamisaasta)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Haridust tõendava dokumendi number"),'ko_tunnistus_nr', rq=True)}
    <div class="col-md-9">
      ${h.text('ko_tunnistus_nr', c.kasutaja.tunnistus_nr)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("väljastamise kuupäev"),'ko_tunnistus_kp', rq=True)}
    <div class="col-md-9">
      ${h.date_field('ko_tunnistus_kp', c.kasutaja.tunnistus_kp, wide=False)}
    </div>
  </div>
  % endif

% if c.app_ekk and c.lopetanud_tingimused:
  <div class="form-group row">  
    <div class="col-md-12">
      ${h.checkbox('ko_lopetanud', 1, checked=c.kasutaja.lopetanud, disabled=True,
      label=_("Lõpetanud"))}
    </div>
  </div>
  <div class="form-group row">  
    <div class="col-md-3">
      ${h.checkbox('ko_lopetanud_kasitsi', 1, checked=c.kasutaja.lopetanud_kasitsi,
      label=_("Lõpetanud (käsitsi)"))}
    </div>
    <div class="col-md-2 text-md-right">
      ${_("Põhjus")}
    </div>
    <div class="col-md-7">
      ${h.text('ko_lopetanud_pohjus', c.kasutaja.lopetanud_pohjus, maxlength=100)}
    </div>
  </div>
% endif
</div>
