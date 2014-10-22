function click_event(my_url){
  console.log('click_event');
  var myurl = my_url;
  $.get(myurl, function(data){
    var div_class = '.comments';
    $(div_class).append(data);
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
  var my_url = $(this).attr('url');
  var set_added_mentions = function (mentions) {

    $(this).find('[name="mention_ids"]')
      .val( JSON.stringify($.map(mentions, function (m) {return m.id;})) );

    console.log('mention_ids:')
    console.log(mentions);

    $.ajax({
      type:'POST',
      url: my_url,
      data: $(this).serialize(),
      success: function(data){
        $.get(my_url, function(data){
          var div_class = '.comments';
          $(div_class).html(data).animate({opacity:'show'}, "slow");
          return false;
        });
        console.log('asdas');
      }
    });
  };

  $(this).find('#textArea')
    .mentionsInput('getMentions', $.proxy(set_added_mentions, this));

  return false;
});

$(document).on('submit', '#edit-comment-form', function (event) {
  var get_url = $(this).attr('url');
  var my_url = $(this).attr('edit-url');

  $.post(
    my_url,
    $(this).serialize() + '&id=' + $(this).attr('comment_id'),
    function(){
      $.get(get_url, function(data){
        var div_class = '.comments';
        $(div_class).html(data).animate({opacity:'show'}, "slow");
        return false;
      });
    });

  return false;
});


function delete_comment(url,id){
  if (confirm("Are you sure you want to delete that comment?")){
    var csrf = $('#csrf').val();
    $.post(url,
    {
      csrfmiddlewaretoken: csrf,
      id: id
    },
    function(){
      var comment_div = '.comment-'+id;
      $(comment_div).animate({ opacity: 'hide' }, "slow");
    });
  }
}

function edit_form(id){
  /*catching the add comment form at the end of comment list
  remove form at the end and paste it into the place where the edit happens
  then it selects the div and hides all the buttons in comments
  but then returns buttons for edit form
  */
  var comment_div = '.comment-'+id;
  side_list = $('.showComments .lineGroup .lineGroup-extra');
  var side_div=side_list.filter(function(){
    return $(this).css('opacity')==1;
  });
  var comment_form = $(side_div).find('#add-comment-form');
  $(side_div).find('#add-comment-form').hide();
  var comment_div = $(side_div).find(comment_div);
  var initial_text = $(side_div).find(comment_div).find('#comment-text').text();
  console.log(initial_text);
  $(comment_div).html(comment_form.html());
  $(':button').hide()
  $(comment_div).find(':button').show();
  $(comment_div).find('#textArea').val(initial_text.toString());
  comment_form = $(comment_div).find('#comment-form');
  comment_form.attr('id','edit-comment-form');
  comment_form.attr('comment_id',id);
  // $('#cancel-button').on('click',function(){
  //     $.get(comment_form.attr('get-url'), function(data){
  //       var div_class = '.comments';
  //       $(div_class).html(data);
  //       return false;
  //     });
  // });
}

function post_edit_comment(id, comment){
  url = $('#edit-button').attr('url');
  get_url = $('#edit-button').attr('return-url');
  $.post(url,
    {
      'id':id,
      'comment':comment,
    },
    function(){
      click_event(get_url);
    }
  );
}


$.comments = {
  'click_event': click_event,
  'delete_comment': delete_comment,
  'edit_form': edit_form,
}
