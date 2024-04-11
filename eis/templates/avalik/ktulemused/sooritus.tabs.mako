## Testiosa soorituse vaatamine
<%namespace name="tab" file='/common/tab.mako'/>
<%
  lang = c.sooritaja.lang
  kursus = c.sooritaja.kursus_kood
  has_opetaja = c.FeedbackReport.init_opetaja(handler, c.test, lang, kursus, check=True)
  has_opilane = c.FeedbackReport.init_opilane(handler, c.test, lang, kursus, check=True, opetajale=True)
%>
% if has_opetaja or not has_opilane:
${tab.draw('opetajatulemus', h.url('ktulemused_opetajatulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or '', id=c.sooritaja.id), _("Õpetaja tagasiside"), c.tab2)}
% endif
% if has_opilane:
${tab.draw('opilasetulemus', h.url('ktulemused_opilasetulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or '', id=c.sooritaja.id), _("Õpilase tagasiside"), c.tab2)}
% endif
% if c.ylesanded_avaldet:
% for tos in c.sooritaja.sooritused:
${tab.draw(tos.id, h.url('ktulemused_osa', test_id=c.test.id, testimiskord_id=c.testimiskord.id, testiosa_id=tos.testiosa_id, alatest_id='', kursus=c.kursus or '', id=tos.id), tos.testiosa.tahis, c.tab2)}
% endfor
% endif
