odoo.define('listing_box', function (require) {
    "use strict";
var ajax = require('web.ajax');
$(document).ready(function()
{
	

	/* 

	1. Vars and Inits

	*/
	console.log("hello world");
	var header = $('.header');

	initMenu();
	initIsotope();

	setHeader();

	$(window).on('resize', function()
	{
		setHeader();

		setTimeout(function()
		{
			$(window).trigger('resize.px.parallax');
		}, 375);
	});

	$(document).on('scroll', function()
	{
		setHeader();
	});

	/* 

	2. Set Header

	*/

	function setHeader()
	{
		if($(window).scrollTop() > 91)
		{
			header.addClass('scrolled');
		}
		else
		{
			header.removeClass('scrolled');
		}
	}

	/* 

	3. Init Menu

	*/

	function initMenu()
	{
		if($('.menu').length && $('.hamburger').length)
		{
			var menu = $('.menu');
			var hamburger = $('.hamburger');
			var close = $('.menu_close');
			var superOverlay = $('.super_overlay');

			hamburger.on('click', function()
			{
				menu.toggleClass('active');
				superOverlay.toggleClass('active');
			});

			close.on('click', function()
			{
				menu.toggleClass('active');
				superOverlay.toggleClass('active');
			});

			superOverlay.on('click', function()
			{
				menu.toggleClass('active');
				superOverlay.toggleClass('active');
			});
		}
	}

	/* 

	4. Init Isotope

	*/

	function initIsotope()
	{
		if($('.listings_container').length)
		{
			var grid = $('.listings_container');
			grid.isotope(
			{
				itemSelector:'.listing_box',
				layoutMode: 'fitRows',
				getSortData:
	            {
	            	price: function(itemElement)
	            	{
	            		var priceEle = $(itemElement).find('.listing_price').text().replace( '$', '' );
	            		priceEle = priceEle.replace(/\s/g, '');
	            		return parseFloat(priceEle);
	            	},
	            	area: function(itemElement)
	            	{
	            		var propertyArea = $(itemElement).find('.property_area span').text().replace(' sq ft', '');
	            		console.log(propertyArea);
	            		return parseFloat(propertyArea);
	            	}
	            }
			});

			var sortingButtons = $('.sorting_button');

			sortingButtons.each(function()
	        {
	        	$(this).on('click', function()
	        	{
	        		var parent = $(this).parent().parent().find('span');
		        		parent.text($(this).text());
		        		var option = $(this).attr('data-isotope-option');
		        		option = JSON.parse( option );
	    				grid.isotope( option );
	        	});
	        });
		}
	}

})});