    function changeLabelColor(labelId) {
        var labels = document.querySelectorAll('label');
        for (var i = 0; i < labels.length; i++) {
            labels[i].style.backgroundColor = '';
        }
        var label = document.getElementById(labelId);
        label.style.backgroundColor = 'black';
    }