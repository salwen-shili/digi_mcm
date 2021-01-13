$(function() {
	if ($('#s_hero_banner').length > 0) {
		$("header").addClass("navbar-trans-header");
		$(".navbar-light").addClass("navbar-tras");
		if ($('#s_hero_banner').length > 0) {
			$("#wrap").removeClass("wrap-trans");
		}
		else {
			
			$("#wrap").addClass("wrap-trans");
		}
	} else {
		$(".navbar-light").removeClass("navbar-tras");
	}
	
})

$(document).ready(function(){
	
	 if ($("header").hasClass("header_four")) {
		 if ($("div").hasClass("homepage")) {
	 		  	$('.h16-navbar').addClass('h-top-33');
	 		}
 	  }
	
	$(function() {
			var a = 0;
			$(window).scroll(function() {
				if ($(this).scrollTop() > 100) {
					if ( $('.counter-box').length > 0 ) {
						var oTop = $('.counter-box').offset().top - window.innerHeight;
						if (a == 0 && $(window).scrollTop() > oTop) {
							$('.counter').each(function () {
						    $(this).prop('Counter',0).animate({
						        Counter: $(this).text()
						    }, {
						        duration: 4000,
						        easing: 'swing',
						        step: function (now) {
						            $(this).text(Math.ceil(now));
						        }
						    	});
							}); 
							a = 1;
						}
					}
				} 
			});
			
		});
});

$(function() {
	$("#to-top").hide();
    	$(function() {
    		$(window).scroll(function() {
    			if ($(this).scrollTop() > 100) {
    				$('#to-top').fadeIn();
    			} else {
    				$('#to-top').fadeOut();
    			}
    		});
    		$('#to-top a').click(function() {
    			$('body,html').animate({
    				scrollTop : 0
    			}, 800);
    			return false;
    		});
    	});
});
