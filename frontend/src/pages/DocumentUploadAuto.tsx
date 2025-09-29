import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const DocumentUploadAuto = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto"></div>
          <p className="text-black text-sm">Carregando documentos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="bg-white border border-black rounded-lg p-6 max-w-sm w-full text-center">
          <h2 className="text-lg font-semibold text-black mb-2">Erro</h2>
          <p className="text-gray-600 mb-4">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-white border-b border-black">
        <div className="px-4 py-4 sm:py-6">
          <h1 className="text-xl font-semibold text-black">Upload de Documentos</h1>
          <p className="text-gray-600">Teste de estrutura</p>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadAuto;