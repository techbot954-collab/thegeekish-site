(function () {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("geekish-theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  root.dataset.theme = savedTheme || (prefersDark ? "dark" : "light");

  const themeButton = document.querySelector("[data-theme-toggle]");
  if (themeButton) {
    themeButton.addEventListener("click", () => {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = nextTheme;
      localStorage.setItem("geekish-theme", nextTheme);
    });
  }

  const form = document.querySelector("[data-join-form]");
  if (!form) return;

  const note = form.querySelector("[data-form-note]");
  const tabs = Array.from(form.querySelectorAll("[data-form-mode]"));
  const submit = form.querySelector(".form-submit");
  let mode = "join";

  function setNote(message, kind) {
    note.textContent = message;
    note.className = `form-note ${kind || ""}`.trim();
  }

  function getProfiles() {
    try {
      return JSON.parse(localStorage.getItem("geekish-profiles") || "[]");
    } catch (_error) {
      return [];
    }
  }

  function saveProfiles(profiles) {
    localStorage.setItem("geekish-profiles", JSON.stringify(profiles));
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      mode = tab.dataset.formMode;
      tabs.forEach((item) => item.classList.toggle("active", item === tab));
      submit.textContent = mode === "join" ? "Create free profile" : "Sign in";
      setNote(
        mode === "join"
          ? "This preview saves uniqueness checks in this browser until the production account database is connected."
          : "Sign-in preview checks the usernames and emails already saved in this browser.",
        ""
      );
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const data = new FormData(form);
    const username = String(data.get("username") || "").trim().toLowerCase();
    const email = String(data.get("email") || "").trim().toLowerCase();
    const password = String(data.get("password") || "");
    const emailConsent = data.get("emailConsent") === "on";
    const profiles = getProfiles();

    if (!username || !email || password.length < 8) {
      setNote("Use a username, valid email, and password with at least 8 characters.", "error");
      return;
    }

    if (mode === "signin") {
      const match = profiles.find((profile) => profile.username === username && profile.email === email);
      setNote(
        match
          ? `Welcome back, ${username}. Production login will connect this to the real account system.`
          : "No saved preview profile matches that username and email yet.",
        match ? "success" : "error"
      );
      return;
    }

    if (profiles.some((profile) => profile.username === username)) {
      setNote("That username is already reserved. Try a different one.", "error");
      return;
    }
    if (profiles.some((profile) => profile.email === email)) {
      setNote("That email is already reserved. Use a different email or sign in.", "error");
      return;
    }

    profiles.push({
      username,
      email,
      emailConsent,
      createdAt: new Date().toISOString()
    });
    saveProfiles(profiles);

    setNote(
      emailConsent
        ? "Profile reserved. Email updates are marked as allowed for the production system."
        : "Profile reserved. Email updates are off until you choose to allow them.",
      "success"
    );
    form.reset();
  });
})();
