const toggleBtn = document.querySelector('.nav-toggle');
const nav = document.querySelector('.site-nav');
if (toggleBtn && nav) {
  toggleBtn.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    toggleBtn.setAttribute('aria-expanded', String(isOpen));
  });
}