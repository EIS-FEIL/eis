${h.form_search(url=h.url('korraldamine_koht_otsilabiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id))}
${h.hidden('grupp_id', c.grupp_id)}
% if c.labiviija:
${h.hidden('labiviija_id', c.labiviija.id)}
% endif

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"), 'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-8">
      <div class="form-group">
            % if c.grupp_id in (const.GRUPP_HINDAJA_K, const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
            % for lang in c.toimumisaeg.testimiskord.get_keeled():
            ${h.checkbox('lang', lang, checkedif=c.lang,
            label=model.Klrida.get_lang_nimi(lang))}
            <br/>
            % endfor
            % endif

            ${h.checkbox('nous', 1, checked=c.nous,
            label=_("Näita ainult osalemise soovi avaldanud läbiviijaid"))}
            <br/>
            ${h.checkbox('nous_kord', 1, checked=c.nous_kord,
            label=_("Näita ainult samal testimiskorral osalemise soovi avaldanud läbiviijaid"))}
            <br/>
            ${h.checkbox('nous_sess', 1, checked=c.nous_sess,
            label=_("Näita ainult samal testsessioonil osalemise soovi avaldanud läbiviijaid"))}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col">
      <div class="form-group text-right">
        ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('korraldamine_koht_otsilabiviijad',toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht.id))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('korraldamine_koht_labiviijad', toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht.id), method='post')}
${h.hidden('grupp_id', c.grupp_id)}
% if c.labiviija:
${h.hidden('labiviija_id', c.labiviija.id)}
% endif

% if not c.labiviija:
% if c.grupp_id != const.GRUPP_KOMISJON_ESIMEES or c.testikoht.toimumisaeg.on_ruumiprotokoll:
  <%
  maaramata = not c.toimumisaeg.ruum_noutud
  opt_testiruumid = c.testikoht.get_testiruumid_opt(maaramata)
  %>
  % if not opt_testiruumid:
  <% c.items = [] %>
  ${h.alert_error(_("Testiruum on määramata. Palun määra esmalt testiruum."), False)}
  % else:
  <div class="row filter">
    <div class="col-12 col-md-4 text-md-right">
      <div class="form-group">    
        ${h.flb(_("Ruum"))}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">    
      ${h.select('testiruum_id', c.testiruum_id, opt_testiruumid)}
      </div>
    </div>
  </div>
  % endif
% endif
% endif

% if c.items:

<% testsessioon_id = c.toimumisaeg.testimiskord.testsessioon_id %>
<div class="listdiv">
      <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th></th>
            ${h.th(_("Isik"))}
            ${h.th(_("Muud osalemised"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <tr>
            <td>
              ${h.submit(_("Vali"),id='valik_id_%d' % rcd.id)}
            </td>
            <td>${rcd.nimi}</td>
            <td>
              <%
                 # osalemised samal testsessioonil
                 muud_cnt = model.Labiviija.query.\
                      filter_by(kasutaja_id=rcd.id).\
                      join(model.Labiviija.toimumisaeg).\
                      join(model.Toimumisaeg.testimiskord).\
                      filter(model.Testimiskord.testsessioon_id==testsessioon_id).\
                      filter(model.Labiviija.kasutajagrupp_id!=const.GRUPP_HIND_INT).\
                      count()
              %>
              ${muud_cnt}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
</script>
</div>
% endif

${h.end_form()}

% endif

