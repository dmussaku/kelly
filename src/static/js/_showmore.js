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
