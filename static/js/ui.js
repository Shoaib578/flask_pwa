const recipes = document.querySelector('.recipes');

document.addEventListener('DOMContentLoaded', function() {
	// nav menu
	const menus = document.querySelectorAll('.side-menu');
	M.Sidenav.init(menus, { edge: 'right' });
	// add recipe form
	const forms = document.querySelectorAll('.side-form');
	M.Sidenav.init(forms, { edge: 'left' });
});


//<div class="recipe-title">${data.title}</div>
//<div class="recipe-ingredients">${data.TimeOut}</div>
//<div class="recipe-ingredients">${data.Location}---line20</div>


// CONFIRMATION BUTTON
function confirmButton() {

  
    document.getElementById("yes").disabled = false;
{
  document.getElementById("submitbutton").disabled = false
}

    ;
}

// added on 23/04/2021
function disableSubmit(){
  document.getElementById("submitbutton").disabled = true;
}

/*function submit() {
    document.getElementById("submitbutton").disabled = false;
    document.getElementById("yes").disabled = true;
}*/

// DISABLE KEYPRESS
function disable()
{
 document.onkeydown = function (e) 
 {
  return false;
 }
}
function enable()
{
 document.onkeydown = function (e) 
 {
  return true;
 }
}