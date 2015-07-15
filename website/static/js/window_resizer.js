
  $(document).ready(function() {
    // Optimalisation: Store the references outside the event handler:
    var $window = $(window);

    function checkWidth() {
        var windowsize = $window.width();
        if (windowsize > 1440) {
          $('.main-content-container-small').show();
          $('.main-content-container-medium').hide();
        }

        if (windowsize > 1720) {
          $('.main-content-container-small').hide();
          $('.main-content-container-medium').show();
        }


    }
    // Execute on load
    checkWidth();
    // Bind event listener
    $(window).resize(checkWidth);
  });
