document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api/auth";
  const welcomeText = document.getElementById("welcomeText");
  const logoutBtn = document.getElementById("logoutBtn");

  async function checkAuth() {
    try {
      const res = await fetch(`${API_BASE}/me`, {
        credentials: "include"
      });
      const data = await res.json();

      if (!data.authenticated || !data.user) {
        // لو مش داخل → رجّعه على الـHome
        window.location.href = "/";
        return;
      }

      welcomeText.textContent = `Welcome, ${data.user.first_name}! Here are your bookings.`;
    } catch (err) {
      window.location.href = "/";
    }
  }

  logoutBtn.addEventListener("click", async () => {
    try {
      await fetch(`${API_BASE}/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({})
      });
    } catch (err) {
      console.log("Logout error:", err.message);
    }
    window.location.href = "/";
  });

  checkAuth();
});
