let flights = [];

async function fetchFlights() {
    try {
        const res = await fetch('/selected-flight', {
            method: 'POST', // your endpoint expects POST
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                flight_name: "", // you can leave empty to fetch all flights if backend supports it
                user_id: 1      // optional if needed
            })
        });
        
        const data = await res.json();

        if (data.success) {
            // The backend returns a single flight, so wrap in array for renderFlights
            flights = [data.flight];
            renderFlights();
        } else {
            console.error(data.message);
        }
    } catch (err) {
        console.error("Error fetching flight:", err);
    }
}

// DOM elements
const flightListings = document.getElementById('flightListings');
const loadingSpinner = document.getElementById('loadingSpinner');
const selectedFlightTitle = document.getElementById('selectedFlightTitle');
const selectedFlightName = document.getElementById('selectedFlightName');
const GoToBookingBtn = document.getElementById('GoToBooking');
const flightModal = new bootstrap.Modal(document.getElementById('flightModal'));

// Current state
let displayedFlights = 3;
let selectedFlight = null;

// Function to format price
function formatPrice(price) {
    return `$${price}`;
}

// Function to get airline abbreviation
function getAirlineAbbreviation(airline) {
    return airline.split(' ').map(word => word[0]).join('').toUpperCase();
}

// Function to create flight card HTML
function createFlightCard(flight) {
    const airlineAbbr = getAirlineAbbreviation(flight.airline);
    
    return `
        <div class="flight-card" data-flight-id="${flight.id}">
            <div class="flight-header">
                <div class="d-flex align-items-center">
                    <div class="airline-logo ${flight.airlineClass}">
                        ${airlineAbbr}
                    </div>
                    <div>
                        <h5 class="mb-0">${flight.airline}</h5>
                        <p class="text-muted mb-0">Flight ${flight.flightNumber}</p>
                    </div>
                </div>
                <div class="d-none d-md-block">
                    <span class="badge bg-light text-dark">Non-stop</span>
                </div>
            </div>
            <div class="flight-info">
                <div class="flight-times">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div class="text-center">
                            <div class="time-display">${flight.departureTime}</div>
                            <div class="airport-code">${flight.departureAirport}</div>
                        </div>
                        <div class="text-center mx-3">
                            <div class="flight-duration">
                                <span>${flight.duration}</span>
                            </div>
                        </div>
                        <div class="text-center">
                            <div class="time-display">${flight.arrivalTime}</div>
                            <div class="airport-code">${flight.arrivalAirport}</div>
                        </div>
                    </div>
                </div>
                <div class="flight-price">
                    <div class="price">${formatPrice(flight.price)}</div>
                    <div class="seats-left">${flight.seatsLeft} seats left</div>
                    <button class="btn btn-primary mt-2 select-flight-btn" data-flight-id="${flight.id}">
                        Select Flight
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Function to render flights
function renderFlights() {
    flightListings.innerHTML = '';
    
    // Show only the number of flights based on displayedFlights
    const flightsToShow = flights.slice(0, displayedFlights);
    
    flightsToShow.forEach(flight => {
        flightListings.innerHTML += createFlightCard(flight);
    });
    
    // Add event listeners to the select buttons
    document.querySelectorAll('.select-flight-btn').forEach(button => {
        button.addEventListener('click', function() {
            const flightId = parseInt(this.getAttribute('data-flight-id'));
            selectFlight(flightId);
        });
    });
}

// Function to handle flight selection
function selectFlight(flightId) {
    selectedFlight = flights.find(flight => flight.id === flightId);
    
    if (selectedFlight) {
        selectedFlightTitle.textContent = `${selectedFlight.airline} - Flight ${selectedFlight.flightNumber}`;
        selectedFlightName.textContent = `${selectedFlight.airline} ${selectedFlight.flightNumber}`;
        flightModal.show();
    }
}

// Function to load more flights
function loadMoreFlights() {
    // Show loading spinner
    loadingSpinner.classList.remove('d-none');
    
    // Simulate API call delay
    setTimeout(() => {
        // Increase displayed flights count
        displayedFlights = Math.min(displayedFlights + 3, flights.length);
        
        // Re-render flights
        renderFlights();
        
        // Hide loading spinner
        loadingSpinner.classList.add('d-none');
        
        // Scroll to the newly loaded flights
        if (displayedFlights > 3) {
            window.scrollTo({
                top: document.body.scrollHeight - 500,
                behavior: 'smooth'
            });
        }
    }, 1000);
}

// Function to handle filter button click
function handleFilterClick() {
    alert('Filter functionality would open here.');
}

// Function to handle change search button click
function handleChangeSearchClick() {
    alert('Change search functionality.');
}

// Function to handle proceed to booking
function handleGoToBooking() {
    if (selectedFlight) {
        flightModal.hide();
        alert(`Proceeding to booking for ${selectedFlight.airline} ${selectedFlight.flightNumber}`);
    }
}


GoToBookingBtn.addEventListener('click', handleGoToBooking);

// Infinite scroll simulation
window.addEventListener('scroll', function() {
    // Check if we've scrolled to the bottom of the page
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        // Only load more if we haven't shown all flights yet
        if (displayedFlights < flights.length) {
            loadMoreFlights();
        }
    }
});

// Initialize the page
// document.addEventListener('DOMContentLoaded', function() {
//     renderFlights();
// });
document.addEventListener('DOMContentLoaded', function() {
    fetchFlights();
});
