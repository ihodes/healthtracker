$(function(){
  $('#change-pw-modal .btn-primary').on('click', function(){
    $('#change-pw-form').submit();
  });
  
  $('#edit-profile').on('click', function(){
    $(this).fadeOut(100, function(){ $('#remove-edit-profile').fadeIn(100);});
    $('#profile-fields').slideDown();
  });
  
  $('#remove-edit-profile').on('click', function(){
    $(this).fadeOut(100, function(){ $('#edit-profile').fadeIn(100);});
    $('#profile-fields').slideUp();
  });
  
  $('#profile-fields .close').on('click', function(){
    $('#profile-fields').slideUp();
    $('#edit-profile').fadeIn(100);
  });
  
  $('i').tooltip();
  
  $('.icon-edit').on('click', function(){
    var thisTr = $(this).parent().parent().parent()
    var editTr = $(thisTr).next();
    $('.icon-edit').fadeIn(100);
    $('.edit-scheduled-question').fadeOut(100);
    $(editTr).show();
    $(this).fadeOut(100, function(){
      $(this).parent().siblings('.sq-edit-close').fadeIn(100);
    });
  });
  
  $('.sq-edit-close').on('click', function(){
    var editTr = $(this).parent().parent().next();
    $(editTr).hide();
    $(this).fadeOut(100, function(){$('.icon-edit').fadeIn(100);});
  });
  
  $('form .icon-remove').on('click', function(){$(this).parent().parent().submit()});
  
  $('#show-add-question').on('click', function(){
    $(this).fadeOut(100, function(){ $('#remove-add-question').fadeIn(100);});
    $('#add-question-controls').slideDown();
  });
  
  $('#remove-add-question').on('click', function(){
    $(this).fadeOut(100, function(){  $('#show-add-question').fadeIn(100);});
    $('#add-question-controls').slideUp();
  });


  $('#question-search').on('keyup', function(){
    var searchTerm = $(this).val().toLowerCase();
    var shown = 0;

    $('#question-table tr td.text').each(function(idx, el){
      var row = $(el).parent();
      var qtext = $(el).text().toLowerCase();
      var qname = $(el).prev().text().toLowerCase();
      if((qtext.indexOf(searchTerm) + qname.indexOf(searchTerm)) != -2){
        row.show();
        shown += 1;
      } else {
        row.hide();
      }
    });

    if(shown > 0) {
      $('#question-table').show();
      $('#no-questions-notify').hide();
    } else {
      $('#no-questions-notify').show();
      $('#question-table').hide();
      $('#question-table tr').hide();
    }

    if(searchTerm.length == 0) {
      $('#question-table').show();
      $('#question-table tr').show();
    }
  });

  // schedule additional question
  $('form .icon-plus').on('click', function(){$(this).parent().parent().submit()});


    ///////////////////////////////////////////////////////////////////
   //                 Create Question Modal Code                    //
  ///////////////////////////////////////////////////////////////////
  $('#add-question-modal .btn-primary').on('click', function(){
    $('#add-question-form').submit();
  });

  $('#add-question-modal a.btn').on('click', function(){
    var active = this.id == 'numeric-button'
    if(active) {
      if($('#add-question-modal #unlimited-checkbox').prop('checked')){
        $('#add-question-modal input[name="qtype"]').val('numeric');
      } else {
        $('#add-question-modal input[name="qtype"]').val('multi_numeric');
      }
      $('#numeric-options').slideDown();
    } else {
      $('#add-question-modal input[name="qtype"]').val('yesno');
      $('#numeric-options').slideUp();
    }
  });

  $('#add-question-modal #unlimited-checkbox').on('click', function(){
    if($(this).prop('checked')){
      $('#add-question-modal input[name="qtype"]').val('numeric');
    } else {
      $('#add-question-modal input[name="qtype"]').val('multi_numeric');
    }
    $('.minmax-input').slideToggle();
  });
});
