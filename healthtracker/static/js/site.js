$(function(){
    // Add data-confirm="...confirmation message..." to a link/input/button to get a confirm popup.
    $('[data-confirm]').on('click', function(event){
        var confirmationMessage = $(this).data('confirm');
        if(!confirm(confirmationMessage)){
            event.stopImmediatePropagation();
            return false;
        }
        return true;
    });


    $('a[data-action-url]').on('click', function(event){
        var actionURL = $(this).data('action-url');
        var actionMethod = $(this).data('action-method') || 'GET';
        $.ajax({url: actionURL,
                type: actionMethod,
                success: function(data, text, jqXHR){
                    window.location = ''; // TK IMPROVE (should do some ujs stuff c.f. rails.js)
                },
                error: function(jqXHR, status, error){
                    console.log('ERROR: ' + error);
                }
        });
    });
})
