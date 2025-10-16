import React, { useState, useEffect, useCallback } from 'react';
import StarRating from './StarRating';

const NewsModal = ({ news, isOpen, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      // Pequeno delay para garantir que o DOM foi atualizado
      setTimeout(() => setIsAnimating(true), 10);
    } else {
      setIsAnimating(false);
      // Delay para permitir animação de saída
      setTimeout(() => setIsVisible(false), 300);
    }
  }, [isOpen]);

  const handleBackdropClick = useCallback((e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  const handleLinkClick = useCallback(() => {
    if (news?.link) {
      window.open(news.link, '_blank');
    }
  }, [news?.link]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  if (!isVisible || !news) return null;


  return (
    <div 
      className={`fixed inset-0 flex items-center justify-center z-50 p-4 transition-all duration-300 ${
        isAnimating 
          ? 'bg-black bg-opacity-60' 
          : 'bg-black bg-opacity-0'
      }`}
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
    >
      <div 
        className={`bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden transform transition-all duration-300 ${
          isAnimating 
            ? 'scale-100 opacity-100 translate-y-0' 
            : 'scale-95 opacity-0 translate-y-4'
        }`}
      >
        {/* Header do Modal */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <StarRating 
              score={news.score} 
              size="lg"
              showLabel={true}
            />
            <span className="text-sm text-gray-600 font-medium">
              {news.fonte}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            aria-label="Fechar modal"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Conteúdo do Modal */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Imagem */}
          <div className="relative h-64 md:h-80 overflow-hidden">
            <img
              src={news.imagem}
              alt={news.titulo}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={(e) => {
                e.target.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&h=400&fit=crop';
              }}
            />
          </div>

          {/* Conteúdo */}
          <div className="p-6">
            {/* Título */}
            <h2 id="modal-title" className="text-2xl font-bold text-gray-800 mb-4 text-center">
              {news.titulo}
            </h2>

            {/* Resumo */}
            <div id="modal-description" className="prose prose-lg max-w-none mb-6">
              <p className="text-gray-700 leading-relaxed text-justify">
                &nbsp;&nbsp;&nbsp;&nbsp;{news.resumo}
              </p>
            </div>

            {/* Botão para ler notícia completa */}
            <div className="flex justify-center">
              <button
                onClick={handleLinkClick}
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 text-lg font-medium"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Ler Notícia Completa
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(NewsModal);
