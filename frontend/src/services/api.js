import axios from 'axios';

// Configuração base da API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Instância do Axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dados mock para funcionamento offline (ordenados por score decrescente)
const mockNewsData = {
  success: true,
  data: [
    {
      id: 3,
      titulo: "Inteligência Artificial no Marketing: Casos de Sucesso",
      link: "https://exemplo.com/ia-marketing-casos",
      imagem: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=250&fit=crop",
      resumo: "Conheça empresas que estão usando IA para revolucionar suas estratégias de marketing e obter resultados impressionantes.",
      fonte: "Mundo do Marketing",
      score: 4.8,
      status: "postada"
    },
    {
      id: 6,
      titulo: "Analytics Avançado: Métricas que Realmente Importam",
      link: "https://exemplo.com/analytics-metricas-importantes",
      imagem: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=250&fit=crop",
      resumo: "Descubra quais métricas você deve acompanhar para tomar decisões mais inteligentes no seu marketing.",
      fonte: "Meio & Mensagem",
      score: 4.6,
      status: "postada"
    },
    {
      id: 1,
      titulo: "Tendências de Marketing Digital para 2024",
      link: "https://exemplo.com/marketing-digital-2024",
      imagem: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=250&fit=crop",
      resumo: "Descubra as principais tendências que vão moldar o marketing digital em 2024, incluindo IA, automação e personalização.",
      fonte: "Exame",
      score: 4.5,
      status: "postada"
    },
    {
      id: 5,
      titulo: "Marketing de Conteúdo: Criando Narrativas que Vendem",
      link: "https://exemplo.com/marketing-conteudo-narrativas",
      imagem: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=250&fit=crop",
      resumo: "Aprenda como criar conteúdo que não apenas informa, mas também converte visitantes em clientes.",
      fonte: "Exame",
      score: 4.3,
      status: "postada"
    },
    {
      id: 2,
      titulo: "Como o E-commerce Está Revolucionando as Vendas",
      link: "https://exemplo.com/ecommerce-revolucao",
      imagem: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=250&fit=crop",
      resumo: "Análise completa sobre como as plataformas de e-commerce estão transformando o cenário de vendas online.",
      fonte: "Meio & Mensagem",
      score: 4.2,
      status: "postada"
    },
    {
      id: 4,
      titulo: "Redes Sociais: Estratégias para Engajamento",
      link: "https://exemplo.com/redes-sociais-engajamento",
      imagem: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=250&fit=crop",
      resumo: "Dicas práticas para aumentar o engajamento nas redes sociais e construir uma comunidade forte.",
      fonte: "GKPB",
      score: 4.0,
      status: "postada"
    }
  ],
  total: 6,
  cached: false,
  timestamp: new Date().toISOString()
};

// Função para verificar se a API está online
const isApiOnline = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 3000 });
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

// Função para buscar notícias
export const getNews = async (limit = 15) => {
  try {
    console.log('Fazendo requisição para a API...');
    const response = await api.get('/news', {
      params: { limit }
    });
    console.log('Dados da API recebidos:', response.data.data.map(n => ({ score: n.score, titulo: n.titulo.substring(0, 30) })));
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar notícias da API:', error);
    // Em caso de erro, retorna dados mock ordenados por score decrescente
    console.log('Usando dados mock devido ao erro');
    return {
      ...mockNewsData,
      data: mockNewsData.data.slice(0, limit)
    };
  }
};

// Função para buscar uma notícia específica por ID
export const getNewsById = async (id) => {
  try {
    const online = await isApiOnline();
    
    if (online) {
      const response = await api.get(`/news/${id}`);
      return response.data;
    } else {
      // Busca nos dados mock
      const newsItem = mockNewsData.data.find(item => item.id === parseInt(id));
      if (newsItem) {
        return {
          success: true,
          data: [newsItem],
          total: 1,
          cached: false,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error('Notícia não encontrada');
      }
    }
  } catch (error) {
    console.error('Erro ao buscar notícia por ID:', error);
    throw error;
  }
};

// Função para verificar status da API
export const getApiStatus = async () => {
  try {
    const response = await api.get('/health');
    return {
      online: true,
      status: response.data.status,
      version: response.data.version,
      database_connected: response.data.database_connected
    };
  } catch (error) {
    return {
      online: false,
      status: 'offline',
      version: '1.0.0',
      database_connected: false
    };
  }
};

export default api;
