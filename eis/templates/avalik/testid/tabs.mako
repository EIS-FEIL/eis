## -*- coding: utf-8 -*- 
<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
   # c.test on Test või MemTest 
   can_view_test = c.user.has_permission('testid', const.BT_SHOW, test_id=c.test.id)
   nk_obj = c.nimekiri or c.testiruum and c.testiruum.nimekiri or c.testiruum
   can_view_nk = nk_obj and c.user.has_permission('omanimekirjad', const.BT_SHOW, nk_obj)
   is_sooritus = c.sooritus and c.sooritus.id and not model.is_temp_id(c.sooritus.id)
   is_sooritaja = c.sooritaja and c.sooritaja.id and not model.is_temp_id(c.sooritaja.id)
   is_hindaja = bool(c.hindaja)
%>
% if c.test and c.test.id:
  % if can_view_test:
<% title = c.test.on_jagatudtoo and _("Töö kirjeldus") or _("Testi kirjeldus") %>
    % if c.testiruum_id and c.testiruum_id != '0':
${tab.draw('yldandmed', h.url('testid_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id), title, c.tab1)}
    % else:
${tab.draw('yldandmed', h.url('test', id=c.test_id),  title, c.tab1)}
    % endif
  % endif
  % if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and can_view_test:
    % if c.test.on_jagatudtoo:
${tab.draw('struktuur', h.url('testid_struktuur', id=c.test_id, testiruum_id=c.testiruum_id),  _('Töö sisu'), c.tab1)}
    % else:
${tab.draw('struktuur', h.url('testid_struktuur', id=c.test_id, testiruum_id=c.testiruum_id, testiosa_id=c.testiosa_id),  _('Testi sisu'), c.tab1)}
    % endif
  % endif
  % if not c.test.on_jagatudtoo and can_view_test:
${tab.draw('eelvaade', h.url('test_new_eelvaade',test_id=c.test_id, testiruum_id=c.testiruum_id, e_komplekt_id=0, alatest_id='', testiosa_id=c.testiosa_id), _('Eelvaade'), c.tab1)}
  % endif

  % if c.user.has_permission('omanimekirjad', const.BT_CREATE, test_id=c.test.id) or c.testiruum_id and c.user.has_permission('omanimekirjad', const.BT_VIEW, testiruum_id=c.testiruum_id):
${tab.draw('nimekirjad', h.url('test_nimekirjad',test_id=c.test_id, testiruum_id=c.testiruum_id),  _('Nimekiri'), c.tab1)}
  % endif

  % if c.testiruum_id and c.testiruum_id != '0' and is_sooritaja and c.nimekiri and not c.test.diagnoosiv:
${tab.draw('kanne', h.url('test_nimekiri_kanne', test_id=c.test_id, testiruum_id=c.testiruum_id, nimekiri_id=c.nimekiri.id, id=c.sooritaja.id),  _('Registreering'), c.tab1)}
  % endif

  % if c.testiruum_id and c.testiruum_id != '0' or c.test.on_avaliktest and can_view_nk:
${tab.draw('labiviimine', h.url('testid_edit_labiviimine', test_id=c.test_id, id=c.testiruum_id or 0, testiosa_id=c.testiosa_id),  _('Läbiviimine'), c.tab1)}

    % if c.test.testiliik_kood == const.TESTILIIK_KUTSE and c.test.avaldamistase == const.AVALIK_MAARATUD:
${tab.draw('protokoll', h.url('test_protokoll', test_id=c.test_id, testiruum_id=c.testiruum_id),  _('Protokoll'), c.tab1)}
    % endif

    % if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and (can_view_test or is_hindaja) and can_view_nk:
      % if c.test.on_kasitsihinnatav and c.testiruum_id and c.testiruum_id != '0' and not c.test.opetajale_peidus:
${tab.draw('hindamised', h.url('test_ylesandehindamised', test_id=c.test_id, testiruum_id=c.testiruum_id),  _('Hindamine'), c.tab1)}
      % endif
    % endif

    % if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and can_view_nk:
      % if c.test.tagasiside_mall is not None:
${tab.draw('tagasiside', h.url('test_tagasiside', test_id=c.test_id, testiruum_id=c.testiruum_id),  _('Tulemused'), c.tab1)}
      % elif c.test.on_jagatudtoo:
${tab.draw('avtulemused', h.url('test_tootulemused', test_id=c.test_id, testiruum_id=c.testiruum_id),  _('Tulemused'), c.tab1)}
      % else:
${tab.draw('avtulemused', h.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id or 0),  _('Tulemused'), c.tab1)}
      % endif
    % endif
  % endif

  % if c.testiruum_id and c.testiruum_id != '0':
    % if is_sooritus:
      % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
${tab.draw('psyhtulemus', h.url('test_psyhtulemus', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritus.id),  _('Tulemus'), c.tab1)}
      % endif
      % if c.sooritus.staatus == const.S_STAATUS_TEHTUD or c.test.on_jagatudtoo:
        % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
${tab.draw('sooritus', h.url('test_labiviimine_sooritus', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritus.id),  _('Sooritus'), c.tab1)}
        % else:
${tab.draw('sooritus', h.url('test_labiviimine_sooritus', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritus.id, grupp_id=c.grupp_id, ty_id=c.ty_id),  _('Sooritus'), c.tab1)}
        % endif
      % endif
    % elif c.ty and c.vy:
${tab.draw('tysooritus', h.url('test_hindamine_edit_ylesanne',test_id=c.test_id,testiruum_id=c.testiruum.id, id=c.vy.id, lang=c.lang),  _('Ülesanne {s}').format(s=c.ty.seq), c.tab1)}
    % elif is_sooritaja and c.test.tagasiside_mall is not None:
${tab.draw('sooritus', h.url('test_tagasiside1', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritaja.id),  _('Sooritus'), c.tab1)}
    % endif
  % endif

% else:
${tab.draw('testid', None,  _('Testi kirjeldus'))}
${tab.draw('struktuur', None,  _('Testi sisu'), c.tab1)}
${tab.draw('eelvaade', None,  _('Eelvaade'), c.tab1)}
${tab.draw('vastused', None,  _('Vastuste analüüs'), c.tab1)}
% endif
