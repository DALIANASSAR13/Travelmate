document.addEventListener('DOMContentLoaded', () => {
  // -----------------------------
  // Update footer year dynamically
  // -----------------------------
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // -----------------------------
  // DOM elements for flight search form
  // -----------------------------
  const tabs = document.querySelectorAll('.search-tabs .tab');
  const returnCol = document.getElementById('returnCol');
  const multiContainer = document.getElementById('multiTripsContainer');
  const multiList = document.getElementById('multiTripsList');
  const addLegBtn = document.getElementById('addLeg');
  const clearLegsBtn = document.getElementById('clearLegs');
  const travelerInput = document.getElementById('travelerInput');

  let travellersCount = 1;

  // -----------------------------
  // Handle travelers input
  // -----------------------------
  if (travelerInput) {
    travelerInput.name = 'travellers';
    travelerInput.value = travellersCount;

    travelerInput.addEventListener('change', () => {
      const val = parseInt(travelerInput.value || '1', 10);
      travellersCount = (!isNaN(val) && val > 0) ? val : 1;
      travelerInput.value = travellersCount;
    });
  }

  // -----------------------------
  // Handle trip mode changes (round, oneway, multi)
  // -----------------------------
  function handleModeChange(mode) {
    if (!returnCol || !multiContainer) return;

    if (mode === 'round') {
      returnCol.style.display = '';
      multiContainer.style.display = 'none';
    } else if (mode === 'oneway') {
      returnCol.style.display = 'none';
      multiContainer.style.display = 'none';
    } else if (mode === 'multi') {
      returnCol.style.display = 'none';
      multiContainer.style.display = '';
      if (multiList && multiList.children.length === 0) addLeg();
    }
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const mode = tab.dataset.mode;
      handleModeChange(mode);
    });
  });

  // -----------------------------
  // Functions to create and manage multi-leg trips
  // -----------------------------
  function createLeg() {
    const wrapper = document.createElement('div');
    wrapper.className = 'trip-leg d-flex gap-2 align-items-center mb-2';
    wrapper.innerHTML = `
      <div class="flex-grow-1">
        <div class="input-glass d-flex align-items-center gap-2 p-2">
          <span class="material-symbols-outlined">flight_takeoff</span>
          <input class="form-control no-border" placeholder="From (city or airport)" />
        </div>
      </div>
      <div class="flex-grow-1">
        <div class="input-glass d-flex align-items-center gap-2 p-2">
          <span class="material-symbols-outlined">flight_land</span>
          <input class="form-control no-border" placeholder="To (city or airport)" />
        </div>
      </div>
      <div style="width:170px">
        <div class="input-glass d-flex align-items-center gap-2 p-2">
          <span class="material-symbols-outlined">calendar_today</span>
          <input type="date" class="form-control no-border" />
        </div>
      </div>
      <div>
        <button class="btn btn-link text-danger remove-leg" title="Remove leg">✕</button>
      </div>
    `;
    // Remove leg button
    wrapper.querySelector('.remove-leg').addEventListener('click', () => wrapper.remove());
    return wrapper;
  }

  function addLeg() {
    if (!multiList) return;
    multiList.appendChild(createLeg());
  }

  if (addLegBtn) addLegBtn.addEventListener('click', addLeg);

  if (clearLegsBtn) {
    clearLegsBtn.addEventListener('click', () => {
      if (!multiList) return;
      multiList.innerHTML = '';
      addLeg();
    });
  }

  // -----------------------------
  // Initialize the form state
  // -----------------------------
  handleModeChange('round');

  // -----------------------------
  // Set minimum selectable date for depart and return
  // -----------------------------
  const today = new Date().toISOString().split('T')[0];
  const departDate = document.getElementById('departDate');
  const returnDate = document.getElementById('returnDate');
  if (departDate) departDate.min = today;
  if (returnDate) returnDate.min = today;

  const flightForm = document.getElementById('flightForm');
});
