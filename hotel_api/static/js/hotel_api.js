$.fn.stars = function() {
	return $(this).each(function() {
		var width = Math.max(0, (Math.min(5, parseFloat($(this).html())))) * 16;
		$(this).width(width);
		$(this).html('');
	});
}

function filter_submit()
{
	$( "#id_real_radius" ).val($( "#id_radius" ).val());
	$('#id_chain').val($('#filter_form').serialize());
	$('#search-form').submit();
}

function search_hotel()
{
	var place = $('#id_place').val().trim();
	var checkin = $('#id_checkin').val().trim();
	var checkout = $('#id_checkout').val().trim();

	if (place == '') {
		$('#id_place').focus();
		return false;
	} else if(checkin == '') {
		$('#id_checkin').focus();
		return false;
	} else if(checkout=='') {
		$('#id_checkout').focus();
		return false;		
	}
	$('#search-form').submit();
}

$(function(){
	var url_on_tweet = $('#twitter_share').attr('href');
	if (url_on_tweet != undefined) {
		url_on_tweet = url_on_tweet.replace(/%2C/g, '0');
		url_on_tweet = url_on_tweet.replace(/%20/g, '_');
		url_on_tweet = url_on_tweet.replace(/%29/g, '1');

		$('#twitter_content').val($('#twitter_content').val()+url_on_tweet);
		$('#twitter_share').click(function() {
			this.href = 'https://twitter.com/home?status=' + $('#twitter_content').val();

			window.open(this.href, 'newwindow', 'width=600, height=250');
			return false;

		});

		$('#social_share').click(function() {
			window.open(this.href, 'newwindow', 'width=600, height=250');
			return false;
		});	
	}
	$('#id_checkin').datepicker({
		dateFormat: "yy-mm-dd",
		minDate: 0,
		onSelect: function() {
			setTimeout(function func(argument) {
				$("#id_checkout").focus();	
			}, 200);
		},
		onClose: function(selectedDate) {
			// $("#id_checkout").focus();
			// Set the minDate of 'to' as the selectedDate of 'from'
			$("#id_checkout").datepicker("option", "minDate", selectedDate);
		}
	});

	$('#id_checkout').datepicker({dateFormat: "yy-mm-dd",});

	if (typeof price_low !== 'undefined')
	{
	  $( "#price-range" ).slider({
		range: true,
		min: price_lowest,
		max: price_highest,
		values: [price_low, price_high],
		slide: function( event, ui ) {
		  $( "#id_price_low" ).val( ui.values[ 0 ] );
		  $( "#id_price_high" ).val( ui.values[ 1 ] );
		  $( "#dis_price_low" ).html( '$'+ui.values[ 0 ] );
		  $( "#dis_price_high" ).html( '$'+ui.values[ 1 ] );
		}
	  });
	  $( "#award-range" ).slider({
		range: true,
		min: award_lowest,
		max: award_highest,
		values: [award_low, award_high],
		slide: function( event, ui ) {
		  $( "#id_award_low" ).val( ui.values[ 0 ] );
		  $( "#id_award_high" ).val( ui.values[ 1 ] );
		  $( "#dis_award_low" ).html( ui.values[ 0 ] );
		  $( "#dis_award_high" ).html( ui.values[ 1 ] );
		}
	  });		
	}

    function log( message ) {
      $( "<div>" ).text( message ).prependTo( "#log" );
      $( "#log" ).scrollTop( 0 );
    }

    $( "#id_place" ).autocomplete({
	  autoFocus: true,
      source: function( request, response ) {
        $.ajax({
          url: "http://wandr.me/scripts/Hustle/HustleAirportLookup.ashx",
          data: {
            term: request.term
          },
          success: function( data ) {
            data = JSON.parse(data);
            // console.log(data);
            response( data );
          }
        });
      },
      minLength: 3,
      select: function( event, ui ) {
        log( ui.item ?
          "Selected: " + ui.item.label :
          "Nothing selected, input was " + this.value);
      },
      open: function() {
        $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
      },
      close: function() {
        $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
      }
    });  	  
});

