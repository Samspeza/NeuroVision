import React, { useCallback, useState } from "react";
import { uploadIrisImage } from "../services/api";

interface PredictionResult {
  classification?: string;
  confidence: number;
}

const Home: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const resetFeedback = () => {
    setResult(null);
    setError(null);
  };

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (!selectedFile) return;

      setFile(selectedFile);
      resetFeedback();
    },
    []
  );

  const handleUpload = useCallback(async () => {
    if (!file) {
      setError("Selecione uma imagem para enviar.");
      return;
    }

    try {
      setLoading(true);
      resetFeedback();

      const response = await uploadIrisImage(file);
      setResult(response.prediction);
    } catch (err) {
      console.error(err);
      setError("Falha ao processar a imagem. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="bg-surface shadow-soft rounded-2xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-primary mb-4 text-center">
          Diagnóstico Iridológico Automatizado
        </h1>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-600 mb-4"
        />

        <button
          onClick={handleUpload}
          disabled={loading}
          className="bg-primary text-white font-medium px-4 py-2 rounded-xl w-full hover:bg-secondary transition disabled:opacity-60"
        >
          {loading ? "Processando..." : "Enviar para Análise"}
        </button>

        {error && (
          <p className="text-red-500 text-sm text-center mt-3">{error}</p>
        )}

        {result && (
          <div className="mt-6 bg-gray-50 rounded-xl p-4 text-center">
            <h2 className="font-semibold text-lg text-primary mb-2">
              Resultado do Diagnóstico
            </h2>

            <p className="text-gray-700 mb-2">
              <strong>Classificação:</strong>{" "}
              {result.classification || "—"}
            </p>

            <p className="text-gray-700">
              <strong>Probabilidade:</strong>{" "}
              {(result.confidence * 100).toFixed(2)}%
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
