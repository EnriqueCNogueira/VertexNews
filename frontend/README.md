# VertexNews Frontend

Frontend React para o sistema VertexNews - Sistema inteligente de notícias de marketing.

## 🚀 Características

- **Interface Moderna**: Design responsivo com Tailwind CSS
- **Funcionamento Offline**: Dados mock para demonstração sem API
- **Cards Interativos**: Expansão de notícias com resumos completos
- **Sistema de Pontuação**: Visualização com estrelas (1-5)
- **Status da API**: Indicador visual de conexão online/offline
- **Responsivo**: Adaptável para desktop, tablet e mobile

## 🛠️ Tecnologias

- **React 18** - Framework frontend
- **Tailwind CSS** - Framework de estilos
- **Axios** - Cliente HTTP para API
- **Create React App** - Ferramenta de build

## 📁 Estrutura do Projeto

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Cabeçalho da aplicação
│   │   ├── NewsCard.jsx        # Card individual de notícia
│   │   ├── NewsGrid.jsx        # Grid responsivo de notícias
│   │   ├── Footer.jsx          # Rodapé da aplicação
│   │   └── ReloadButton.jsx    # Botão de recarregar
│   ├── services/
│   │   └── api.js              # Serviço de API com dados mock
│   ├── styles/
│   │   └── App.css             # Estilos globais + Tailwind
│   ├── App.jsx                 # Componente principal
│   └── index.js                # Ponto de entrada
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## 🎨 Design

### Cores
- **Header/Footer**: Azul escuro (`#1e3a8a`)
- **Background**: Cinza claro (`#f3f4f6`)
- **Cards**: Branco com sombras
- **Acentos**: Azul e amarelo para estrelas

### Layout
- **Header**: Logo + título + informações
- **Grid**: 2x3 cards responsivo (1 col mobile, 2 tablet, 3 desktop)
- **Footer**: Informações sobre o sistema
- **Cards**: Imagem + estrelas + fonte + título + resumo expansível

## 🔧 Instalação e Execução

### Pré-requisitos
- Node.js 16+ 
- npm ou yarn

### Passos

1. **Instalar dependências**:
   ```bash
   cd frontend
   npm install
   ```

2. **Executar em desenvolvimento**:
   ```bash
   npm start
   ```
   A aplicação abrirá em `http://localhost:3000`

3. **Build para produção**:
   ```bash
   npm run build
   ```

## 🌐 Funcionamento Offline

O frontend funciona completamente offline usando dados mock:

- **6 notícias de exemplo** com dados realistas
- **Imagens do Unsplash** para demonstração
- **Sistema de pontuação** funcional (1-5 estrelas)
- **Indicador visual** de status offline

### Dados Mock Incluídos
- Tendências de Marketing Digital 2024
- E-commerce e vendas online
- Inteligência Artificial no Marketing
- Redes Sociais e Engajamento
- Marketing de Conteúdo
- Analytics Avançado

## 🔌 Integração com API

### Endpoints Utilizados
- `GET /api/v1/news` - Lista notícias
- `GET /api/v1/news/{id}` - Notícia específica
- `GET /api/v1/health` - Status da API

### Formato dos Dados
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "titulo": "Título da Notícia",
      "link": "https://exemplo.com",
      "imagem": "https://imagem.jpg",
      "resumo": "Resumo da notícia...",
      "fonte": "Nome da Fonte",
      "score": 4.5,
      "status": "postada"
    }
  ],
  "total": 6,
  "cached": false,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 📱 Funcionalidades

### Cards de Notícias
- **Clique para expandir**: Mostra resumo completo
- **Botão "Ler Notícia"**: Abre link em nova aba
- **Sistema de estrelas**: Visualização da pontuação
- **Imagens responsivas**: Fallback para imagens quebradas

### Interface
- **Status da API**: Indicador online/offline
- **Botão Reload**: Recarrega dados da API
- **Loading states**: Skeleton loading durante carregamento
- **Error handling**: Tratamento de erros com fallback

### Responsividade
- **Mobile**: 1 coluna
- **Tablet**: 2 colunas  
- **Desktop**: 3 colunas
- **Breakpoints**: Tailwind CSS padrão

## 🎯 Como Usar

1. **Visualizar Notícias**: Cards são exibidos automaticamente
2. **Expandir Card**: Clique em qualquer card para ver resumo completo
3. **Ler Notícia**: Clique no botão "Ler Notícia Completa"
4. **Recarregar**: Use o botão "Recarregar Notícias"
5. **Status**: Observe o indicador de conexão com a API

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na pasta `frontend/`:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Proxy
O `package.json` já inclui proxy para desenvolvimento:
```json
"proxy": "http://localhost:8000"
```

## 🚀 Deploy

### Build de Produção
```bash
npm run build
```

### Servir Build Localmente
```bash
npx serve -s build
```

### Deploy em Netlify/Vercel
1. Conecte o repositório
2. Configure build command: `npm run build`
3. Configure publish directory: `build`
4. Deploy automático

## 📊 Performance

- **Lazy Loading**: Imagens carregam sob demanda
- **Error Boundaries**: Tratamento de erros React
- **Optimized Images**: Imagens do Unsplash otimizadas
- **Minimal Bundle**: Apenas dependências necessárias

## 🐛 Troubleshooting

### Problemas Comuns

1. **API não conecta**: Verifique se a API está rodando na porta 8000
2. **Imagens não carregam**: Fallback automático para imagem padrão
3. **Estilos não aplicam**: Execute `npm install` novamente
4. **Build falha**: Verifique versão do Node.js (16+)

### Logs
- Console do navegador mostra erros de API
- Network tab mostra requisições HTTP
- React DevTools para debug de componentes

## 📝 Licença

Este projeto é parte do sistema VertexNews e segue as mesmas diretrizes de licenciamento.

## 🤝 Contribuição

Para contribuir com o frontend:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**VertexNews Frontend** - Sistema inteligente de notícias de marketing
