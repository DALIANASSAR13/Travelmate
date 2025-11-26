
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    const featureCards = document.querySelectorAll('.feature-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    
    });

    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(245, 247, 248, 0.95)';
        } else {
            navbar.style.backgroundColor = 'rgba(245, 247, 248, 0.8)';
        }
    });

document.getElementById('goToSignUp').addEventListener('click', function(){
  var signInModal = bootstrap.Modal.getInstance(document.getElementById('signInModal'));
  signInModal.hide();
  var signUpModal = new bootstrap.Modal(document.getElementById('signUpModal'));
  signUpModal.show();
});

document.getElementById('goToSignIn').addEventListener('click', function(){
  var signUpModal = bootstrap.Modal.getInstance(document.getElementById('signUpModal'));
  signUpModal.hide();
  var signInModal = new bootstrap.Modal(document.getElementById('signInModal'));
  signInModal.show();
});

let isSignedIn = false; 

document.getElementById("myBookingBtn").addEventListener("click", function () {
  if (!isSignedIn) {
    const signInModal = new bootstrap.Modal(document.getElementById('signInModal'));
    signInModal.show();
  } else {
    window.location.href = "mybooking.html";
  }
});

document.querySelector("#signInModal form").addEventListener("submit", (e) => {
  e.preventDefault();
  isSignedIn = true;
  alert("You are now signed in!");
  bootstrap.Modal.getInstance(document.getElementById("signInModal")).hide();
});
