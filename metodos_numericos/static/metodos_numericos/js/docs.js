// Aninmacion de la barras
document.addEventListener("DOMContentLoaded", function() {
gsap.from(["#rojo", "#amarillo", "#verde"], {
  y: -120,
  opacity: 0,
  duration: 1.2,
  stagger: 0.18,
  ease: "bounce.out"
});

gsap.from("#lineaFlecha", {
  scale: 0,
  transformOrigin: "center center",
  duration: 1,
  delay: 1.3,
  ease: "elastic.out(1, 0.6)"
});
});

document.querySelectorAll(".navbar-nav a").forEach((btn, index) => {
  btn.addEventListener("click", () => {
    const target = "#section" + (index + 1);

    // Feedback visual: escala rápida
    gsap.fromTo(btn, 
      { scale: 1 }, 
      { scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: "power1.inOut" }
    );

    // Desactivar temporalmente el botón
    btn.style.pointerEvents = "none";

    // Animar scroll con easing
    gsap.to(window, {
      duration: 2.2,
      ease: "power4.inOut",
      scrollTo: { y: target, offsetY: 85 },
      onComplete: () => {
        btn.style.pointerEvents = "";
      }
    });
  });
});

