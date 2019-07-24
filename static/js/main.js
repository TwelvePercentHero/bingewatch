$(document).ready(function () {

function flashed_messages() {
	let messages = parseInt($("#messages p").length);
	if (messages) {
		$("#alerts").slideDown(1500);
		setTimeout(() => {
			$("#alerts").slideUp(1500);
		}, 7000);
	}
}

$('#add-ingredient').click(function() {
    var newIngredient = $(`<div class='form-group' id='ingredients-div'>
    <input id='ingredients' name='ingredients' class='form-control' type='text' placeholder='Ingredient'>
    <a class='btn btn-primary' id='remove-ingredient'>Remove Ingredient</a>
    </div>` );
    $('#ingredients-list').append(newIngredient);
});

$(document).on('click', '#remove-ingredient', function() {
    $(this).parent().remove();
});

$('#add-step').click(function() {
    var newStep = $(`<div class='form-group' id='method-div'>
    <input id='method' name='method' class='form-control' type='text' placeholder='Step'>
    <a class='btn btn-primary' id='remove-step'>Remove Step</a>
    </div>` );
    $('#method-steps').append(newStep);
});

$(document).on('click', '#remove-step', function() {
    $(this).parent().remove();
});

});