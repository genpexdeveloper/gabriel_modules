// DOCUMENT LOADED
$(document).ready(function() {
    // ACCOUNT ADDRESS
    $('.aj-address-submit').click(function() {
        var form = $(this).closest('form');
        var data = form.serializeObject();
        // fix select2
        data.disease_ids = form.find('select[name=disease_ids]').val();
        if (Array.isArray(data.disease_ids)) data.disease_ids = data.disease_ids.join();
        ip_model.ajax({
            url: '/account/address/update',
            type: 'POST',
            data: data
        }, function() {
            window.location = "/account/address";
        }, function(response) {
            form.find('.error').removeClass('error');
            _.each(response, function(v, k) {
                form.find('[name="' + k + '"]').parents('tr:first').addClass('error');
            });
        }, function() {
            $('#aj-profile-failed').modal('show');
        });
    });
    // UNBIND MODULE'S IP_WEB_ADDONS AUTOSHIP UPDATE HOOK & REBIND
    $('a.update').unbind('click').html('<i class="glyphicon glyphicon-ok"></i>');
    $('a.update').on('click', function(e) {
        e.preventDefault();
        // get elements, id and values
        var element = $(this);
        var auto_ship_id = element.closest("*[data-auto-ship-id]").attr('data-auto-ship-id');
        var interval = $('*[data-auto-ship-id="' + auto_ship_id + '"] .interval').val();
        var end_date = $('*[data-auto-ship-id="' + auto_ship_id + '"] .end_date').val();
        // send update 
        ip_model.ajax({
            url: "/account/auto-ship/update/" + auto_ship_id,
            type: 'POST',
            data: {
                interval: interval,
                end_date: end_date
            }
        }, function() {
            $('#aj-autoship-updated').modal('show');
        }, function() {}, function() {
            $('#aj-autoship-remove').modal('hide');
            $('#aj-error-modal').modal('show');
        });
    });
    // UNBIND MODULE'S IP_WEB_ADDONS AUTOSHIP REMOVE HOOK & REBIND
    $('a.delete').removeAttr('onclick').unbind('click').html('<i class="glyphicon glyphicon-remove"></i>');
    $('a.delete').on('click', function(e) {
        e.preventDefault();
        // get elements and id
        var element = $(this);
        var parent = element.closest("*[data-auto-ship-id]");
        var auto_ship_id = parent.attr('data-auto-ship-id');
        $('#aj-autoship-remove').attr('data-autoship-id', auto_ship_id).modal('show');
    });
    $('#aj-autoship-remove-confirm').on('click', function(e) {
        e.preventDefault();
        // send deactivation request 
        ip_model.ajax({
            url: "/account/auto-ship/delete/" + $('#aj-autoship-remove').attr('data-autoship-id'),
            async: false
        }, function() {
            window.location = '/account/auto-ships';
        }, function() {}, function() {
            $('#aj-autoship-remove').modal('hide');
            $('#aj-error-modal').modal('show');
        });
    });
});