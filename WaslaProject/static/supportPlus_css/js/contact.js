
      document.querySelectorAll('form').forEach((form) => {
        form.addEventListener('submit', function (e) {
          const requiredFields = form.querySelectorAll('[required]');
          let isValid = true;

          requiredFields.forEach((field) => {
            if (!field.value.trim()) {
              field.classList.add('is-invalid');
              isValid = false;
            } else {
              field.classList.remove('is-invalid');
              field.classList.add('is-valid');
            }
          });

          if (!isValid) {
            e.preventDefault();
            const errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
            errorAlert.innerHTML = `
              <i class="fas fa-exclamation-triangle me-2"></i>
              Please fill in all required fields
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
            `;
            form.prepend(errorAlert);
          }
        });
      });

      document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
          e.preventDefault();
          const target = document.querySelector(this.getAttribute('href'));
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      });

      setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-dismissible)').forEach((alert) => {
          alert.style.opacity = '0';
          setTimeout(() => alert.remove(), 300);
        });
      }, 5000);
    