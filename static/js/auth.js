/**
 * AirSense AI — Authentication Module (auth.js)
 * Manages:
 *   - Login overlay show/hide
 *   - Sign In / Sign Up mode switching
 *   - Demo credential one-click pills (fetched from /api/auth/demo-users)
 *   - Session persistence via sessionStorage
 *   - Sidebar user profile update
 *   - Sign-Out flow
 */

const AuthModule = (() => {
  const SESSION_KEY = "airsense_session";

  function _getOverlay() { return document.getElementById("auth-overlay"); }

  function _showError(msg) {
    const el = document.getElementById("auth-error");
    const txt = document.getElementById("auth-error-text");
    if (el && txt) {
      txt.textContent = msg;
      el.style.display = "flex";
      el.style.animation = "none";
      el.offsetHeight;
      el.style.animation = "";
    }
  }

  function _hideError() {
    const el = document.getElementById("auth-error");
    if (el) el.style.display = "none";
  }

  function _setLoading(formId, loading) {
    const spinnerId = formId === "form-signin" ? "spinner-signin" : "spinner-signup";
    const btnId     = formId === "form-signin" ? "btn-submit-signin" : "btn-submit-signup";
    const spinner = document.getElementById(spinnerId);
    const btn     = document.getElementById(btnId);
    const txt     = btn ? btn.querySelector(".auth-btn-text") : null;
    if (spinner) spinner.style.display = loading ? "block" : "none";
    if (txt)     txt.style.display     = loading ? "none" : "flex";
    if (btn)     btn.disabled = loading;
  }

  function _saveSession(user) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
  }

  function _getSession() {
    try { return JSON.parse(sessionStorage.getItem(SESSION_KEY)); }
    catch { return null; }
  }

  function _clearSession() {
    sessionStorage.removeItem(SESSION_KEY);
  }

  function _updateSidebarProfile(user) {
    const avatarEl = document.getElementById("sidebar-avatar");
    const nameEl   = document.getElementById("sidebar-user-name");
    const roleEl   = document.getElementById("sidebar-user-role");
    if (avatarEl) {
      avatarEl.textContent = user.initials || user.name.slice(0, 2).toUpperCase();
      avatarEl.style.background = user.avatar_color || "#2563eb";
    }
    if (nameEl) nameEl.textContent = user.name || "EcoAir User";
    if (roleEl) roleEl.textContent = user.role || user.health_profile || "Environmental Intelligence";
  }

  function _showSuccessToast(message) {
    const existing = document.querySelector(".auth-success-toast");
    if (existing) existing.remove();
    const toast = document.createElement("div");
    toast.className = "auth-success-toast";
    toast.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>${message}`;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-12px)";
      setTimeout(() => toast.remove(), 420);
    }, 3200);
  }

  async function _loadDemoUsers() {
    const container = document.getElementById("demo-pills-container");
    if (!container) return;
    try {
      const res = await fetch("/api/auth/demo-users");
      if (!res.ok) throw new Error("Failed");
      const users = await res.json();
      container.innerHTML = "";
      users.forEach(user => {
        const pill = document.createElement("button");
        pill.type = "button";
        pill.className = "demo-pill";
        pill.id = `demo-pill-${user.id}`;
        pill.innerHTML = `
          <div class="demo-pill-avatar" style="background:${user.avatar_color};">${user.initials}</div>
          <div class="demo-pill-info">
            <div class="demo-pill-name">${user.icon} ${user.name}</div>
            <div class="demo-pill-creds">${user.email}&nbsp;/&nbsp;${user.password}</div>
          </div>
          <span class="demo-pill-tag">${user.tag}</span>
        `;
        pill.addEventListener("click", () => {
          const emailInput    = document.getElementById("si-email");
          const passwordInput = document.getElementById("si-password");
          if (emailInput)    emailInput.value    = user.email;
          if (passwordInput) passwordInput.value = user.password;
          container.querySelectorAll(".demo-pill").forEach(p => p.classList.remove("selected"));
          pill.classList.add("selected");
          _hideError();
        });
        container.appendChild(pill);
      });
    } catch (err) {
      console.warn("Could not fetch demo users:", err);
      container.innerHTML = `
        <button type="button" class="demo-pill" onclick="(function(e){document.getElementById('si-email').value='admin@ecoair.gov.in';document.getElementById('si-password').value='admin123';e.currentTarget.closest('.demo-pills').querySelectorAll('.demo-pill').forEach(p=>p.classList.remove('selected'));e.currentTarget.classList.add('selected');})(event)">
          <div class="demo-pill-avatar" style="background:#2563eb;">HK</div>
          <div class="demo-pill-info"><div class="demo-pill-name">&#x1F6E1;&#xFE0F; Harika K. (Admin)</div><div class="demo-pill-creds">admin@ecoair.gov.in / admin123</div></div>
          <span class="demo-pill-tag">Admin &#x2022; Full Access</span>
        </button>
        <button type="button" class="demo-pill" onclick="(function(e){document.getElementById('si-email').value='citizen@ecoair.org';document.getElementById('si-password').value='demo123';e.currentTarget.closest('.demo-pills').querySelectorAll('.demo-pill').forEach(p=>p.classList.remove('selected'));e.currentTarget.classList.add('selected');})(event)">
          <div class="demo-pill-avatar" style="background:#059669;">AS</div>
          <div class="demo-pill-info"><div class="demo-pill-name">&#x1F6B4; Aarav Sharma</div><div class="demo-pill-creds">citizen@ecoair.org / demo123</div></div>
          <span class="demo-pill-tag">Citizen &#x2022; Standard</span>
        </button>
        <button type="button" class="demo-pill" onclick="(function(e){document.getElementById('si-email').value='asthma.care@airsense.org';document.getElementById('si-password').value='health123';e.currentTarget.closest('.demo-pills').querySelectorAll('.demo-pill').forEach(p=>p.classList.remove('selected'));e.currentTarget.classList.add('selected');})(event)">
          <div class="demo-pill-avatar" style="background:#ea580c;">RV</div>
          <div class="demo-pill-info"><div class="demo-pill-name">&#x1FAC1; Dr. Rohan Verma</div><div class="demo-pill-creds">asthma.care@airsense.org / health123</div></div>
          <span class="demo-pill-tag">High Sensitivity &#x2022; 1.4&#xD7;</span>
        </button>`;
    }
  }

  return {
    init() {
      const session = _getSession();
      if (session && session.name) {
        _updateSidebarProfile(session);
        this.hideOverlay();
      } else {
        this.showOverlay();
        _loadDemoUsers();
      }
    },

    showOverlay() {
      const ov = _getOverlay();
      if (ov) { ov.classList.remove("hidden"); document.body.style.overflow = "hidden"; }
    },

    hideOverlay() {
      const ov = _getOverlay();
      if (ov) { ov.classList.add("hidden"); document.body.style.overflow = ""; }
    },

    switchMode(mode) {
      const isSignIn = mode === "signin";
      document.getElementById("form-signin").style.display = isSignIn ? "flex" : "none";
      document.getElementById("form-signup").style.display = isSignIn ? "none" : "flex";
      document.getElementById("btn-mode-signin").classList.toggle("active", isSignIn);
      document.getElementById("btn-mode-signup").classList.toggle("active", !isSignIn);
      const demoBox = document.getElementById("demo-creds-box");
      if (demoBox) demoBox.style.display = isSignIn ? "block" : "none";
      _hideError();
    },

    togglePwd(inputId, btn) {
      const inp = document.getElementById(inputId);
      if (!inp) return;
      const isPassword = inp.type === "password";
      inp.type = isPassword ? "text" : "password";
    },

    async handleSignIn(evt) {
      evt.preventDefault();
      _hideError();
      const email    = document.getElementById("si-email")?.value.trim();
      const password = document.getElementById("si-password")?.value.trim();
      if (!email || !password) { _showError("Please enter your email and password."); return; }
      _setLoading("form-signin", true);
      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, remember_me: true })
        });
        const data = await res.json();
        if (!res.ok) { _showError(data.detail || "Invalid email or password."); return; }
        _saveSession(data.user);
        _updateSidebarProfile(data.user);
        this.hideOverlay();
        _showSuccessToast("Welcome back, " + data.user.name + "! \uD83C\uDF3F");
        if (data.user.health_profile) {
          const hdrSel = document.getElementById("header-health-profile-select");
          const pgSel  = document.getElementById("health-profile-select");
          if (hdrSel) hdrSel.value = data.user.health_profile;
          if (pgSel)  pgSel.value  = data.user.health_profile;
          if (window.App) App.state.selectedHealthProfile = data.user.health_profile;
        }
      } catch (err) {
        console.error("Login error:", err);
        _showError("Connection error. Please check your network.");
      } finally {
        _setLoading("form-signin", false);
      }
    },

    async handleSignUp(evt) {
      evt.preventDefault();
      _hideError();
      const name     = document.getElementById("su-name")?.value.trim();
      const email    = document.getElementById("su-email")?.value.trim();
      const password = document.getElementById("su-password")?.value.trim();
      const profile  = document.getElementById("su-profile")?.value;
      if (!name || !email || !password) { _showError("Please fill in all required fields."); return; }
      if (password.length < 4) { _showError("Password must be at least 4 characters long."); return; }
      _setLoading("form-signup", true);
      try {
        const res = await fetch("/api/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password, health_profile: profile || "General User" })
        });
        const data = await res.json();
        if (!res.ok) { _showError(data.detail || "Registration failed."); return; }
        _saveSession(data.user);
        _updateSidebarProfile(data.user);
        this.hideOverlay();
        _showSuccessToast("Account created! Welcome, " + data.user.name + "! \uD83C\uDF31");
        if (data.user.health_profile) {
          const hdrSel = document.getElementById("header-health-profile-select");
          const pgSel  = document.getElementById("health-profile-select");
          if (hdrSel) hdrSel.value = data.user.health_profile;
          if (pgSel)  pgSel.value  = data.user.health_profile;
          if (window.App) App.state.selectedHealthProfile = data.user.health_profile;
        }
      } catch (err) {
        console.error("Sign-up error:", err);
        _showError("Connection error. Please check your network.");
      } finally {
        _setLoading("form-signup", false);
      }
    },

    signOut() {
      const session = _getSession();
      const name = session?.name || "User";
      if (!confirm("Sign out of EcoAir, " + name + "?")) return;
      _clearSession();
      const avatarEl = document.getElementById("sidebar-avatar");
      const nameEl   = document.getElementById("sidebar-user-name");
      const roleEl   = document.getElementById("sidebar-user-role");
      if (avatarEl) { avatarEl.textContent = "?"; avatarEl.style.background = "#64748b"; }
      if (nameEl)   nameEl.textContent = "Guest Explorer";
      if (roleEl)   roleEl.textContent = "Not signed in";
      const emailInp = document.getElementById("si-email");
      const pwdInp   = document.getElementById("si-password");
      if (emailInp) emailInp.value = "";
      if (pwdInp)   pwdInp.value   = "";
      this.switchMode("signin");
      document.querySelectorAll(".demo-pill").forEach(p => p.classList.remove("selected"));
      this.showOverlay();
      _loadDemoUsers();
    }
  };
})();

window.AuthModule = AuthModule;
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => AuthModule.init());
} else {
  AuthModule.init();
}
