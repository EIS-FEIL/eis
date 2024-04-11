  % if not c.test.pallideta:
  <div class="gray-legend p-3">
    ${h.flb(_("Vali filter"), 'rfilter')}:

    <div class="row filter" id="rfilter">
      <div class="col-md-6 col-lg-3">
        <div class="form-group">        
          ${h.checkbox('cnt', 1, checked=c.cnt, label=_("sooritajate arv"))}
          % if not c.mitu_testiosa:
          <br/>
          ${h.checkbox('ajakulu', 1, checked=c.ajakulu, label=_("kasutatud aeg"))}
          % endif
          <br/>
          ${h.checkbox('lang', 1, checked=c.lang, label=_("soorituskeel"))}
          <br/>
          ${h.checkbox('sugu', 1, checked=c.sugu, label=_("sugu"))}
        </div>
      </div>
      <div class="col-md-6 col-lg-3">
        <div class="form-group">            
          ${h.checkbox('avg_pt', 1, checked=c.avg_pt, label=_("keskmine (punktides)"))}
          <br/>
          ${h.checkbox('avg_pr', 1, checked=c.avg_pr, label=_("keskmine (%)"))}
          <br/>
          ${h.checkbox('mediaan', 1, checked=c.mediaan, label=_("mediaan"))}
        </div>
      </div>
      <div class="col-md-6 col-lg-3">
        <div class="form-group">            
          ${h.checkbox('min', 1, checked=c.min, label=_("min punktide saajate arv"))}
          <br/>
          ${h.checkbox('max', 1, checked=c.max, label=_("max punktide saajate arv"))}
        </div>
      </div>
      % if c.rvaade:
      <div class="col-md-6 col-lg-3">
        <div class="form-group">            
          ${_("Kuni {p}% pallidest").format(p=h.posfloat('alla', c.alla, size=3, maxvalue=100))}
          <br/>
          ${h.checkbox('alla20', 1, checked=c.alla20, label=_("sooritajate arv"))}
          <br/>
          ${h.checkbox('alla20pr', 1, checked=c.alla20pr, label=_("sooritajate protsent"))}
        </div>
      </div>
      <div class="col-md-6 col-lg-3">
        <div class="form-group">            
          ${_("Vähemalt {p}% pallidest").format(p=h.posfloat('yle', c.yle, size=3, maxvalue=100))}
          <br/>
          ${h.checkbox('yle80', 1, checked=c.yle80, label=_("sooritajate arv"))}
          <br/>
          ${h.checkbox('yle80pr', 1, checked=c.yle80pr, label=_("sooritajate protsent"))}
        </div>
      </div>
      % else:
      <div class="col-md-6 col-lg-3">
        <div class="form-group">            
          ${h.checkbox('edukus_pt', 1, checked=c.edukus_pt, label=_("edukus"))}
          <br/>
          ${h.checkbox('edukus_pr', 1, checked=c.edukus_pr, label=_("edukuse %"))}
          <br/>
          ${h.checkbox('kvaliteet_pt', 1, checked=c.kvaliteet_pt, label=_("kvaliteet"))}
          <br/>
          ${h.checkbox('kvaliteet_pr', 1, checked=c.kvaliteet_pr, label=_("kvaliteedi %"))}
        </div>
      </div>
      % endif
      <div class="col d-flex justify-content-end align-items-end">
        <div class="form-group">
          ${h.btn_search(_("Arvuta"))}
          ${h.submit(_("CSV (Excel)"), id='csv', level=2)}
        </div>
      </div>
    </div>
  </div>
  % endif
