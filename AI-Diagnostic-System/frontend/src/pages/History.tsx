import React, { useEffect, useState } from "react";
import { fetchAnalyses, fetchAnalysisById } from "../services/api";

interface Analysis {
  id: number;
  patient_name?: string;
  diagnosis: string;
  accuracy: number;
  created_at: string;
  image_url?: string;
}

const History: React.FC = () => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [selected, setSelected] = useState<Analysis | null>(null);

  useEffect(() => {
    async function loadData() {
      const data = await fetchAnalyses();
      setAnalyses(data);
    }
    loadData();
  }, []);

  const openDetails = async (id: number) => {
    const data = await fetchAnalysisById(id);
    setSelected(data);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-6 text-primary">
        Histórico de Análises
      </h2>

      <div className="grid gap-4">
        {analyses.map((item) => (
          <div
            key={item.id}
            onClick={() => openDetails(item.id)}
            className="p-4 bg-white shadow-sm rounded-xl hover:shadow-md transition cursor-pointer"
          >
            <div className="flex justify-between items-center">
              <p className="font-medium">
                {item.patient_name || "Paciente não identificado"}
              </p>
              <span className="text-sm text-gray-500">
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>
            <p className="text-gray-700 mt-2">
              Diagnóstico:{" "}
              <span className="font-semibold text-primary">
                {item.diagnosis}
              </span>{" "}
              — Precisão: {(item.accuracy * 100).toFixed(2)}%
            </p>
          </div>
        ))}
      </div>

      {selected && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-[90%] max-w-md shadow-lg relative">
            <button
              onClick={() => setSelected(null)}
              className="absolute top-2 right-3 text-gray-500 hover:text-red-500"
            >
              ✕
            </button>

            <h3 className="text-xl font-semibold text-primary mb-4">
              Detalhes da Análise
            </h3>

            {selected.image_url && (
              <img
                src={selected.image_url}
                alt="Íris analisada"
                className="rounded-xl mb-4"
              />
            )}

            <p>
              <strong>Diagnóstico:</strong> {selected.diagnosis}
            </p>
            <p>
              <strong>Precisão:</strong>{" "}
              {(selected.accuracy * 100).toFixed(2)}%
            </p>
            <p>
              <strong>Data:</strong>{" "}
              {new Date(selected.created_at).toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
