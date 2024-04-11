<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Suulise vastamise hindamisprotokolli sisestamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Suulise vastamise hindamisprotokolli sisestamine'),
h.url('sisestamine_suulised', ta_tahised=c.toimumisaeg.tahised,
sessioon_id=c.toimumisaeg.testimiskord.testsessioon_id, toimumisaeg_id=c.toimumisaeg.id))}
<% sk = c.hindamisprotokoll.sisestuskogum %>
${h.crumb('%s %s' % (c.hindamisprotokoll.get_tahised(), sk and sk.nimi or ''))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<% 
   c.protokoll = c.hindamisprotokoll.testiprotokoll 
   c.sisestuskogum = c.hindamisprotokoll.sisestuskogum
%>
<%include file="protokoll.before_tabs.mako"/>

${h.form_save(None, autocomplete='off')}

% for c.hk_n, hk in enumerate(c.hindamisprotokoll.sisestuskogum.hindamiskogumid):
 <% 
    c.hindamiskogum = hk 
    c.hindamiskogum_id = hk.id
    c.testiylesanded = hk.testiylesanded
    c.items = c.get_items()
 %>
 <%include file="hprotokoll.hkogum.mako"/>
% endfor

${h.submit(_('Kinnita protokolli sisestus'), id='kinnita', clicked=True)}
% if c.sisestus != 'p':
${h.submit(_('Loobu'), id='loobu')}
% endif
## liik on selleks, et ValidationError korral otsinguvormi liik ära ei kaoks
${h.hidden('liik', c.hindamisprotokoll.liik)} 

## need väljad on selleks, et ValidationErrori korral järgmise vorm
## tühjaks ei tehtaks
${h.hidden('sisesta','1')}
${h.hidden('ta_tahised',c.toimumisaeg.tahised)}
${h.hidden('sessioon_id',c.toimumisaeg.testimiskord.testsessioon_id)}
${h.hidden('toimumisaeg_id',c.toimumisaeg.id)}
% if c.sisestus == 'p':
${h.hidden('sisestus','p')}
% endif

${h.end_form()}

${h.form_search(h.url('sisestamine_suulised'))}
${h.hidden('sisesta','1')}
${h.hidden('ta_tahised',c.toimumisaeg.tahised)}
${h.hidden('sessioon_id',c.toimumisaeg.testimiskord.testsessioon_id)}
${h.hidden('toimumisaeg_id',c.toimumisaeg.id)}
% if c.sisestus == 'p':
${h.hidden('sisestus','p')}
% else:
Järgmise protokolli tähis: 
## kui on seatud URLi parameeter focus, siis järgmise tähise väli saab fookuse
${h.text('tahis', c.jrg_tahis, size=16, class_=c.focus and 'initialfocus' or None)}
Hindamise liik:
${h.select('liik', c.hindamisprotokoll.liik, c.opt_liik, tabindex=100)}
% endif
${h.button(_('Järgmine'), id='otsi', onclick='this.form.submit()')}
${h.end_form()}

<script>
## formencode pandud kole teade "Erineb" teisendatakse punaseks kastiks
$(function(){
$.each($('.error'), function(n, item){
  $(item).closest('table.showerr').addClass('form-control').addClass('is-invalid');
  $(item).siblings('span.alert-danger').filter(function(){ return $(this).text().trim()=="Erineb";}).remove('');
});
});
</script>
