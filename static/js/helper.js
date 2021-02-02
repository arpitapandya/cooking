function addSentinel() {
    $(createSentineDivHTML()).insertAFter('#recipe-container');
    intersectionObserver.observe(document.querySelector('#sentinel'));
}

function displayResults(resp) {
    $('main').children().slideUp('slow', function() {
        $(this).remove();
    });

    setTimeout(() => {
        const $p1 = makeP1();
        const $hr = makeHr();
        const $total = makeTotalResults(resp.data.data);
        const $row = makeRow();
        $('main').prepend($p1).hide().slideDown('slow');
        $('p1').after($row).after($hr).after($total);
        resp.data.data.results.forEach((recipe) => {
            showRecipeCard(recipe, resp.data.data, resp.data.favorites);
        });
        $('form').on('click', '.fa-heart-o', handleFavorite);
    }, 800);
}

function showRecipeCard(recipe, data, favorites) {
    const recipeHTML = generateRecipeCardHTML(recipe, data, favorites);
    $('#recipe-container').append(recipeHTML);
    $('form').on('submit', (e) => {
        e.preventDefault();
    });
}

function generateRecipeCardHTML(recipe, data, favorites) {
    let favoriteButton;

    if (favorites.includes(recipe.id)) {
        favoriteButton = `<button id="${recipe.id}" data-id="${recipe.id}" class= 'btn btn-lg'><sapn><i class="fas fa-heart-o"></i></span></button>`;
    } else {
        favoriteButton = `<button id="${recipe.id}" data-id="${recipe.id}" class='btn btn-lg'><span><i class="fas fa-heart-o"></i></span></button>`;
    }

    return `<div class="card border mb-4 mx-auto p-2 rounded text-center">
    <a href="/recipes/${recipe.id}" class="card-link">
    <img src="${data.baseUri}${recipe.image}" class="card-img-top img-fluid" alt="Image of ${recipe.title}">
    <div class="card-body py-2">
    <h4 class="card-title d-inline">${recipe.title}</h4>
    <form id="favorite-form" class="favorite-form d-inline"> ${favoriteButton}
    </form>
    <p class="lead mb-0">Ready In: ${recipe.readyInMinutes} minutes</p>
    <p class="lead">Servings: ${recipe.servings}</p>
    <a class="small text-muted" href="${recipe.sourceUrl}">View Original</a>
    <br>
    </a>
    </div>
</div>`;
}
function makeTotalResults(data) {
	let $newTotal = $('<p>').text(`${data.totalResults} total results`).addClass('small text-center text-dark');
	return $newTotal;
}

function makeP1(text = 'Recipe') {
	let $newP1 = $('<h1>').text(text).addClass('display-2 text-center');
	return $newP1;
}

function makeHr() {
	let $newHr = $('<hr>');
	return $newHr;
}

function makeRow() {
	let $newRow = $('<div>').addClass('row p-0 m-0').attr('id', 'recipe-container');
    return $newRow;
}

function showUpdateForm() {
	const id = $(this).data('id');
	const modalHTML = generateUpdateModalHTML(id);
	addShowModal(modalHTML);
	$('#submit-update').on('click', handleUserUpdate);
}

function toggleFavorite(response) {
	if (response.status !== 200) {
		displayErrorAlert(response);
	} else {
		$(this).toggleClass('fas fa-heart');
		$(this).toggleClass('far fa-heart');
		displaySuccessAlert(response);
	}
}

function updateProfile(response) {
	$('#user-email').text(`${response.data.user.email}`);
	$('#user-image').attr('src', `${response.data.user.img_url}`);
	$('.avatar').attr('src', `${response.data.user.img_url}`);
}

function displaySuccessAlert(response) {
	$('.feedback').remove();
	const alertHTML = generateAlertHTML(response.data.message, 'success');
	$('main').prepend(alertHTML).alert();
	$('.feedback').hide().fadeIn('slow').delay(1000).fadeOut('slow');
}

function displaySuccessModal(response) {
	const modalHTML = generateRecipeModalHTML(response.data);
	if ($('#myModal')) {
		$('#myModal').remove();
	}
	addShowModal(modalHTML);
}

function displayAndRemove(data) {
	const $toRemove = $(this).closest('li');
	$toRemove.html(`${data.message}`);
	$toRemove.delay(500).fadeOut(2000);
}

function confirmRemove() {
	$(this).removeClass('far fa-trash-alt');
	$(this).addClass('fas fa-minus-circle');
	$(this)
		.attr('id', 'confirm-remove')
		.attr('data-toggle', 'tooltip')
		.attr('data-placement', 'right')
		.attr('title', 'Remove from list')
		.tooltip()
		.on('click', removeIngredientFromGroceryList)
		.tooltip('hide');
}

function showAddIngredient() {
	if ($('.add-ingredient').length !== 0) {
		return;
	}

	const newAddIngredient = makeAddIngredient();
	$(this).closest('li').before(newAddIngredient);
	$('.add-ingredient').on('submit', handleAddIngredient);
}

function makeAddIngredient() {
	return `<li class='list-group-item my-0 text-center'>
	<form class="add-ingredient form-inline d-inline">
	<input class="form-control" id="user-add-ingredient" type="text" placeholder="Add new ingredient..." required>
	<button type="submit" id="show-add-ingredient" class='btn btn-sm btn-outline-primary'>
	Add
	</button>
	</form>
	</li>
	`;
}

function generateIngredientHTML(ingredient) {
	return `
	${ingredient}
	<span class="btn" data-ingredient="${ingredient}">
	<i class="far fa-trash-alt remove"></i>
	</span>`;
}

function generateUpdateModalHTML(id) {
	return `<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModal" aria-hidden="true">
	<div class="modal-dialog" role="document">
	  <div class="modal-content">
		<div class="modal-header">
		  <h5 class="modal-title text-center">Update Profile</h5>
		  <button type="button" class="close" data-dismiss="modal" aria-label="Close">
			<span aria-hidden="true">&times;</span>
		  </button>
		</div>
		<div class="modal-body">
		  <form id="user-update">
			<div class="form-group">
			  <label for="email" class="col-form-label">Email:</label>
			  <input type="text" class="form-control" id="email">
			</div>
			<div class="form-group">
			  <label for="img-url" class="col-form-label">Image URL:</label>
			  <input type="url" class="form-control" id="img-url">
			</div>
		  </form>
		</div>
		<div class="modal-footer">
		  <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
		  <button data-id="${id}" data-dismiss="modal" id="submit-update" type="button" class="btn btn-primary">Update</button>
		</div>
	  </div>
	</div>
  </div>`;
}
function createSentinelDivHTML() {
	return `<div class="d-flex justify-content-center mb-3" id="sentinel">
      <div class="spinner-border" role="status"></div>
    </div>`;
}