
${h.form_search(url=h.url('test_komplekt_otsiylesanded', test_id=c.test.id, testiylesanne_id=c.testiylesanne_id,
komplekt_id=c.komplekt_id), id="form_search_y")}
${h.hidden('komplekt_id', c.komplekt_id)}
${h.hidden('komplektivalik_id', c.komplektivalik_id)}
${h.hidden('partial', 1)}
${h.hidden('aine', c.test.aine_kood)}
<script>
  function search_ylesanded()
  {
     var form = $('form#form_search_y');
     var url = $(form).attr('action');
     var data = $(form).serialize();
     dialog_load(url, data, 'GET', $('div.listdiv')); 
     return false;
  }
  $(function(){
    $('form#form_search_y').submit(search_ylesanded);
  });
</script>

<div class="d-flex pb-2">
  <b class="mr-2">${_("Kuhu valitakse")}:</b>
  <div class="d-flex flex-grow-1 flex-wrap">
    % if c.testiylesanne.alatest:
    <div class="mx-2">${_("Alatest")}: ${c.testiylesanne.alatest.nimi}</div>
    % endif
            
    % if c.testiylesanne.testiplokk:
    <div class="mx-2">${_("Testiplokk")}: ${c.testiylesanne.testiplokk.nimi}</div>
    % endif
            
    <div class="mx-2">${_("Ülesanne")}: ${c.testiylesanne.seq}
            ${c.testiylesanne.nimi or ''}
    </div>
    <div class="mx-2">${_("Komplekt")}: ${c.komplekt.tahis}</div>
    % if c.testiylesanne.on_valikylesanne:
    <div class="mx-2">${_("Valik")} ${c.seq}</div>
    % endif
  </div>
</div>

<div class="gray-legend p-3">
  <b>${_("Nõuded valitavale ülesandele")}</b>
  <div class="row">
    <div class="col-md-6 col-lg-4 col-xl-3">
      ${h.flb(_("Ülesande ID"),'ylesanne_id')}
      ${h.int10('ylesanne_id', c.ylesanne_id)}
    </div>
    <div class="col-md-6 col-lg-4 col-xl-3">
      ${h.flb(_("Keel"), 'okeel')}
      <span id="okeel">
        ${', '.join([model.Klrida.get_lang_nimi(lang) for lang in c.komplekt.keeled])}
      </span>
    </div>
    ${noue('aste', c.testiylesanne.aste_kood, _("Kooliaste"), c.testiylesanne.aste_nimi)}
    ${noue('teema', c.testiylesanne.alateema_kood, _("Alateema"), c.testiylesanne.alateema_nimi)}
    ${noue('valdkond', c.testiylesanne.teema_kood, _("Teema"), c.testiylesanne.teema_nimi)}
    ${noue('mote', c.testiylesanne.mote_kood, _("Mõtlemistasand"), c.testiylesanne.mote_nimi)}
    ${noue('keeletase', c.testiylesanne.keeletase_kood, _("Keeleoskuse tase"), c.testiylesanne.keeletase_nimi)} 
    ${noue('tyyp', c.testiylesanne.tyyp, _("Liik"), c.testiylesanne.tyyp_nimi)}
    ${noue('hindamine', c.testiylesanne.hindamine_kood, _("Hindamise liik"), c.testiylesanne.hindamine_nimi)}
    ${noue('arvutihinnatav', c.testiylesanne.arvutihinnatav, _("Arvutiga hinnatav"), 'Jah')}
    ${noue('max_pallid', h.fstr(c.testiylesanne.max_pallid), _("Hindepallide arv"))}
    ${noue('kasutusmaar', h.fstr(c.testiylesanne.kasutusmaar), _("Kasutusmäär"))}
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">      
      ${h.button150(_("Otsi"), onclick="search_ylesanded()")}     
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<%def name="noue(id, kood, kirjeldus, nimi=None)">
 % if kood:
<div class="col-md-6 col-lg-4 col-xl-3">
  ${h.checkbox(id, kood, checked=True, label=f"{kirjeldus}: {nimi or kood}")}
</div>
 % endif
</%def>

${h.form_save(c.seq)}
${h.hidden('komplekt_id2', c.komplekt_id2 or '')}
${h.hidden('komplektivalik_id', c.komplektivalik_id)}

<div class="listdiv">
% if c.items != '':
<%include file="komplekt.otsiylesanded_list.mako"/>
% endif
</div>

${h.end_form()}
