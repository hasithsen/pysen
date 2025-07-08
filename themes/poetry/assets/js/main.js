(function() {
  const THEME_KEY = 'theme';
  const DARK_CLASS = 'dark-theme';
  const LIGHT_ICON = '🌞';
  const DARK_ICON = '🌙';

  function setTheme(theme) {
    if (theme === 'dark') {
      document.body.classList.add(DARK_CLASS);
      document.getElementById('theme-toggle').textContent = LIGHT_ICON;
    } else {
      document.body.classList.remove(DARK_CLASS);
      document.getElementById('theme-toggle').textContent = DARK_ICON;
    }
    localStorage.setItem(THEME_KEY, theme);
  }

  function toggleTheme() {
    const current = localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light';
    setTheme(current === 'dark' ? 'light' : 'dark');
  }

  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    // Set initial theme
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark' || (saved === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setTheme('dark');
    } else {
      setTheme('light');
    }
    btn.addEventListener('click', toggleTheme);
  });
})();