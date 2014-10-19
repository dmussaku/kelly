function click_event(my_url){
  console.log('click_event');
  var myurl = my_url;
  $.get(myurl, function(data){
    var div_class = '.comments';
    $(div_class).html(data);
    return false;
  });
  return false;
}
/*
Script for ajax post of a comment
*/
function comment_submit(){
  console.log($(this));
}


$(document).on('submit', '#comment-form', function() {
  var postData = $(this).serialize();
  var my_url = $(this).attr('url');
  console.log(postData);
  $.ajax({
    type:'POST',
    url: my_url,
    data: postData,
    success: function(data){
      $.get(my_url, function(data){
        var div_class = '.comments';
        $(div_class).html(data);
        return false;
      });
      console.log('asdas');
    }
  });
  return false;
});


function delete_comment(obj, id) {
    var comment_div = $('#comment-'+id);
    if (confirm('Are you sure you want to delete this comment')) {
        $.ajax({
          type: "GET",
          url: $(obj).attr('link'),
          success: function(data){
            comment_div.animate({ opacity: 'hide' }, "slow");
          }
        });
    }
}
$.comments = {
  'click_event': click_event,
}
