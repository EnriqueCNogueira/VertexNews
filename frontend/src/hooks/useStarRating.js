import { useMemo } from 'react';

/**
 * Hook customizado para renderizar sistema de avaliação por estrelas
 * @param {number} score - Pontuação da notícia (0-20)
 * @param {number} maxScore - Pontuação máxima (padrão: 20)
 * @param {number} maxStars - Número máximo de estrelas (padrão: 5)
 * @param {string} size - Tamanho das estrelas ('sm' | 'md' | 'lg')
 * @returns {Array} Array de elementos SVG das estrelas
 */
export const useStarRating = (score, maxScore = 20, maxStars = 5, size = 'md') => {
  const starSize = useMemo(() => {
    const sizes = {
      sm: 'w-3 h-3',
      md: 'w-4 h-4',
      lg: 'w-5 h-5'
    };
    return sizes[size] || sizes.md;
  }, [size]);

  const stars = useMemo(() => {
    const starElements = [];
    
    // Converter score para estrelas (score de 20 = 5 estrelas)
    const starValue = (score / maxScore) * maxStars;
    const fullStars = Math.floor(starValue);
    const hasHalfStar = starValue % 1 >= 0.5;

    // Estrelas preenchidas
    for (let i = 0; i < fullStars; i++) {
      starElements.push(
        <svg 
          key={i} 
          className={`${starSize}`} 
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path 
            fill="#facc15" 
            stroke="#000000" 
            strokeWidth="0.2"
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
        </svg>
      );
    }

    // Meia estrela
    if (hasHalfStar) {
      starElements.push(
        <svg 
          key="half" 
          className={`${starSize}`} 
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id={`half-${score}`}>
              <stop offset="50%" stopColor="#facc15"/>
              <stop offset="50%" stopColor="#d1d5db"/>
            </linearGradient>
            <mask id={`mask-${score}`}>
              <rect width="10" height="20" fill="white"/>
            </mask>
          </defs>
          {/* Estrela cinza completa */}
          <path 
            fill="#d1d5db" 
            stroke="#000000" 
            strokeWidth="0.2"
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
          {/* Metade amarela */}
          <path 
            fill="#facc15" 
            stroke="#000000" 
            strokeWidth="0.2"
            mask={`url(#mask-${score})`}
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
        </svg>
      );
    }

    // Estrelas vazias
    const emptyStars = maxStars - Math.ceil(starValue);
    for (let i = 0; i < emptyStars; i++) {
      starElements.push(
        <svg 
          key={`empty-${i}`} 
          className={`${starSize}`} 
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path 
            fill="#d1d5db" 
            stroke="#000000" 
            strokeWidth="0.2"
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
        </svg>
      );
    }

    return starElements;
  }, [score, maxScore, maxStars, starSize]);

  return stars;
};
