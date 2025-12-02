import axios from "axios";

// URL base da API — pode ser definida via variável de ambiente (.env)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api",
});


export async function uploadIrisImage(file: File) {
  const formData = new FormData();
  formData.append("image", file);

  const response = await api.post("/iris/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

/**
 * Busca o histórico de análises realizadas
 */
export async function fetchAnalyses() {
  const response = await api.get("/analises");
  return response.data;
}

/**
 * Busca uma análise específica por ID
 */
export async function fetchAnalysisById(id: number) {
  const response = await api.get(`/analises/${id}`);
  return response.data;
}

export default api;
