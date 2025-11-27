document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('year').textContent = new Date().getFullYear();

  const tabs = document.querySelectorAll('.search-tabs .tab');
  const returnCol = document.getElementById('returnCol');
  const multiContainer = document.getElementById('multiTripsContainer');
  const multiList = document.getElementById('multiTripsList');
  const addLegBtn = document.getElementById('addLeg');
  const clearLegsBtn = document.getElementById('clearLegs');
  const travelerInput = document.getElementById("travelerInput");


  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const mode = tab.dataset.mode;
      handleModeChange(mode);
    });
  });

  function handleModeChange(mode){
    if(mode === 'round'){
      returnCol.style.display = '';
      multiContainer.style.display = 'none';
    } else if(mode === 'oneway'){
      returnCol.style.display = 'none';
      multiContainer.style.display = 'none';
    } else if(mode === 'multi'){
      returnCol.style.display = 'none';
      multiContainer.style.display = '';
      if(multiList.children.length === 0) addLeg(); 
    }
  }

  travelerBtn.addEventListener('click', () => {
    const menu = document.createElement('div');
    menu.className = 'p-3 rounded-3 bg-white shadow-lg';
    menu.style.position = 'absolute';
    menu.style.right = '20px';
    menu.style.top = '70px';
    menu.style.minWidth = '180px';
    menu.innerHTML = `
      <div class="d-flex align-items-center justify-content-between mb-2">
        <div class="small text-muted">Adults</div>
        <div class="d-flex align-items-center gap-2">
          <button class="btn btn-sm btn-outline-secondary" id="travMinus">−</button>
          <div id="travCount" class="px-2 fw-semibold">${travelers}</div>
          <button class="btn btn-sm btn-outline-secondary" id="travPlus">+</button>
        </div>
      </div>
      <div class="d-flex justify-content-end">
        <button id="travClose" class="btn btn-sm btn-primary">Done</button>
      </div>
    `;
    document.body.appendChild(menu);

    menu.querySelector('#travPlus').addEventListener('click', () => {
      travelers = Math.min(9, travelers + 1);
      menu.querySelector('#travCount').textContent = travelers;
    });
    menu.querySelector('#travMinus').addEventListener('click', () => {
      travelers = Math.max(1, travelers - 1);
      menu.querySelector('#travCount').textContent = travelers;
    });
    menu.querySelector('#travClose').addEventListener('click', () => {
      travelerLabel.textContent = `${travelers} Adult${travelers>1 ? 's' : ''}`;
      menu.remove();
    });

    const outsideClick = (e) => {
      if(!menu.contains(e.target) && e.target !== travelerBtn) {
        menu.remove();
        document.removeEventListener('click', outsideClick);
      }
    };
    setTimeout(()=> document.addEventListener('click', outsideClick), 10);
  });

  function createLeg(index = 1){
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
    wrapper.querySelector('.remove-leg').addEventListener('click', () => {
      wrapper.remove();
    });
    return wrapper;
  }

  function addLeg(){
    const n = multiList.children.length + 1;
    const leg = createLeg(n);
    multiList.appendChild(leg);
  }

  addLegBtn.addEventListener('click', addLeg);
  clearLegsBtn.addEventListener('click', () => {
    multiList.innerHTML = '';
    addLeg();
  });

  function init(){
    handleModeChange('round');
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('departDate').setAttribute('min', today);
    document.getElementById('returnDate').setAttribute('min', today);

    document.getElementById('flightForm').addEventListener('submit', (e) => {
      e.preventDefault();
      const mode = document.querySelector('.search-tabs .tab.active').dataset.mode;
      const from = document.getElementById('fromInput').value;
      const to = document.getElementById('toInput').value;
      const depart = document.getElementById('departDate').value;
      const ret = document.getElementById('returnDate').value;
      alert(`Searching (${mode})\nFrom: ${from}\nTo: ${to}\nDepart: ${depart}\nReturn: ${ret}\nPassengers: ${travelers}`);
    });
  }

  init();
});
