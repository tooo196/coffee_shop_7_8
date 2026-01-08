// Main JavaScript file for Coffee Shop

// Document ready function
$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Handle quantity changes in cart
    $('.quantity-input').on('change', function() {
        const productId = $(this).data('product-id');
        const quantity = $(this).val();
        updateCartItem(productId, quantity);
    });
    
    // Handle remove item from cart
    $('.remove-item').on('click', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            removeFromCart(productId);
        }
    });
    
    // Handle add to cart buttons
    $('.add-to-cart').on('click', function() {
        const productId = $(this).data('product-id');
        const quantity = $(this).siblings('.quantity-input').val() || 1;
        addToCart(productId, quantity);
    });
    
    // Handle search form submission
    $('#search-form').on('submit', function(e) {
        const query = $('#search-input').val().trim();
        if (!query) {
            e.preventDefault();
            $('#search-input').addClass('is-invalid');
        }
    });
    
    // Reset search input validation on focus
    $('#search-input').on('focus', function() {
        $(this).removeClass('is-invalid');
    });
    
    // Handle image preview on product detail page
    $('.product-thumbnail').on('click', function() {
        const imgSrc = $(this).attr('src');
        $('.product-main-image').attr('src', imgSrc);
        $('.product-thumbnail').removeClass('active');
        $(this).addClass('active');
    });
    
    // Initialize first thumbnail as active
    $('.product-thumbnail:first').addClass('active');
    
    // Handle review form submission
    $('#review-form').on('submit', function(e) {
        e.preventDefault();
        submitReview();
    });
});

// Function to add item to cart
function addToCart(productId, quantity = 1) {
    const csrfToken = getCookie('csrftoken');
    
    $.ajax({
        type: 'POST',
        url: '/orders/cart/add/' + productId + '/',
        data: {
            'quantity': quantity,
            'csrfmiddlewaretoken': csrfToken
        },
        dataType: 'json',
        beforeSend: function() {
            // Show loading state
            $(`#add-to-cart-${productId}`).prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...');
        },
        success: function(response) {
            // Update cart count in navbar
            $('.cart-count').text(response.total_items || '0');
            
            // Show success message
            showAlert('Item added to cart!', 'success');
            
            // Reset button state
            $(`#add-to-cart-${productId}`).prop('disabled', false).html('Add to Cart');
        },
        error: function(xhr, status, error) {
            // Show error message
            showAlert('Failed to add item to cart. Please try again.', 'danger');
            
            // Reset button state
            $(`#add-to-cart-${productId}`).prop('disabled', false).html('Add to Cart');
        }
    });
}

// Function to update cart item quantity
function updateCartItem(productId, quantity) {
    const csrfToken = getCookie('csrftoken');
    
    $.ajax({
        type: 'POST',
        url: '/orders/cart/update/' + productId + '/',
        data: {
            'quantity': quantity,
            'csrfmiddlewaretoken': csrfToken
        },
        dataType: 'json',
        success: function(response) {
            // Update cart totals
            updateCartTotals(response);
            
            // Show success message
            showAlert('Cart updated!', 'success');
        },
        error: function(xhr, status, error) {
            // Show error message
            showAlert('Failed to update cart. Please try again.', 'danger');
        }
    });
}

// Function to remove item from cart
function removeFromCart(productId) {
    const csrfToken = getCookie('csrftoken');
    
    $.ajax({
        type: 'POST',
        url: '/orders/cart/remove/' + productId + '/',
        data: {
            'csrfmiddlewaretoken': csrfToken
        },
        dataType: 'json',
        success: function(response) {
            // Remove item from DOM
            $(`#cart-item-${productId}`).fadeOut(300, function() {
                $(this).remove();
                updateCartTotals(response);
                
                // If cart is empty, show empty cart message
                if (response.total_items === 0) {
                    $('.cart-items').html('<div class="alert alert-info">Your cart is empty.</div>');
                }
            });
            
            // Update cart count in navbar
            $('.cart-count').text(response.total_items || '0');
            
            // Show success message
            showAlert('Item removed from cart', 'info');
        },
        error: function(xhr, status, error) {
            // Show error message
            showAlert('Failed to remove item. Please try again.', 'danger');
        }
    });
}

// Function to update cart totals
function updateCartTotals(data) {
    if (data.subtotal) {
        $('.cart-subtotal').text('$' + parseFloat(data.subtotal).toFixed(2));
    }
    if (data.total) {
        $('.cart-total').text('$' + parseFloat(data.total).toFixed(2));
    }
    if (data.total_items !== undefined) {
        $('.cart-count').text(data.total_items);
    }
}

// Function to submit a review
function submitReview() {
    const form = $('#review-form');
    const formData = form.serialize();
    
    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: formData,
        dataType: 'json',
        beforeSend: function() {
            // Show loading state
            $('#submit-review').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...');
        },
        success: function(response) {
            // Add new review to the list
            const reviewHtml = `
                <div class="card mb-3 fade-in">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h5 class="card-title">${response.user_name}</h5>
                            <div class="text-warning">
                                ${'<i class="fas fa-star"></i>'.repeat(response.rating)}${'<i class="far fa-star"></i>'.repeat(5 - response.rating)}
                            </div>
                        </div>
                        <p class="text-muted">${response.created_at}</p>
                        <p class="card-text">${response.comment}</p>
                    </div>
                </div>
            `;
            
            $('.reviews-list').prepend(reviewHtml);
            
            // Reset form
            form.trigger('reset');
            
            // Update rating display
            updateRatingStats(response.average_rating, response.total_reviews);
            
            // Show success message
            showAlert('Thank you for your review!', 'success');
        },
        error: function(xhr, status, error) {
            // Show error message
            showAlert('Failed to submit review. Please try again.', 'danger');
        },
        complete: function() {
            // Reset button state
            $('#submit-review').prop('disabled', false).html('Submit Review');
        }
    });
}

// Function to update rating stats
function updateRatingStats(averageRating, totalReviews) {
    if (averageRating !== undefined) {
        $('.average-rating').text(averageRating);
        $('.rating-stars').html(
            '<i class="fas fa-star"></i>'.repeat(Math.floor(averageRating)) +
            (averageRating % 1 >= 0.5 ? '<i class="fas fa-star-half-alt"></i>' : '') +
            '<i class="far fa-star"></i>'.repeat(5 - Math.ceil(averageRating))
        );
    }
    
    if (totalReviews !== undefined) {
        $('.total-reviews').text(totalReviews);
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to show alert messages
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add alert to the alerts container or create one if it doesn't exist
    let $alertsContainer = $('.alerts-container');
    if ($alertsContainer.length === 0) {
        $('main').prepend('<div class="container alerts-container"></div>');
        $alertsContainer = $('.alerts-container');
    }
    
    // Add alert and auto-remove after 5 seconds
    const $alert = $(alertHtml).appendTo($alertsContainer).hide().fadeIn(300);
    
    // Remove alert when close button is clicked
    $alert.on('closed.bs.alert', function() {
        $(this).fadeOut(300, function() {
            $(this).remove();
        });
    });
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        $alert.alert('close');
    }, 5000);
}
