let i = 0;
        let images = [];

        images[0] = "./static/images/4.jpg";
        images[1] = "./static/images/5.jpg";
        images[2] = "./static/images/6.jpg";
        images[3] = "./static/images/7.jpg";
        images[4] = "./static/images/8.jpg";
        images[5] = "./static/images/9.jpg";

        let time = 1500;
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