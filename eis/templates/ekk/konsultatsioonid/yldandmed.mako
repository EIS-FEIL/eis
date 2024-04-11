<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%
c.can_update = c.user.has_permission('konsultatsioonid', const.BT_UPDATE,c.item) 
%>
<%def name="page_title()">
Konsultatsioon: ${c.item.nimi or ''} | Üldandmed
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'konsultatsioonid' %>
</%def>
<%def name="breadcrumbs()">
${h.crumb(_('Konsultatsioonid'), h.url('konsultatsioonid'))}
${h.crumb_sep()}
${h.crumb(c.item.nimi or _('Konsultatsioon'))}
</%def>
${h.form_save(c.item.id)}

${h.rqexp()}
<div class="form-wrapper mb-2">
  % if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("ID"))}
    <div class="col">
      ${c.item.id}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    ${h.flb3(_("Nimetus"), rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testi liik"), rq=True)}
    <div class="col">
      <% opt_testiliik = [r for r in c.opt.testiliik if r[0] in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)] %>
      ${h.select('f_testiliik_kood', c.item.testiliik_kood, opt_testiliik)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppeaine"), rq=True)}
    <div class="col">
      ${h.select('f_aine_kood', c.item.aine_kood, c.opt.klread_kood('AINE',
      empty=True, vaikimisi=c.item.aine_kood))}
    </div>
  </div>
  <div class="form-group row keeletase ${c.is_edit and 'd-none' or ''}">
    ${h.flb3(_("Keeleoskuse tase"))}
    <div class="col">
      ${h.select('keeletase_kood', c.item.keeletase_kood, 
      c.opt.klread_kood('KEELETASE', c.item.aine_kood, empty=True, vaikimisi=c.item.keeletase_kood, ylem_required=True), wide=False, class_="keeletase")}
      <script>
        $(function(){
         $('select#f_aine_kood').change(
           callback_select("${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                           'ylem_kood', 
                           $('select.keeletase'))
           );
          $('select.keeletase').eq(0).change(function(){
            $('div.keeletase').toggleClass('d-none', ($(this).find('option').length<=2));
    });
          $('div.keeletase').toggleClass('d-none', ($('select.keeletase').eq(0).find('option').length<=2));
        
        });
      </script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col">
      ${h.textarea('f_markus', c.item.markus, cols=90, rows=3)}
    </div>
  </div>

</div>

<div class="d-flex flex-wrap">
  ${h.btn_back(url=h.url('konsultatsioonid'))}
  % if c.item.id and c.can_update:
  ${h.btn_to(_('Eemalda konsultatsioon'), h.url('delete_konsultatsioon', id=c.item.id), method='delete')}
  ${h.btn_to(_('Kopeeri'), h.url('update_konsultatsioon',id=c.item.id, sub='kopeeri'), method='post')}
  % endif
  <div class="flex-grow-1 text-right">
    % if c.is_edit:
    %   if c.item.id:
    ${h.btn_to(_('Vaata'), h.url('konsultatsioon', id=c.item.id), method='get', level=2)}
    %   endif
    ${h.submit()}
    % elif c.can_update:
${h.btn_to(_('Muuda'), h.url('edit_konsultatsioon', id=c.item.id), method='get')}
    % endif
  </div>
</div>

${h.end_form()}
