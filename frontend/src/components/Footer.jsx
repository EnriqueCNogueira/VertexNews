import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-dark-blue text-white py-8 px-4 mt-12" role="contentinfo">
      <div className="max-w-7xl mx-auto text-center">
        <p className="text-white text-base mb-2">
          Desenvolvido por Enrique Nogueira
        </p>
        <p className="text-blue-200 text-sm">
          © 2025 Site para portfolio pessoal. Todos os direitos reservados.
        </p>
      </div>
    </footer>
  );
};

export default React.memo(Footer);
