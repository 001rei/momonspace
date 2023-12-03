$('.toggler').on('click', function () {
    let $this = $(this);
    let $content = $this.parent().next();
    $content.slideToggle();
});
