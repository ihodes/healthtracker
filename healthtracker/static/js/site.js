$(function(){
    $('[data-confirm]').on('click', function(event){
        var confirmationMessage = $(this).data('confirm');
        return confirm(confirmationMessage);
    });
})
