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
    var newIngredient = $(`<div class='input-group' id='ingredients-div'>
    <input id='ingredients' name='ingredients' class='form-control' type='text' placeholder='Ingredient'>
    <div class="input-group-append">
        <a class="btn btn-add" id="remove-ingredient"><i class="fas fa-minus"></i></a>
    </div>
    </div>` );
    $('#ingredients-list').append(newIngredient);
});

$(document).on('click', '#remove-ingredient', function() {
    $(this).parent().parent().remove();
});

$('#add-step').click(function() {
    var newStep = $(`<div class='input-group' id='method-div'>
    <input id='method' name='method' class='form-control' type='text' placeholder='Step'>
    <div class="input-group-append">
        <a class='btn btn-add' id='remove-step'><i class="fas fa-minus"></i></a>
    </div>
    </div>` );
    $('#method-steps').append(newStep);
});

$(document).on('click', '#remove-step', function() {
    $(this).parent().parent().remove();
});

$('#add-actor').click(function() {
    var newActor = $(`<div class='input-group' id='actor-div'>
    <input id='starring' name='starring' class='form-control' type='text' placeholder='Actor'>
    <div class="input-group-append">
        <a class='btn btn-add' id='remove-actor'><i class="fas fa-minus"></i></a>
    </div>
    </div>` );
    $('#actor-list').append(newActor);
});

$(document).on('click', '#remove-actor', function() {
    $(this).parent().parent().remove();
});

$('#add-creator').click(function() {
    var newCreator = $(`<div class='input-group' id='creator-div'>
    <input id='creators' name='creators' class='form-control' type='text' placeholder='Creator'>
    <div class="input-group-append">
        <a class='btn btn-add' id='remove-creator'><i class="fas fa-minus"></i></a>
    </div>
    </div>` );
    $('#creator-list').append(newCreator);
});

$(document).on('click', '#remove-creator', function() {
    $(this).parent().parent().remove();
});

});