var result_list = function(data){
    var result_list = [];
    for (var i in data){
      result_list.push({value:data[i].name});
    }
    console.log(result_list);
    return result_list;
  };

$(document).ready(function(){
  $('#scrollable-dropdown-menu .typeahead').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'states',
    displayKey: 'name',
    source: function(query, process){
      var url = $(this.$el).closest('div.js-search-block').data('url');
      return $.ajax({
        type:'GET',
        url:'http://bwayne.alma.net:8000/almcrm/contacts/search/'+query+'/',
        success: function(data){
          return process(data);
        }
      });
    }
  });
})
