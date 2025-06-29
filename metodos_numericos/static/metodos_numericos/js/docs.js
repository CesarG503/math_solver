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