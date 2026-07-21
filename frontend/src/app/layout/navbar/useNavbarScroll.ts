import { useState, useEffect } from 'react';

export function useNavbarScroll(threshold = 20) {
  const [isVisible, setIsVisible] = useState(true);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      // Detect if user has scrolled past top
      setIsScrolled(currentScrollY > 10);

      // Hide on scroll down past threshold, show on scroll up
      if (currentScrollY > lastScrollY && currentScrollY > threshold) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [threshold]);

  return { isVisible, isScrolled };
}

export default useNavbarScroll;
