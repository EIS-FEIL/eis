<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Testi läbiviimise nõusolekud")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_save(None)}

<h3>${_("Piirkonnad, kus toimuvate testide läbiviimisel saan osaleda")}</h3>
<div class="form-wrapper-lineborder d-flex flex-wrap mb-2">
  <div class="mr-5">
    ${h.btn_to_dlg(_('Muuda'), h.url('new_nousolek', sub='prk', partial=True), title=_('Piirkondade valimine'), mdicls='mdi-file-edit')}
  </div>
  <div>
    ${h.literal(', '.join(rcd.piirkond.nimi for rcd in c.kasutaja.kasutajapiirkonnad))}
  </div>
</div>

<h3>${_("Testid, milles saan läbiviijana osaleda")}</h3>
<div class="form-wrapper-lineborder mb-2">
  % if c.opt_testsessioon:
  <div class="d-flex flex-wrap">
    ${h.flb(_("Testsessioon"), 'testsessioon_id', 'mr-5')}
    <div>
        ${h.select('testsessioon_id', c.testsessioon_id,
        c.opt_testsessioon, empty=True, wide=False)}
        <script>
        $('select#testsessioon_id').change(function(){
          var u='${h.url('nousolekud',partial=True)}' + \
                '&testsessioon_id='+$(this).val();
          $('div.listdiv').load(u);
        });
        </script>
    </div>
  </div>
  % endif
  <div class="listdiv">
    <%include file="nousolekud_list.mako"/>
  </div>
</div>

<div id="savefooter">
<ul>
  <li>${_("Vajadusel kooskõlastan  tööandjaga hindamiskomisjoni töös osalemise.")}</li>
  <li>${_("Oman hindamiskomisjoni töös osalemiseks vajalikku kvalifikatsiooni.")}</li>
  <li>${_("Olen kohustatud hoidma konfidentsiaalsena mulle hindamiskomisjoni töös teatavaks saanud infot.")}</li>
</ul>
<div class="text-right">
  ${h.submit()}
</div>
</div>

${h.end_form()}
