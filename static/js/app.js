let diets = ['vegetarian', 'vegan', 'lacto vegetarian']
let cuisines = ['indian', 'chinese', 'spanish', 'african', 'southern', 'mexican', 'korean', 'japanese', 'american', 'german', 'greek', 'thai', 'italian']

const sentinel = document.querySelector('#sentinel');


let offset;
const intersectionObserver = new IntersectionObserver((entries) => {
	if (entries[0].intersectionRatio <= 0) {
		return;
	}
	loadItems();
});



// Event-Listeners
$('.favorite-form').on('click', '.fa-heart', handleFavorite);
$('#search-form').on('submit', handleSearch);
// $('.remove').on('click', confirmRemove);
// $('#update').on('click', showUpdateForm);
// $('#show-add-ingredient').on('click', showAddIngredient);
if (sentinel !== null) intersectionObserver.observe(sentinel);


$(document).ready(function() {
    // message falsh fad in fad out
    $('#flash').hide().delay(300).fadeIn(500).delay(3000).fadeOut(800);

    // Reset offset to 0
    offset = 0;
    if ($('#recipe-container').length) offset = 12;
});

	//handleSearch
async function handleSearch(evt) {
	evt.preventDefault();
	const id = $(this).data('id');
	const query = $('#search-value').val();
	const diet = $('#diet').val();
	const cuisine = $('#cuisine').val();
	offset = 0;

	const response = await axios.get('/search', { params: { id, query, diet, cuisine, offset } });
	if (response.status !== 200) {
		console.log('There was an error - please refresh and try again');
		console.log('response: ', response);
	} else {
		displayResults(response);
	}
	setTimeout(() => {
		if (!$('#sentinel').length) addSentinel();
		offset += 12;
	}, 800);
}

async function handleFavorite(evt) {
    evt.preventDefault();

    const id = $(this).closest('button').data('id');

    if ($(this).hasClass('fas')) {
        let resp = await axios.delete(`/favorites/${id}`);
        toggleFavorite.call(this, resp);
    } else {
        let resp = await axios.post(`/favorites/${id}`, (data = { id }));
        toggleFavorite.call(this, resp);
    }
}

async function loadItems() {
	const id = $(this).data('id');
	const query = $('#search-value').val();
	const diet = $('#diet').val();
	const cuisine = $('#cuisine').val();

	const response = await axios.get('/load', { params: { id, query, diet, cuisine, offset } });

	if (response.data.data.results.length === 0) {
		$('#sentinel').html('recipes not found!');
	} else {
		response.data.data.results.forEach((recipe) => {
			showRecipeCard(recipe, response.data.data, response.data.favorites);
		});

		$('.favorite-form').on('click', '.fa-heart', handleFavorite);
		offset += 12;
	}
}

async function handleAddIngredient(evt) {
	evt.preventDefault();
	const id = $(this).closest('ul').data('id');
	const ingredient = $('#user-add-ingredient').val();

	const response = await axios.post(`/groceries/${id}`, (data = { ingredient }));

	if (response.status === 201) {
		const newItem = generateIngredientHTML(response.data.ingredient);
		$(this).closest('li').html(newItem);
	} else {
		const data = { message: `Couldn't add ${ingredient}. Refresh and try again` };
		displayAndRemove(data);
	}
}

async function handleUserUpdate(evt) {
	evt.preventDefault();

	const id = $(this).data('id');
	const email = $('#email').val();
	const imgUrl = $('#img-url').val();
	const response = await axios.patch(`/users/${id}`, (data = { id, email, imgUrl }));

	if (response.data.errors) {
		displayErrorAlert(response);
	} else {
		updateProfile(response);
		displaySuccessAlert(response);
	}
}
