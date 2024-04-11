function update_teema_yo()
{
    var aine_field = $('form#yo_search select#aine');
    var aste_kood = $('form#yo_search select#aste').val();
    var url = "${h.url('pub_formatted_valikud', kood='TEEMA', format='json')}";
    var data = {aste: aste_kood};
    var target = $('form#yo_search select#teema');
    var subtarget = $('form#yo_search select#alateema');
    update_options(aine_field, url, 'ylem_kood', target, data, subtarget, true);
}
function update_alateema_yo()
{
    var teema_id = $('form#yo_search select#teema option:selected').attr('name');
    if(teema_id)
    {
        var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA',format='json')}";
        var target = $('form#yo_search select#alateema');
        var data = {ylem_id: teema_id};
        update_options(null, url, null, target, data);
    }
}
function update_opitulemus_yo()
{
    var aine_kood = $('form#yo_search select#aine').val();
    var url = "${h.url('pub_formatted_valikud', kood='OPITULEMUS', format='json')}";
    var data = {aine: aine_kood};
    var target = $('form#yo_search select#opitulemus_id');
    update_options(null, url, null, target, data);
}     
function toggle_keeletase_yo()
{
    $('form#yo_search tr.keeletase').toggle($('form#yo_search select#keeletase option').length > 1);
}

$(function(){
    $('form#yo_search select#aine').change(function(){update_teema_yo(); update_opitulemus_yo();});
    $('form#yo_search select#aste').change(function(){update_teema_yo();});
    $('form#yo_search select#teema').change(function(){update_alateema_yo();});
    $('form#yo_search select[name="aine"]').change(function(){
        update_options(this, 
                       "${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                       'ylem_kood', 
                       $('form#yo_search select#keeletase'),
                       null,
                       null,
                       null,
                       toggle_keeletase_yo);
    });
    toggle_keeletase_yo();
});

function toggle_add_yl(){   
    var visible = ($('div#listdiv_yl input:checked[name="ylesanne_id"]').length > 0);
    $('div#listdiv_yl span#add').toggleClass('invisible', !visible);
}
$(function(){
    //## ylesande märkeruudu klikkimisel kuvame/peidame salvestamise nupu
    $('div#listdiv_yl').on('click', 'input[name="ylesanne_id"]', toggle_add_yl);
    $('div#listdiv_yl').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="ylesanne_id"]').prop('checked', this.checked);
        toggle_add_yl();
    });

    ## dialoogiaknas teise saki valimisel kontrollime dialoogi kõrgust
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
        ##var target = $(e.target).attr('href');
        hold_dlg_height(null, false, $(this));
    });
});
         
