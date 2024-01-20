//[ico-filter Javascript]

//Project:	Crypto Admin - Responsive Admin Template

$(function () {
    'use strict';

    // radios filter

    // In this example, we must bind a 'change' event handler to
    // our radios, then interact with the mixer via
    // its .filter() API methods.

    // check if container exists
    if (!$('.ico-filter').length) {
        return false;
    }

    var containerEl = document.querySelector('.ico-filter');
    var radiosFilter = document.querySelector('.radios-filter');

    var mixer = mixitup(containerEl);

    radiosFilter.addEventListener('change', function () {
        var checked = radiosFilter.querySelector(':checked');

        var selector = checked ? checked.value : 'all';

        mixer.filter(selector);
    });

}); // End of use strict
