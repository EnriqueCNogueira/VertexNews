import React, { useCallback } from 'react';
import Logo from '../assets/Logo.png';

const Header = () => {
  const handleSiteClick = useCallback(() => {
    window.open('https://enriquenogueira.netlify.app/', '_blank');
  }, []);

  return (
    <header className="bg-dark-blue text-white py-6 px-4 shadow-lg" role="banner">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img 
              src={Logo} 
              alt="VertexNews Logo" 
              className="h-10 w-10 object-contain"
              style={{backgroundColor: 'transparent'}}
            />
            <h1 className="text-3xl font-bold text-white">
              <span className="text-3xl">Vertex</span>
              <span className="text-xl align-top">News</span>
            </h1>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <button
              onClick={handleSiteClick}
              className="bg-transparent border border-white/80 text-white px-4 py-2 rounded-lg hover:border-white hover:bg-white/10 transition-all duration-200 font-medium inline-flex items-center"
              aria-label="Acessar site pessoal do desenvolvedor"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Acesse meu site
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default React.memo(Header);
