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

$('#add-actor').click(function() {
    var newActor = $(`<div class='form-group' id='actor-div'>
    <input id='starring' name='starring' class='form-control' type='text' placeholder='Actor'>
    <a class='btn btn-primary' id='remove-actor'>Remove Actor</a>
    </div>` );
    $('#actor-list').append(newActor);
});

$(document).on('click', '#remove-actor', function() {
    $(this).parent().remove();
});

$('#add-creator').click(function() {
    var newCreator = $(`<div class='form-group' id='creator-div'>
    <input id='creators' name='creators' class='form-control' type='text' placeholder='Creator'>
    <a class='btn btn-primary' id='remove-creator'>Remove Creator</a>
    </div>` );
    $('#creator-list').append(newCreator);
});

$(document).on('click', '#remove-creator', function() {
    $(this).parent().remove();
});

$('input[type="file"]').change(function(e) {
    var fileName = e.target.files[0].name;
    $("#file").val(fileName);
    // read the image file as a data URL.
    reader.readAsDataURL(this.files[0]);
});

});