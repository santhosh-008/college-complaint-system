/**
 * Nandha Engineering College - College Complaint Management System
 * Client-Side Interactivity, Live Filtering & Validation
 */

document.addEventListener('DOMContentLoaded', function () {
  initMobileNav();
  initAlertDismissal();
  initLoginTabs();
  initDemoCredentials();
  initTableLiveFilter();
  initFileInputPreview();
  initFormValidation();
});

/* -------------------------------------------------------------
   1. Mobile Navigation Toggle
   ------------------------------------------------------------- */
function initMobileNav() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', function () {
      navLinks.classList.toggle('show');
      const isExpanded = navLinks.classList.contains('show');
      toggleBtn.setAttribute('aria-expanded', isExpanded);
    });
  }
}

/* -------------------------------------------------------------
   2. Alert Dismissal
   ------------------------------------------------------------- */
function initAlertDismissal() {
  const alertCloses = document.querySelectorAll('.alert-close');
  alertCloses.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Optional: Auto-dismiss alerts after 6 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function (alert) {
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-6px)';
      setTimeout(() => alert.remove(), 400);
    });
  }, 6000);
}

/* -------------------------------------------------------------
   3. Login Tabs (Student vs Admin)
   ------------------------------------------------------------- */
function initLoginTabs() {
  const studentTabBtn = document.getElementById('tabStudent');
  const adminTabBtn = document.getElementById('tabAdmin');
  const loginTypeInput = document.getElementById('login_type');
  const identifierLabel = document.getElementById('identifierLabel');
  const identifierInput = document.getElementById('identifier');
  const studentDemoBox = document.getElementById('studentDemoBox');
  const adminDemoBox = document.getElementById('adminDemoBox');

  if (!studentTabBtn || !adminTabBtn) return;

  function switchTab(type) {
    if (type === 'student') {
      studentTabBtn.classList.add('active');
      adminTabBtn.classList.remove('active');
      if (loginTypeInput) loginTypeInput.value = 'student';
      if (identifierLabel) identifierLabel.textContent = 'Student ID / Roll No';
      if (identifierInput) {
        identifierInput.placeholder = 'e.g. STU001 or 7322...';
        identifierInput.name = 'identifier';
      }
      if (studentDemoBox) studentDemoBox.style.display = 'block';
      if (adminDemoBox) adminDemoBox.style.display = 'none';
    } else {
      adminTabBtn.classList.add('active');
      studentTabBtn.classList.remove('active');
      if (loginTypeInput) loginTypeInput.value = 'admin';
      if (identifierLabel) identifierLabel.textContent = 'Admin Username';
      if (identifierInput) {
        identifierInput.placeholder = 'e.g. admin';
        identifierInput.name = 'identifier';
      }
      if (studentDemoBox) studentDemoBox.style.display = 'none';
      if (adminDemoBox) adminDemoBox.style.display = 'block';
    }
  }

  studentTabBtn.addEventListener('click', () => switchTab('student'));
  adminTabBtn.addEventListener('click', () => switchTab('admin'));
}

/* -------------------------------------------------------------
   4. Demo Credentials Autofill Helper
   ------------------------------------------------------------- */
function initDemoCredentials() {
  const fillButtons = document.querySelectorAll('[data-fill-id]');
  fillButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const idVal = btn.getAttribute('data-fill-id');
      const passVal = btn.getAttribute('data-fill-pass');
      const typeVal = btn.getAttribute('data-fill-type');

      // Switch tab if appropriate
      const studentTabBtn = document.getElementById('tabStudent');
      const adminTabBtn = document.getElementById('tabAdmin');
      if (typeVal === 'student' && studentTabBtn) {
        studentTabBtn.click();
      } else if (typeVal === 'admin' && adminTabBtn) {
        adminTabBtn.click();
      }

      const idInput = document.getElementById('identifier');
      const passInput = document.getElementById('password');
      if (idInput) idInput.value = idVal;
      if (passInput) passInput.value = passVal;

      // Highlight inputs briefly
      [idInput, passInput].forEach(inp => {
        if (inp) {
          inp.style.backgroundColor = '#ecfdf5';
          setTimeout(() => (inp.style.backgroundColor = ''), 500);
        }
      });
    });
  });
}

/* -------------------------------------------------------------
   5. Dynamic Table Live Filtering (Admin & Student)
   ------------------------------------------------------------- */
function initTableLiveFilter() {
  const table = document.getElementById('complaintsTable');
  if (!table) return;

  const searchInput = document.getElementById('searchInput');
  const statusFilter = document.getElementById('statusFilter');
  const categoryFilter = document.getElementById('categoryFilter');
  const priorityFilter = document.getElementById('priorityFilter');
  const deptFilter = document.getElementById('deptFilter');
  const resetBtn = document.getElementById('resetFiltersBtn');
  const filterCountEl = document.getElementById('filterCount');
  const emptyRow = document.getElementById('noResultsRow');

  const rows = table.querySelectorAll('tbody tr:not(#noResultsRow)');

  function applyFilters() {
    const searchVal = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const statusVal = statusFilter ? statusFilter.value.toLowerCase().trim() : '';
    const categoryVal = categoryFilter ? categoryFilter.value.toLowerCase().trim() : '';
    const priorityVal = priorityFilter ? priorityFilter.value.toLowerCase().trim() : '';
    const deptVal = deptFilter ? deptFilter.value.toLowerCase().trim() : '';

    let visibleCount = 0;

    rows.forEach(function (row) {
      const rowText = row.textContent.toLowerCase();
      const rowStatus = (row.getAttribute('data-status') || '').toLowerCase();
      const rowCategory = (row.getAttribute('data-category') || '').toLowerCase();
      const rowPriority = (row.getAttribute('data-priority') || '').toLowerCase();
      const rowDept = (row.getAttribute('data-dept') || '').toLowerCase();

      const matchesSearch = !searchVal || rowText.includes(searchVal);
      const matchesStatus = !statusVal || rowStatus === statusVal;
      const matchesCategory = !categoryVal || rowCategory === categoryVal;
      const matchesPriority = !priorityVal || rowPriority === priorityVal;
      const matchesDept = !deptVal || rowDept === deptVal;

      if (matchesSearch && matchesStatus && matchesCategory && matchesPriority && matchesDept) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (filterCountEl) {
      filterCountEl.textContent = `Showing ${visibleCount} of ${rows.length} complaints`;
    }

    if (emptyRow) {
      emptyRow.style.display = visibleCount === 0 ? '' : 'none';
    }
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (statusFilter) statusFilter.addEventListener('change', applyFilters);
  if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);
  if (priorityFilter) priorityFilter.addEventListener('change', applyFilters);
  if (deptFilter) deptFilter.addEventListener('change', applyFilters);

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      if (searchInput) searchInput.value = '';
      if (statusFilter) statusFilter.value = '';
      if (categoryFilter) categoryFilter.value = '';
      if (priorityFilter) priorityFilter.value = '';
      if (deptFilter) deptFilter.value = '';
      applyFilters();
    });
  }

  // Initial count update
  applyFilters();
}

/* -------------------------------------------------------------
   6. File Input Selected Preview
   ------------------------------------------------------------- */
function initFileInputPreview() {
  const fileInput = document.getElementById('attachment');
  const fileNameDisplay = document.getElementById('selectedFileName');

  if (fileInput && fileNameDisplay) {
    fileInput.addEventListener('change', function () {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        fileNameDisplay.textContent = `Selected: ${file.name} (${fileSizeMB} MB)`;
        fileNameDisplay.style.display = 'block';
      } else {
        fileNameDisplay.textContent = '';
        fileNameDisplay.style.display = 'none';
      }
    });
  }
}

/* -------------------------------------------------------------
   7. Form Validation Feedback
   ------------------------------------------------------------- */
function initFormValidation() {
  const complaintForm = document.getElementById('complaintForm');
  if (complaintForm) {
    complaintForm.addEventListener('submit', function (e) {
      const title = document.getElementById('title');
      const category = document.getElementById('category');
      const department = document.getElementById('department');
      const description = document.getElementById('description');

      let isValid = true;
      let errorMsg = '';

      if (!title || !title.value.trim()) {
        isValid = false;
        errorMsg = 'Please enter a complaint title.';
      } else if (!category || !category.value) {
        isValid = false;
        errorMsg = 'Please select a complaint category.';
      } else if (!department || !department.value) {
        isValid = false;
        errorMsg = 'Please select your department.';
      } else if (!description || !description.value.trim()) {
        isValid = false;
        errorMsg = 'Please provide a clear description.';
      }

      if (!isValid) {
        e.preventDefault();
        alert(errorMsg);
      }
    });
  }
}
