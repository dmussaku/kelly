(function($, document, window, undefined) {
  'use strict';

  var toggle = '[data-toggle="dropdown"]';

  var Dropdown = function(element) {
    $(element).on('click.dropdown', this.toggle);
  }

  Dropdown.prototype.toggle = function(e) {
    e.preventDefault();

    var $toggle    = $(e.currentTarget);
    var $container = $toggle.parents('.dropdown');

    if ($container.hasClass('open')) {
      $container.removeClass('open');
      return;
    }

    var $triangle  = $container.find('.dropdown-triangle');
    var $menu      = $container.find('.dropdown-menu');

    $toggle.trigger('focus');
    $container.addClass('open');
  }

  Dropdown.prototype.keydown = function(e) {
    if (e.keyCode == 27) {
      clearDropdowns(e);
    }
  }

  function clearDropdowns(e) {
    var $target = $(e.target);
    var container = $target.parents('.dropdown')[0];

    var dropdowns = document.querySelectorAll('.dropdown');

    for (var i = 0; i < dropdowns.length; i++) {
      if ((dropdowns[i].classList.contains('open') && container !== dropdowns[i]) || e.keyCode == 27) {
        dropdowns[i].classList.remove('open');
      }
    }

  }

  $(document)
    .on('click.dropdown', clearDropdowns)
    .on('click.dropdown', toggle, Dropdown.prototype.toggle)
    .on('keydown.dropdown', toggle, Dropdown.prototype.keydown);

})(jQuery, document, window);

(function($, document, window, undefined) {
  'use strict'

  var toggle = '[data-toggle="showmore"]';

  var Showmore = function(element) {
    $(element).on('click.showmore', this.toggle);
  }

  Showmore.prototype.toggle = function(e) {
    e.preventDefault();

    var $toggle    = $(e.currentTarget);
    var $container = $toggle.parents('.showmore');

    var oldText    = $toggle.text();
    var newText    = $toggle.data('text');
    $toggle.text(newText).data('text', oldText);

    if ($container.hasClass('open')) {
      $container.removeClass('open');
      return;
    }

    $container.addClass('open');
  }

  $(document)
    .on('click.showmore', toggle, Showmore.prototype.toggle);

})(jQuery, document, window);


