/* ═══════════════════════════════════════════════════════════════
   AI Health Prediction System — Landing Page Scripts
   particles.js · AOS · Animated Counters · Navbar · Smooth Scroll
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

    /* ──────────────────────────────────────────────────
       1. PARTICLES.JS CONFIGURATION
       ────────────────────────────────────────────────── */
    if (typeof particlesJS !== "undefined" && document.getElementById("particles-js")) {
        particlesJS("particles-js", {
            particles: {
                number:  { value: 80, density: { enable: true, value_area: 900 } },
                color:   { value: ["#00d4ff", "#7c3aed", "#f472b6"] },
                shape:   { type: "circle" },
                opacity: { value: 0.35, random: true,
                           anim: { enable: true, speed: 0.6, opacity_min: 0.1, sync: false } },
                size:    { value: 2.5, random: true,
                           anim: { enable: true, speed: 1.5, size_min: 0.5, sync: false } },
                line_linked: {
                    enable: true, distance: 130,
                    color: "#00d4ff", opacity: 0.12, width: 1
                },
                move: {
                    enable: true, speed: 1.2,
                    direction: "none", random: true,
                    straight: false, out_mode: "out",
                    attract: { enable: true, rotateX: 600, rotateY: 1200 }
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "grab" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                },
                modes: {
                    grab:   { distance: 180, line_linked: { opacity: 0.35 } },
                    push:   { particles_nb: 3 }
                }
            },
            retina_detect: true
        });
    }

    /* ──────────────────────────────────────────────────
       2. AOS – SCROLL ANIMATIONS
       ────────────────────────────────────────────────── */
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 800,
            easing: "ease-out-cubic",
            once: true,
            offset: 80
        });
    }

    /* ──────────────────────────────────────────────────
       3. NAVBAR SCROLL EFFECT
       ────────────────────────────────────────────────── */
    const navbar = document.getElementById("navbar");
    if (navbar) {
        const onScroll = () => {
            navbar.classList.toggle("scrolled", window.scrollY > 40);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    /* ──────────────────────────────────────────────────
       4. HAMBURGER MENU (MOBILE)
       ────────────────────────────────────────────────── */
    const hamburger = document.getElementById("hamburger");
    const navLinks  = document.getElementById("navLinks");
    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("open");
        });
        // close menu on link click
        navLinks.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => {
                hamburger.classList.remove("active");
                navLinks.classList.remove("open");
            });
        });
    }

    /* ──────────────────────────────────────────────────
       5. ANIMATED COUNTERS (Intersection Observer)
       ────────────────────────────────────────────────── */
    const counters = document.querySelectorAll(".lp-counter-num");
    const animateCounter = (el) => {
        const target = +el.dataset.target;
        const suffix = el.dataset.suffix || "";
        const duration = 2000; // ms
        const startTime = performance.now();

        const step = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // easeOutExpo
            const ease = 1 - Math.pow(2, -10 * progress);
            const current = Math.round(target * ease);
            el.textContent = current.toLocaleString() + suffix;
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };

    if (counters.length) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(c => counterObserver.observe(c));
    }

    /* ──────────────────────────────────────────────────
       6. SMOOTH SCROLL FOR ANCHOR LINKS
       ────────────────────────────────────────────────── */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", (e) => {
            const id = anchor.getAttribute("href");
            if (id === "#") return;
            const target = document.querySelector(id);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    /* ──────────────────────────────────────────────────
       7. TYPING EFFECT ON HERO SUBTITLE
       ────────────────────────────────────────────────── */
    const subtitle = document.querySelector(".lp-hero-subtitle");
    if (subtitle) {
        const text = subtitle.textContent;
        subtitle.textContent = "";
        let i = 0;
        const type = () => {
            if (i < text.length) {
                subtitle.textContent += text[i];
                i++;
                setTimeout(type, 45);
            }
        };
        // start after a brief delay
        setTimeout(type, 800);
    }

    /* ──────────────────────────────────────────────────
       8. ACTIVE NAV LINK HIGHLIGHT ON SCROLL
       ────────────────────────────────────────────────── */
    const sections = document.querySelectorAll("section[id]");
    const navAnchors = document.querySelectorAll(".lp-nav-links a");
    if (navAnchors.length) {
        const highlightNav = () => {
            let current = "";
            sections.forEach(sec => {
                const top = sec.offsetTop - 120;
                if (window.scrollY >= top) current = sec.id;
            });
            navAnchors.forEach(a => {
                a.style.color = a.getAttribute("href") === "#" + current
                    ? "#00d4ff" : "";
            });
        };
        window.addEventListener("scroll", highlightNav, { passive: true });
    }

    /* ──────────────────────────────────────────────────
       9. LEGAL DOCUMENT ENHANCEMENTS
       ────────────────────────────────────────────────── */
    const tocLinks = document.querySelectorAll("[data-toc-link]");
    const legalSections = document.querySelectorAll("section[id].legal-section");
    const legalProgress = document.querySelector("[data-legal-progress]");
    if (tocLinks.length && legalSections.length) {
        const setActiveSection = (activeId) => {
            tocLinks.forEach(link => {
                const isActive = link.getAttribute("href") === "#" + activeId;
                link.classList.toggle("active", isActive);
                if (isActive) {
                    link.setAttribute("aria-current", "true");
                } else {
                    link.removeAttribute("aria-current");
                }
            });
        };

        const legalObserver = new IntersectionObserver((entries) => {
            const visible = entries
                .filter(entry => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
            if (visible && visible.target && visible.target.id) {
                setActiveSection(visible.target.id);
            }
        }, { rootMargin: "-22% 0px -62% 0px", threshold: [0.08, 0.2, 0.35] });

        legalSections.forEach(section => legalObserver.observe(section));
        if (window.location.hash) {
            const initial = document.querySelector(window.location.hash);
            if (initial && initial.id) setActiveSection(initial.id);
        } else if (legalSections[0] && legalSections[0].id) {
            setActiveSection(legalSections[0].id);
        }
    }

    if (legalProgress) {
        const updateLegalProgress = () => {
            const doc = document.documentElement;
            const maxScroll = Math.max(1, doc.scrollHeight - window.innerHeight);
            const progress = Math.min(100, Math.max(0, (window.scrollY / maxScroll) * 100));
            legalProgress.style.width = progress + "%";
        };
        window.addEventListener("scroll", updateLegalProgress, { passive: true });
        updateLegalProgress();
    }

    const copyButtons = document.querySelectorAll("[data-copy-link]");
    if (copyButtons.length) {
        copyButtons.forEach(button => {
            button.addEventListener("click", async () => {
                const target = button.getAttribute("data-copy-link");
                if (!target) return;
                const url = new URL(window.location.href);
                url.hash = target;
                try {
                    await navigator.clipboard.writeText(url.toString());
                    const original = button.textContent;
                    button.textContent = "Copied";
                    button.setAttribute("aria-label", "Copied section link");
                    setTimeout(() => {
                        button.textContent = original;
                        button.removeAttribute("aria-label");
                    }, 1600);
                } catch (error) {
                    window.location.hash = target;
                }
            });
        });
    }

    const backToTop = document.querySelector("[data-back-to-top]");
    if (backToTop) {
        const onScroll = () => {
            backToTop.classList.toggle("is-visible", window.scrollY > 560);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    /* ──────────────────────────────────────────────────
       10. PARALLAX LOTTIE ON SCROLL
       ────────────────────────────────────────────────── */
    const lottie = document.querySelector(".lp-hero-lottie");
    if (lottie) {
        window.addEventListener("scroll", () => {
            const y = window.scrollY;
            if (y < window.innerHeight) {
                lottie.style.transform = "translateY(" + (y * 0.15) + "px) scale(" + (1 - y * 0.0003) + ")";
                lottie.style.opacity = 1 - y / (window.innerHeight * 0.8);
            }
        }, { passive: true });
    }

});
