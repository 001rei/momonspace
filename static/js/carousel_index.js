let i = 0;
        let images = [];

        images[0] = "./static/images/1.jpg";
        images[1] = "./static/images/2.jpg";
        images[2] = "./static/images/3.jpg";

        let time = 2000;
        function carousel() {
            document.carousel.src = images[i];

            if (i < images.length - 1) {
                i++
            } else {
                i = 0;
            }

            setTimeout("carousel()", time);
        }

        window.onload = carousel;