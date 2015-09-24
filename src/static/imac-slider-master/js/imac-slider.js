$(function(){
  var $imac     = $('.imac'),
      $imgs     = $imac.find('img'),
      totalImgs = $imgs.length - 1,
      speed     = '10000';

  $imac.append('<div class="arrow"><a href="#" class="aleft" /><a href="#" class="aright" /></div>');

  $imgs.not(':first').css('display', 'none').addClass('hidden');

  var slideNext = function(target){
    target.next().fadeOut(0).removeClass('hidden').fadeIn('slow');
  }
  var slidePrev = function(target){
    target.prev().fadeOut(0).removeClass('hidden').fadeIn('slow');
  }
  var slideFirst = function(target){
    target.closest($imac).find('img:first').fadeOut(0).removeClass('hidden').fadeIn('slow');
  }
  var slideLast = function(target){
    target.closest($imac).find('img:last').fadeOut(0).removeClass('hidden').fadeIn('slow');
  }

  var slider = function (direction){
    $imgs.each(function(i){
      var target = $(this);
      if(!target.hasClass('hidden')){
        target.fadeOut('slow', function(){
          target.addClass('hidden');
          if(direction === 'prev'){
            sliderPrev(i, target);
          }else{
            sliderNext(i, target);
          }
        });
      }
    });
  }

  var sliderNext = function (i, target){
    if(i < totalImgs) {
      slideNext(target);
    }else{
      slideFirst(target);
    }
  }

  var sliderPrev = function (i, target){
    if(!i == 0) {
      slidePrev(target);
    }else{
      slideLast(target);
    }
  }

  var int = setInterval(slider, speed);

  $imac.hover(function(){
    clearInterval(int);
  }, function(){
    setTimeout(function() {
      int = setInterval(slider, speed);
    });
  });

  $('.arrow .aleft').click(function(){
    slider('prev');
  });

  $('.arrow .aright').click(function(){
    slider();
  });

});