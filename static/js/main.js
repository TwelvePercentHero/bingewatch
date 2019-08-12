$(document).ready(function () {

function flashed_messages() {
	let messages = parseInt($("#messages p").length);
	if (messages) {
		$("#alerts").slideDown(1500);
		setTimeout(() => {
			$("#alerts").slideUp(1500);
		}, 7000);
	}
};

$(document).ready(function(){
    $('#show-media').click(function() {        
        $('#media-search').removeClass("d-none").addClass("d-block");
        $('#show-media').removeClass("btn-deselected").addClass("btn-selected");
        $('#recipe-search').removeClass("d-block").addClass("d-none");
        $('#show-recipe').removeClass("btn-selected").addClass("btn-deselected");
    });
    $('#show-recipe').click(function() {
        $('#recipe-search').removeClass("d-none").addClass("d-block");
        $('#show-recipe').removeClass("btn-deselected").addClass("btn-selected");
        $('#media-search').removeClass("d-block").addClass("d-none");
        $('#show-media').removeClass("btn-selected").addClass("btn-deselected");
    });
});

$(".custom-file-input").on("change", function() {
    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});

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

});