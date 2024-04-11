function toggle_add_tk(){   
    var visible = ($('div#listdiv_tk input:checked[name="ylesanne_id"]').length > 0);
    $('div#listdiv_tk span#add').toggleClass('invisible', !visible);
}
$(function(){
    ## töökogumiku valimisel teha kohe otsing
    $('#tookogumik_id').change(function(){
        submit_dlg(this, $('#listdiv_tk'));
    });
    ## ylesande märkeruudu klikkimisel kuvame/peidame salvestamise nupu
    $('div#listdiv_tk').on('click', 'input[name="ylesanne_id"]', toggle_add_tk);
    $('div#listdiv_tk').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="ylesanne_id"]').prop('checked', this.checked);
        toggle_add_tk();
    });
});
