function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const stripePk = document.querySelector('[data-stripe-pk]').dataset.stripePk
const stripe = Stripe(stripePk);

initialize();

// Fetch Checkout Session and retrieve the client secret
async function initialize() {
    const fetchClientSecret = async () => {
        const orderId = document.querySelector('[data-order-id]').dataset.orderId
        const response = await fetch(`/create-checkout-session/${orderId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
        });
        const {clientSecret} = await response.json();
        return clientSecret;
    };

    // Initialize Checkout
    const checkout = await stripe.initEmbeddedCheckout({
        fetchClientSecret,
    });

    // Mount Checkout
    checkout.mount('#checkout');
}