<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Fail")} ${c.item.filename}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Failid"), h.url('muud_toofailid'))} 
${h.crumb(c.item.filename or _("Fail"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

${h.form_save(c.item.id, multipart=True)}
${h.rqexp()}
<div class="form-wrapper">
  <div class="form-group row">
    ${h.flb3(_("Fail"),'f_filedata', rq=True)}
    <div class="col-md-9">
      <%
        files = []
        if c.item.filename:
           url = h.url('muud_toofail_format', id=c.item.id, format=c.item.fileext)
           files = [(url, c.item.filename, c.item.filesize)]
      %>
      ${h.file('f_filedata', value=_("Fail"), files=files)}
      ${h.hidden('f_id', c.item.id)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Failinimi"),'filename')}
    <div class="col-md-9">
      ${h.text('filename', c.item.filename)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kirjeldus"),'f_kirjeldus')}
    <div class="col-md-9">
      ${h.text('f_kirjeldus', c.item.kirjeldus, maxlength=256)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testi ID"),'test_id')}
    <div class="col-md-9">
      ${h.posint5('test_id', c.item.test_id)}
      % if c.item.test_id:
      ${h.link_to(model.Test.get(c.item.test_id).nimi, h.url('test', id=c.item.test_id))}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Avalik alates"),'avalik_kuupaev')}
    <div class="col-md-3">
    <%
      avalik_alates = c.item.avalik_alates
      if not avalik_alates:
         avalik_alates = model.datetime.now()
    %>
    ${h.date_field('avalik_kuupaev', avalik_alates, wide=False)}
    </div>
    <div class="col-md-1 text-right">${h.flb(_("kell"),'avalik_kell')}</div>
    <div class="col-md-3">
      ${h.time('avalik_kell', avalik_alates, show0=True, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kooli õppetase"),'f_oppetase_kood')}
    <div class="col-md-9">
      ${h.select('f_oppetase_kood', c.item.oppetase_kood,
      c.opt.OPPETASE, empty=True,wide=False)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('tase_all', label=_("Õppekavad ja õppekavajärgsed haridustasemed"))}

      <table width="100%" 
             class="table table-borderless table-striped" id="tbl_haridustase">

        <% haridustase_koodid = [r.kavatase_kood for r in c.item.toofailitasemed] %>
        % for r in c.opt.klread('KAVATASE'):
        <%
          r_ylem = r[3] and model.Klrida.get(r[3]) or None
          r_kood = r[1]
          r_nimi = r[2]
        %>
        % if r_ylem:
          % if r_ylem.kood==c.item.oppetase_kood:
        <tr id="tr_tase_${r_ylem.kood}">
          % elif r_ylem:
        <tr id="tr_tase_${r_ylem.kood}" class="d-none">
          % endif
          <td>
            ${h.checkbox('tase_kood', r_kood, 
            checked=r_kood in haridustase_koodid,
            class_='selectrow')}
            ${r_nimi}
          </td>
        </tr>
        % endif
        % endfor
      </table>
    </div>
  </div>
</div>

% if c.item.modifier:
<p>
  ${_("Viimati muutnud")}
  ${model.Kasutaja.get_name_by_creator(c.item.modifier) or c.item.modifier} 
  ${h.str_from_datetime(c.item.modified)}
</p>
% endif
<br/>

% if c.is_edit:
${h.submit()}
% endif
% if c.item.id and c.user.has_permission('failid', const.BT_UPDATE):
${h.btn_to(_("Kustuta"), h.url('muud_delete_toofail', id=c.item.id), method='delete')}
% endif
${h.btn_to(_("Tagasi"), h.url('muud_toofailid'))}
${h.end_form()}


      <script>
        $(document).ready(function(){
        ## võimalus kõik haridustasemed korraga valida
        $('#tase_all').change(function(){
          var rows = $('table#tbl_haridustase tr:not(.d-none)');
          rows.find('input').prop('checked',this.checked);
          rows.toggleClass('selected', this.checked);
        });
        ## kui muudetakse õppetaset, siis kuvame ainult õppetasemele vastavad haridustasemed
        $('#f_oppetase_kood').change(function(){
          $('#tase_all').prop('checked', false);
          var oppetase = $(this).val();
          $.each($('table#tbl_haridustase tr'), function(n, item){
            $(item).toggleClass('d-none', $(item).attr('id')!='tr_tase_'+oppetase);
          });
        });
        });
      </script>
