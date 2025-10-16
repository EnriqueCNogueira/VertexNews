import React, { useState, useEffect, useCallback } from 'react';
import './styles/App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import NewsGrid from './components/NewsGrid';
import NewsModal from './components/NewsModal';
import { getNews, getApiStatus } from './services/api';

function App() {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState({ online: false, status: 'offline' });
  const [error, setError] = useState(null);
  const [selectedNews, setSelectedNews] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadNews = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const newsData = await getNews(15);
      
      if (newsData.success) {
        setNews(newsData.data);
      } else {
        setError('Erro ao carregar notícias');
      }
    } catch (err) {
      console.error('Erro ao carregar notícias:', err);
      setError('Erro ao carregar notícias');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const checkApiStatus = useCallback(async () => {
    try {
      const status = await getApiStatus();
      setApiStatus(status);
    } catch (err) {
      console.error('Erro ao verificar status da API:', err);
      setApiStatus({ online: false, status: 'offline' });
    }
  }, []);

  useEffect(() => {
    loadNews();
    checkApiStatus();
  }, [loadNews, checkApiStatus]);

  const handleNewsClick = useCallback((newsItem) => {
    setSelectedNews(newsItem);
    setIsModalOpen(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setSelectedNews(null);
  }, []);

  return (
    <div className="min-h-screen bg-stone-100">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8" role="main">
        {/* Status da API */}
        <div className="mb-6">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            apiStatus.online 
              ? 'bg-green-100 text-green-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`} role="status" aria-live="polite">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              apiStatus.online ? 'bg-green-500' : 'bg-yellow-500'
            }`} aria-hidden="true"></div>
            {apiStatus.online ? 'API Online' : 'Modo Offline'}
          </div>
          {!apiStatus.online && (
            <p className="text-sm text-gray-600 mt-2">
              Exibindo dados de exemplo. Conecte-se à API para dados em tempo real.
            </p>
          )}
        </div>

        {/* Mensagem de Erro */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6" role="alert" aria-live="assertive">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Grid de Notícias */}
        <NewsGrid news={news} isLoading={isLoading} onNewsClick={handleNewsClick} />

        {/* Modal de Notícia */}
        <NewsModal 
          news={selectedNews} 
          isOpen={isModalOpen} 
          onClose={handleCloseModal} 
        />

      </main>

      <Footer />
    </div>
  );
}

export default App;
