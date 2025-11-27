

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("year").textContent = new Date().getFullYear();

  
  let flights = [
    {
      id: 1,
      airline: "EgyptAir",
      code: "MS 912",
      from: "Cairo (CAI)",
      to: "Dubai (DXB)",
      departTime: "08:10",
      arriveTime: "12:35",
      duration: "3h 25m",
      stops: 0,
      price: 5200
    },
    {
      id: 2,
      airline: "Emirates",
      code: "EK 924",
      from: "Cairo (CAI)",
      to: "Dubai (DXB)",
      departTime: "14:45",
      arriveTime: "19:05",
      duration: "3h 20m",
      stops: 0,
      price: 6100
    },
    {
      id: 3,
      airline: "Saudia",
      code: "SV 302",
      from: "Cairo (CAI)",
      to: "Jeddah (JED)",
      departTime: "06:00",
      arriveTime: "09:10",
      duration: "3h 10m",
      stops: 1,
      price: 3800
    },
    {
      id: 4,
      airline: "FlyDubai",
      code: "FZ 182",
      from: "Cairo (CAI)",
      to: "Dubai (DXB)",
      departTime: "22:30",
      arriveTime: "02:45",
      duration: "4h 15m",
      stops: 0,
      price: 4700
    }
  ];

  
  const params = new URLSearchParams(window.location.search);
  const mode = params.get("mode") || "round";
  const from = params.get("from") || flights[0].from;
  const to = params.get("to") || flights[0].to;
  const depart = params.get("depart") || "";
  const ret = params.get("return") || "";
  const travelers = params.get("trav") || "1";

  
  const routeText = `${from} → ${to}`;
  document.getElementById("summaryRoute").textContent = routeText;
  document.getElementById("summaryRouteInline").textContent = routeText;

  let datesText = "";
  if (depart && ret && mode === "round") {
    datesText = `Round trip • Depart ${depart} · Return ${ret}`;
  } else if (depart) {
    datesText = `Depart ${depart}`;
  } else {
    datesText = "Flexible dates";
  }

  document.getElementById("summaryDates").textContent = datesText;
  document.getElementById("summaryDatesInline").textContent = datesText;

  const modeLabel =
    mode === "round" ? "Round trip" :
    mode === "oneway" ? "One-way" :
    "Multi-trip";

  document.getElementById("summaryMeta").textContent =
    `${modeLabel} • ${travelers} traveler(s)`;

  
  const filterPills = document.querySelectorAll(".filter-pill");
  let activeFilter = null;

  filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
      if (pill.classList.contains("active")) {
        pill.classList.remove("active");
        activeFilter = null;
      } else {
        filterPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        activeFilter = pill.dataset.filter;
      }
      renderFlights();
    });
  });

  const sortSelect = document.getElementById("sortSelect");
  sortSelect.addEventListener("change", renderFlights);

  function getFilteredAndSortedFlights() {
    let list = [...flights];

    if (activeFilter === "nonstop") {
      list = list.filter(f => f.stops === 0);
    } else if (activeFilter === "morning") {
      list = list.filter(f => {
        const hour = parseInt(f.departTime.split(":")[0], 10);
        return hour >= 5 && hour < 12;
      });
    }

    const sort = sortSelect.value;
    if (sort === "cheapest") {
      list.sort((a, b) => a.price - b.price);
    } else if (sort === "fastest") {
      list.sort((a, b) => {
        const toMinutes = d => {
          const [hStr, mStr] = d.replace("m", "").split("h");
          const h = parseInt(hStr.trim(), 10) || 0;
          const m = parseInt(mStr.trim(), 10) || 0;
          return h * 60 + m;
        };
        return toMinutes(a.duration) - toMinutes(b.duration);
      });
    }

    return list;
  }

  function renderFlights() {
    const container = document.getElementById("resultsList");
    container.innerHTML = "";

    const list = getFilteredAndSortedFlights();

    if (list.length === 0) {
      container.innerHTML = `
        <div class="alert alert-warning">
          No flights found for your filters. Try changing the filters.
        </div>
      `;
      return;
    }

    list.forEach(f => {
      const card = document.createElement("div");
      card.className = "flight-card";

      card.innerHTML = `
        <div class="d-flex align-items-start gap-3 flex-grow-1">
          <div class="airline-badge">
            <span class="airline-logo-text">
              ${f.airline.charAt(0)}
            </span>
          </div>
          <div>
            <div class="fw-semibold">${f.airline}</div>
            <div class="text-muted small">${f.code}</div>

            <div class="d-flex flex-wrap align-items-center gap-3 mt-2">
              <div>
                <div class="fw-bold fs-5">${f.departTime}</div>
                <div class="text-muted small">${f.from}</div>
              </div>
              <div class="text-center small text-muted">
                <span class="material-symbols-outlined d-block">
                  trending_flat
                </span>
                ${f.duration}
              </div>
              <div>
                <div class="fw-bold fs-5">${f.arriveTime}</div>
                <div class="text-muted small">${f.to}</div>
              </div>
            </div>

            <div class="mt-2 text-muted small">
              ${f.stops === 0 ? "Non-stop" : `${f.stops} stop`}
            </div>
          </div>
        </div>

        <div class="text-end flight-price-col">
          <div class="fw-bold fs-5">${f.price.toLocaleString()} EGP</div>
          <div class="text-muted small mb-2">per traveler</div>
          <button class="btn btn-search btn-sm w-100">
            Book now
          </button>
        </div>
      `;

      container.appendChild(card);
    });
  }

  renderFlights();
});
