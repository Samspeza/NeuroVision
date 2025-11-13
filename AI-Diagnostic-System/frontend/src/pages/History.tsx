import React, { useEffect, useState } from "react";
import { fetchAnalyses } from "../services/api";

interface Analise {
  id: number;
  nomeArquivo: string;
  resultado: string;
  probabilidade: number;
  criadoEm: string;
}

const History: React.FC = () => {
  const [analises, setAnalises] = useState<Analise[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchAnalyses();
        setAnalises(data);
      } catch (err) {
        console.error(err);
        setError("Falha ao carregar histórico de análises.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen text-primary">
        Carregando histórico...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto bg-surface shadow-soft rounded-2xl p-6">
        <h1 className="text-2xl font-bold text-primary mb-4 text-center">
          Histórico de Análises Iridológicas
        </h1>

        {analises.length === 0 ? (
          <p className="text-center text-gray-600">
            Nenhuma análise registrada até o momento.
          </p>
        ) : (
          <table className="w-full border-collapse mt-4">
            <thead>
              <tr className="bg-gray-100 text-left">
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-3">Arquivo</th>
                <th className="py-2 px-3">Resultado</th>
                <th className="py-2 px-3">Probabilidade</th>
                <th className="py-2 px-3">Data</th>
              </tr>
            </thead>
            <tbody>
              {analises.map((a) => (
                <tr
                  key={a.id}
                  className="border-b hover:bg-gray-50 transition"
                >
                  <td className="py-2 px-3 text-gray-700">{a.id}</td>
                  <td className="py-2 px-3 text-gray-700">{a.nomeArquivo}</td>
                  <td className="py-2 px-3 font-semibold text-primary">
                    {a.resultado}
                  </td>
                  <td className="py-2 px-3 text-gray-700">
                    {(a.probabilidade * 100).toFixed(2)}%
                  </td>
                  <td className="py-2 px-3 text-gray-600">
                    {new Date(a.criadoEm).toLocaleString("pt-BR")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default History;
