import React from 'react';
import { useStarRating } from '../hooks/useStarRating';

/**
 * Componente de avaliação por estrelas
 * @param {Object} props
 * @param {number} props.score - Pontuação da notícia (0-20)
 * @param {number} props.maxScore - Pontuação máxima (padrão: 20)
 * @param {number} props.maxStars - Número máximo de estrelas (padrão: 5)
 * @param {string} props.size - Tamanho das estrelas ('sm' | 'md' | 'lg')
 * @param {string} props.className - Classes CSS adicionais
 * @param {boolean} props.showLabel - Se deve mostrar label de acessibilidade
 */
const StarRating = ({ 
  score, 
  maxScore = 20, 
  maxStars = 5, 
  size = 'md', 
  className = '',
  showLabel = false 
}) => {
  const stars = useStarRating(score, maxScore, maxStars, size);
  
  const ratingText = `${Math.round((score / maxScore) * maxStars * 2) / 2} de ${maxStars} estrelas`;

  return (
    <div 
      className={`flex items-center space-x-1 ${className}`}
      role="img"
      aria-label={showLabel ? ratingText : undefined}
    >
      {stars}
      {showLabel && (
        <span className="sr-only">
          {ratingText}
        </span>
      )}
    </div>
  );
};

export default React.memo(StarRating);
