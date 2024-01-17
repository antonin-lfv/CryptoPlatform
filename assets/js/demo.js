//[Preview Menu Javascript]

//Project:	Specie Admin Admin - Responsive Admin Template
//Primary use:   This file is for demo purposes only.

$(function () {
  'use strict'

  /**
   * Get access to plugins
   */

  $('[data-toggle="control-sidebar"]').controlSidebar()
  $('[data-toggle="push-menu"]').pushMenu()

  var $pushMenu       = $('[data-toggle="push-menu"]').data('lte.pushmenu')
  var $controlSidebar = $('[data-toggle="control-sidebar"]').data('lte.controlsidebar')
  var $layout         = $('body').data('lte.layout')

  /**
   * Toggles layout classes
   *
   * @param String cls the layout class to toggle
   * @returns void
   */
  function changeLayout(cls) {
    $('body').toggleClass(cls)
    if ($('body').hasClass('fixed') && cls == 'fixed') {
      $pushMenu.expandOnHover()
      $layout.activate()
    }
    $controlSidebar.fix()
  }

  /**
   * Retrieve default settings and apply them to the template
   *
   * @returns void
   */
  function setup() {
    // Add the layout manager
    $('[data-layout]').on('click', function () {
      changeLayout($(this).data('layout'))
    })

    $('[data-controlsidebar]').on('click', function () {
      changeLayout($(this).data('controlsidebar'))
      var slide = !$controlSidebar.options.slide

      $controlSidebar.options.slide = slide
      if (!slide)
        $('.control-sidebar').removeClass('control-sidebar-open')
    })


    $('[data-enable="expandOnHover"]').on('click', function () {
      $(this).attr('disabled', true)
      $pushMenu.expandOnHover()
      if (!$('body').hasClass('sidebar-collapse'))
        $('[data-layout="sidebar-collapse"]').click()
    })

    $('[data-enable="rtl"]').on('click', function () {
      $(this).attr('disabled', true)
      $pushMenu.expandOnHover()
      if (!$('body').hasClass('rtl'))
        $('[data-layout="rtl"]').click()
    })

    $('[data-mainsidebarskin="toggle"]').on('click', function () {
      var $sidebar = $('body')
      if ($sidebar.hasClass('dark-skin')) {
        $sidebar.removeClass('dark-skin')
        $sidebar.addClass('light-skin')
      } else {
        $sidebar.removeClass('light-skin')
        $sidebar.addClass('dark-skin')
      }
    })
  }

  // Create the tab button
  var $tabButton = $('<li />', { 'class': 'nav-item' })
    .html('<a href=\'#control-sidebar-theme-demo-options-tab\' class=\'active\' data-bs-toggle=\'tab\' title=\'Setting\'>'
      + '<i class="mdi mdi-settings"></i>'
      + '</a>')

  // Add the tab button to the right sidebar tabs
  $('[href="#control-sidebar-home-tab"]')
    .parent()
    .before($tabButton)

  // Create the menu
  var $demoSettings = $('<div />')




  // Layout options
  $demoSettings.append(
    '<h4 class="control-sidebar-heading p-0">'
    + '</h4>'

    // Theme Skin Toggle
	+ '<div class="flexbox mb-10 pb-10 bb-1 light-on-off">'
	+ '<label for="toggle_left_sidebar_skin" class="control-sidebar-subheading">'
    + 'Dark or Light Skin'
    + '</label>'
	+ '<label class="switch">'
	+ '<input type="checkbox" data-mainsidebarskin="toggle" id="toggle_left_sidebar_skin">'
	+ '<span class="switch-on fs-30"><i class="mdi mdi-lightbulb-on"></i></span>'
	+ '<span class="switch-off fs-30"><i class="mdi mdi-lightbulb"></i></span>'
	+ '</label>'
	+ '</div>'
  )

  setup()

  $('[data-toggle="tooltip"]').tooltip()
});// End of use strict

