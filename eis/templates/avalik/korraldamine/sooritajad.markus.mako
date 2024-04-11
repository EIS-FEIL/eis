## -*- coding: utf-8 -*- 
## $Id: sooritajad.markus.mako 544 2016-04-01 09:07:15Z ahti $         

${h.form_save(None)}
${h.hidden('sub','markus')}
${h.textarea('markus', c.testikoht.markus, rows=12)}
${h.submit(_("Salvesta"))}
${h.end_form()}
