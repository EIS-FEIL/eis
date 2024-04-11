$(document).ready(function(){
    $('select#aine').change(
        function(){
            update_options(this,
                           "${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}",
                           'ylem_kood', 
                           $('select#oskus'),
                           null,
                           null,
                           null,
                           toggle_oskus);
            update_options(this, 
                           "${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                           'ylem_kood', 
                           $('select#keeletase'),
                           null,
                           null,
                           null,
                           toggle_keeletase);
        });
    $('select#aine').change(function(){change_teema();});
    $('select#valdkond').change(function(){change_alateema();});

    toggle_oskus();
    toggle_keeletase();
});
function toggle_oskus()
{
    $('tr.oskus').toggle($('select#oskus option').length > 1);
}
function toggle_keeletase()
{
    $('tr.keeletase').toggle($('select#keeletase option').length > 1);
}
function change_teema()
{
    var aine_field = $('select#aine');
    var aste_kood = $('select#aste').val();
    var url = "${h.url('pub_formatted_valikud', kood='TEEMA', format='json')}";
    var data = {aste: aste_kood};
    var target = $('select#valdkond');
    var subtarget = $('select#teema');
    update_options(aine_field, url, 'ylem_kood', target, data, subtarget, true);
}
function change_alateema()
{
    var teema_id = $('select#valdkond option:selected').attr('name');
    if(teema_id)
    {
        var aine_kood = $('select#aine').val();
        var aste_kood = $('select#aste').val();      
        var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA', format='json')}";
        var data = {ylem_id: teema_id, aste: aste_kood, aine: aine_kood};
        var target = $('select#teema');
        update_options(null, url, null, target, data);
    }
}
