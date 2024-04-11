<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('sub', 'proctorio')}
<div class="form-group row">
    <div class="col-md-6">
        <% params = (c.item.verif_param or '').split(',') %>
        ${h.checkbox('verif_param', 'recordvideo', checkedif=params,
        label=_("Video salvestamine"))}
        <br/>
        ${h.checkbox('verif_param', 'recordaudio', checkedif=params,
        label=_("Heli salvestamine"))}
        <br/>
        ${h.checkbox('verif_param', 'recordscreen', checkedif=params,
        label=_("Ekraanipildi salvestamine"))}
        <br/>
        ${h.checkbox('verif_param', 'recordwebtraffic', checkedif=params,
        label=_("Veebiliikluse salvestamine"))}
        <br/>
        ${h.checkbox('verif_param', 'recordroomstart', checkedif=params,
        label=_("Ruumi skannimine eksami alguses"))}
        <br/>
        ${h.checkbox('verif_param', 'verifyvideo', checkedif=params,
        label=_("Kaamera kontroll"))}
        <br/>
        ${h.checkbox('verif_param', 'verifyaudio', checkedif=params,
        label=_("Mikrofoni kontroll"))}
        <br/>
        ${h.checkbox('verif_param', 'verifydesktop', checkedif=params,
        label=_("Töölaua salvestamise kontroll"))}        
        <br/>
        ${h.checkbox('verif_param', 'verifyidauto', checkedif=params,
        label=_("Isikut tõendava dokumendi automaatkontroll enne eksamit"))}        
        <br/>
        ${h.checkbox('verif_param', 'verifysignature', checkedif=params,
        label=_("Lepingu allkirjastamine enne eksamit"))}
        <br/>
        ${h.checkbox('verif_param', 'fullscreensevere', checkedif=params,
        label=_("Eksam täisekraanil, täisekraanilt lahkumine lõpetab Proctorio seansi"))}
        <br/>
        ${h.checkbox('verif_param', 'clipboard', checkedif=params,
        label=_("Kopeerimine/kleepimine ning kontekstmenüü välja lülitatud"))}        
        <br/>
    </div>
    <div class="col-md-6">        
        ${h.checkbox('verif_param', 'notabs', checkedif=params,
        label=_("Uue akna või saki avamine keelatud"))}        
        <br/>
        ${h.checkbox('verif_param', 'linksonly', checkedif=params,
        label=_("Uue akna või saki avamine lubatud ainult EISi lehel olevate linkidega"))}
        <br/>
        ${h.checkbox('verif_param', 'closetabs', checkedif=params,
        label=_("Muud aknad ja sakid suletakse enne eksami algust"))}        
        <br/>
        ${h.checkbox('verif_param', 'onescreen', checkedif=params,
        label=_("Lubatud ainult üks monitor"))}        
        <br/>
        ${h.checkbox('verif_param', 'print', checkedif=params,
        label=_("Printimine keelatud"))}        
        <br/>
        ${h.checkbox('verif_param', 'downloads', checkedif=params,
        label=_("Failide allalaadimine keelatud"))}        
        <br/>
        ${h.checkbox('verif_param', 'cache', checkedif=params,
        label=_("Peale lõpetamist tühjendatakse ajutiste failide puhver"))}
        <br/>
        ${h.checkbox('verif_param', 'rightclick', checkedif=params,
        label=_("Parem hiireklikk välja lülitatud"))}
        <br/>
        ${h.checkbox('verif_param', 'noreentry', checkedif=params,
        label=_("Katkestamine lõpetab eksami"))}
        ##<br/>
        ##${h.checkbox('verif_param', 'agentreentry', checkedif=params,
        ##label=_("Katkestamisel saab jätkata Proctorio agendi loal"))}
        <br/>
        ${h.checkbox('verif_param', 'calculatorbasic', checkedif=params,
        label=_("Lubatud lihtne taskuarvuti"))}
        <br/>
        ${h.checkbox('verif_param', 'calculatorsci', checkedif=params,
        label=_("Lubatud teadusfunktsioonidega taskuarvuti"))}
        <br/>
        ${h.checkbox('verif_param', 'whiteboard', checkedif=params,
        label=_("Lubatud ajutised märkmed"))}                
    </div>
</div>
% if c.is_edit:
${h.submit_dlg()}
% endif
${h.end_form()}
