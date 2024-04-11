## Testiosa sooritamise vaatamine
<%inherit file="/common/page.mako"/>
<%def name="require()">
<%
c.includes['form'] = True
c.includes['countdown'] = True
c.includes['test'] = True
c.hide_header_footer = True
%>
</%def>
<% 
   c.url_to_alatest = lambda alatest :  h.url('test_labiviimine_alatestisooritusaknas', id=c.item.id, alatest_id=alatest.id, testiruum_id=c.testiruum_id, test_id=c.test.id)
   heading = None
%>
% if heading:
${heading}
% endif
##<h2>${c.sooritus.sooritaja.nimi}</h2>

% if c.tagasiside_html:
<div class="accordion" id="accordionSA">
  ${self.accordion_card_begin('ts', _("Tagasiside"), True)}
  ${c.tagasiside_html}
  ${self.accordion_card_end()}

  ${self.accordion_card_begin('vs', _("Vastused"), True)}
  ${self.vastused()}
  ${self.accordion_card_end()}
</div>
% else:
${self.vastused()}
% endif

<%def name="accordion_card_begin(card_id, label, expanded)">
  <div class="accordion-card card parent-accordion-card border-bottom-0">
    <div class="card-header" id="heading${card_id}">
      <div class="accordion-title">
        <button class="btn btn-link"
          type="button"
          data-toggle="collapse"
          data-target="#collapse${card_id}"
          aria-expanded="${expanded and 'true' or 'false'}"
          aria-controls="collapse${card_id}"
        >
          <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
            ${label}
          </span>
        </button>
      </div>
    </div>
    <div id="collapse${card_id}" class="collapse ${expanded and 'show' or ''}" aria-labelledby="heading${card_id}">
      <div class="card-body">
        <div class="content pb-0">
</%def>

<%def name="accordion_card_end()">
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="vastused()">
% if c.test.opetajale_peidus:
${h.alert_notice(_("Testi vastuseid õpetajale ei näidata!"), False)}
% else:
<%include file="/avalik/sooritamine/testiosasisu.mako"/>
% endif
</%def>
