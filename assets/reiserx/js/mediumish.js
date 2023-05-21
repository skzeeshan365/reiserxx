var prevScrollpos = window.pageYOffset;
    window.onscroll = function () {
        var currentScrollPos = window.pageYOffset;
        if (prevScrollpos > currentScrollPos) {
            document.querySelector(".navbar.fixed-top").classList.remove("hidden");
        } else {
            document.querySelector(".navbar.fixed-top").classList.add("hidden");
        }
        prevScrollpos = currentScrollPos;
    }

    document.addEventListener('DOMContentLoaded', function() {
      var searchIcon = document.getElementById('searchIcon');
      var searchOverlay = document.getElementById('searchOverlay');

      searchIcon.addEventListener('click', function() {
        searchOverlay.classList.toggle('active');
        document.body.classList.toggle('overlay-active');
      });
    });

    function closeSearchOverlay() {
      var searchOverlay = document.getElementById('searchOverlay');
      searchOverlay.classList.remove('active');
      document.body.classList.remove('overlay-active');
    }