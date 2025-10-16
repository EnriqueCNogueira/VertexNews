import React, { useMemo } from 'react';
import NewsCard from './NewsCard';

const NewsGrid = ({ news, isLoading, onNewsClick }) => {
  const skeletonItems = useMemo(() => 
    [...Array(6)].map((_, index) => (
      <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
        <div className="h-48 bg-gray-300"></div>
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex space-x-1">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="w-4 h-4 bg-gray-300 rounded"></div>
              ))}
            </div>
            <div className="w-8 h-4 bg-gray-300 rounded"></div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          </div>
          <div className="mt-3 space-y-2">
            <div className="h-3 bg-gray-300 rounded"></div>
            <div className="h-3 bg-gray-300 rounded w-5/6"></div>
            <div className="h-3 bg-gray-300 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    )), []
  );

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" role="status" aria-label="Carregando notícias">
        {skeletonItems}
      </div>
    );
  }

  if (!news || news.length === 0) {
    return (
      <div className="text-center py-12" role="status" aria-live="polite">
        <div className="w-24 h-24 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center" aria-hidden="true">
          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">Nenhuma notícia encontrada</h3>
        <p className="text-gray-500">Tente recarregar a página ou verificar sua conexão.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" role="main" aria-label="Lista de notícias">
      {news.map((item) => (
        <NewsCard key={item.id} news={item} onCardClick={onNewsClick} />
      ))}
    </div>
  );
};

export default React.memo(NewsGrid);
