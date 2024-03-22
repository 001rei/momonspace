function calculateCalories(gender,weight,height,age,activity) {

  let bmr;
  
  if (gender === 'male') {
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
  } else {
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
  }

  // Total Energy Expenditure (TEE)
  const tee = bmr * activity;

  return tee.toFixed(2); 
}

let submit = document.querySelector('#submit');
let output = document.querySelector('#result');
let enable = document.querySelector('#result-info');

submit.addEventListener('click', function(event){
    event.preventDefault()

    let gender = document.querySelector('#gender').value;
    let age = parseFloat(document.querySelector('#age').value);
    let height = parseFloat(document.querySelector('#height').value);
    let weight = parseFloat(document.querySelector('#weight').value);
    let activity = parseFloat(document.querySelector('#activity').value);

    let result = calculateCalories(gender,weight,height,age,activity);

    enable.style.display = 'block';
            setTimeout(() => {
                enable.style.opacity = '1';
            }, 6);

    output.innerHTML = `Your daily calorie needs: ${result} kcal`;
});
