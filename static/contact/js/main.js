$(function() {
	'use strict';

	// Form

	var contactForm = function() {

		if ($('#contactForm').length > 0 ) {
			$( "#contactForm" ).validate( {
				rules: {
					fname: "required",
					lname: "required",
					email: {
						required: true,
						email: true
					},
					message: {
						required: true,
						minlength: 5
					}
				},
				messages: {
					fname: "Please enter your first name",
					lname: "Please enter your last name",
					email: "Please enter a valid email address",
					message: "Please enter a message"
				},
				/* submit via ajax */
				submitHandler: function(form) {
					var $submit = $('.submitting'),
						waitText = 'Submitting...';

					$.ajax({
				      type: "POST",
				      url: "",
				      data: $(form).serialize(),

				      beforeSend: function() {
				      	$submit.css('display', 'block').text(waitText);
				      },
				      success: function(response) {
    if (response.status == 'success') {
      $('#form-messages').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
      $('#contactForm')[0].reset();
    } else {
      $('#form-messages').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
    }
  },
  error: function() {
    $('#form-messages').html('<div class="alert alert-danger" role="alert">Something went wrong. Please try again.</div>');
  },
  complete: function() {
    $submit.css('display', 'none');
  }
});
		  		}
				
			} );
		}
	};
	contactForm();

});