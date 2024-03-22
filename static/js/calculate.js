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


const bmiColors = {
  "Underweight": "#f9d59c", 
  "Normal": "#9ccc65", 
  "Overweight": "#fcb045", 
  "Obesity": "#ff5c5c" 
};

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

  let status;
  if (result < 18.5) {
    status = "Underweight";
  } else if (result >= 18.5 && result <= 24.9) {
    status = "Normal";
  } else if (result >= 25 && result <= 29.9) {
    status = "Overweight";
  } else {
    status = "Obesity";
  }

  output.innerHTML = `Your current status is ${status}.`;
  output1.innerHTML = bmiTips[status][0];
  output2.innerHTML = bmiTips[status][1];
  output3.innerHTML = bmiTips[status][2];

  enable.style.backgroundColor = bmiColors[status];
});

const bmiTips = {
  "Underweight": [
    'Consult a Healthcare Professional',
    'Regular Meals',
    'Strength Training'
  ],
  "Normal": [
    'Maintain a Balanced Diet',
    'Regular Exercise',
    'Maintaining a Healthy Lifestyle'
  ],
  "Overweight": [
    'Healthy Eating Habits',
    'Regular Exercise',
    'Seek Support'
  ],
  "Obesity": [
    'Consult a Healthcare Professional',
    'Behavioral Changes',
    'Regular Physical Activity'
  ]
};