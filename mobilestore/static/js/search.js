$(document).ready(function() {
	$(".card-content").on('click', function() {
		var id = $(this).find(">:first-child").val();
		$(location).prop('href', '/store/detail?id=' + id);
	});
	
	$("#cart").on('click', function(){
		$(location).prop('href', '/store/cart/show-cart');
	});
	
	$(".popular-product").on('click', function() {
		var id = $(this).find(">:first-child").val();
		$(location).prop('href', '/store/detail?id=' + id);
	});
})