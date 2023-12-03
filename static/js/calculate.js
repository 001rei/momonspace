function BMI(height, weight) {
            let bmi = weight / (height / 100) ** 2;
            return bmi;
        }

        let submit = document.querySelector('#submit');
        let output = document.querySelector('#result');
        let output1 = document.querySelector('#tips-1');
        let output2 = document.querySelector('#tips-2');
        let output3 = document.querySelector('#tips-3');
        let output4 = document.querySelector('#span-status');
        let enable = document.querySelector('#result-info');
     

        submit.addEventListener('click', function (event) {
            event.preventDefault();
            let height = parseFloat(document.querySelector('#height').value);
            let weight = parseFloat(document.querySelector('#weight').value);

            if (height === '' || isNaN(height) || weight === '' || isNaN(weight)) {
                alert('Please enter valid height and weight values.');
                return;
            }

            let result = BMI(height, weight);

            enable.style.display = 'block';
            setTimeout(() => {
                enable.style.opacity = '1';
            }, 6);

            if (result < 18.5) {
                output.innerHTML = 'Your current status is Underweight.';
                output1.innerHTML = 'Consult a Healthcare Professional';
                output2.innerHTML = 'Regular Meals';
                output3.innerHTML = 'Strength Training';


            } else if (result >= 18.5 && result <= 24.9) {
                output.innerHTML = 'Your current status is Normal.';
                output1.innerHTML = 'Maintain a Balanced Diet';
                output2.innerHTML = 'Regular Exercise';
                output3.innerHTML = 'Maintaining a Healthy Lifestyle';
            } else if (result >= 25 && result <= 29.9) {
                output.innerHTML = 'Your current status is Overweight.';
                output1.innerHTML = 'Healthy Eating Habits';
                output2.innerHTML = 'Regular Exercise';
                output3.innerHTML = 'Seek Support';
            } else {
                output.innerHTML = 'Your current status is Obesity.';
                output1.innerHTML = 'Consult a Healthcare Professional';
                output2.innerHTML = 'Behavioral Changes';
                output3.innerHTML = 'Regular Physical Activity';
            }
        });