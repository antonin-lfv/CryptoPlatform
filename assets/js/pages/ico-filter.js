//[ico-filter Javascript]

//Project:	Crypto Admin - Responsive Admin Template

$(function () {
    'use strict';

    // radios filter

    // In this example, we must bind a 'change' event handler to
    // our radios, then interact with the mixer via
    // its .filter() API methods.

    var containerEl = document.querySelector('.ico-filter');
    var radiosFilter = document.querySelector('.radios-filter');

    var mixer = mixitup(containerEl);

    radiosFilter.addEventListener('change', function () {
        var checked = radiosFilter.querySelector(':checked');
        console.log(checked);

        var selector = checked ? checked.value : 'all';
        console.log(selector);

        mixer.filter(selector).then(function (state) {
            console.log(state.totalShow);  // Nombre d'éléments affichés après le filtrage
        });
    });

}); // End of use strict
