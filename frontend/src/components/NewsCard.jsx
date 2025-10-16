import React, { useCallback } from 'react';
import StarRating from './StarRating';

const NewsCard = ({ news, onCardClick }) => {
  const handleCardClick = useCallback(() => {
    onCardClick(news);
  }, [news, onCardClick]);

  const handleLinkClick = useCallback((e) => {
    e.stopPropagation();
    window.open(news.link, '_blank');
  }, [news.link]);

  return (
    <article 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden"
      onClick={handleCardClick}
      role="button"
      tabIndex={0}
      aria-label={`Ver detalhes da notícia: ${news.titulo}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleCardClick();
        }
      }}
    >
      {/* Imagem */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={news.imagem}
          alt={news.titulo}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=250&fit=crop';
          }}
        />
      </div>

      {/* Conteúdo */}
      <div className="p-4">
        {/* Fonte da notícia */}
        <div className="flex items-center justify-between mb-3">
          <StarRating 
            score={news.score} 
            size="md"
            showLabel={true}
          />
          <span className="text-sm text-gray-600 font-medium">
            {news.fonte}
          </span>
        </div>

        {/* Título */}
        <h3 className="text-lg font-semibold text-gray-800 mb-2 text-center">
          {news.titulo}
        </h3>
      </div>
    </article>
  );
};

export default React.memo(NewsCard);
