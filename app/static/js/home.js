function initFeatures(){
    document.querySelectorAll('nav a').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const section = document.querySelector(this.getAttribute('href'));
        if (section) { section.scrollIntoView({ behavior: 'smooth' }); }
      });
    });

    const boxes = document.querySelectorAll(".box");
    window.addEventListener("scroll", () => {
      boxes.forEach(box => {
        const rect = box.getBoundingClientRect();
        if (rect.top < window.innerHeight - 50) { box.classList.add("visible"); }
      });
    });

    const text = "smart study assistant";
    let i = 0;
    function typeEffect() {
      if (i < text.length) {
        document.querySelector(".heading").innerHTML = text.substring(0, i+1);
        i++;
        setTimeout(typeEffect, 100);
      }
    }
    typeEffect();
  }

  window.onload = () => {
    setTimeout(() => {
      document.getElementById("preloader").style.opacity = "0";
      document.getElementById("preloader").style.visibility = "hidden";
      initFeatures();
    }, 2000);
  };
    function openModal(id) {
    document.getElementById(id).style.display = 'flex';
  }
  function closeModal(id) {
    document.getElementById(id).style.display = 'none';
  }

  // Close modal when clicking outside
  window.onclick = function(e) {
    if (e.target.classList.contains('modal')) {
      e.target.style.display = 'none';
    }
  }