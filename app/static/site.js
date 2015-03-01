
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
    $('[data-toggle="popover"]').popover()

    // If there is error in form submission, reshow modal forms
    if ($('.has-error').length > 0) {
	$('#formModal').modal('show');
    }
})
