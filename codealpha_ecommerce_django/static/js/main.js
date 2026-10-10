document.addEventListener("DOMContentLoaded", () => {
  // Add a subtle confirmation to checkout and prevent accidental double-submit.
  document.querySelectorAll(".checkout-form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (button) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = "Placing order…";
      }
    });
  });

  // Dismiss status messages after a short pause.
  document.querySelectorAll(".message").forEach((message) => {
    window.setTimeout(() => {
      message.classList.add("message-hide");
      window.setTimeout(() => message.remove(), 350);
    }, 4500);
  });
});
