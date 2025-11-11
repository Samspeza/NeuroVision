import * as tf from "@tensorflow/tfjs-node";
import fs from "fs";
import path from "path";
import sharp from "sharp";

/**
 * Carrega o modelo TensorFlow salvo no formato H5 ou TFJS.
 * @param modelPath Caminho absoluto até o modelo.
 */
export async function loadModel(modelPath: string): Promise<tf.LayersModel> {
  try {
    if (!fs.existsSync(modelPath)) {
      throw new Error(`Modelo não encontrado em: ${modelPath}`);
    }

    const ext = path.extname(modelPath);
    let model: tf.LayersModel;

    if (ext === ".h5") {
      model = await tf.loadLayersModel(`file://${modelPath}`);
    } else {
      model = await tf.loadLayersModel(`file://${modelPath}/model.json`);
    }

    console.log("✅ Modelo carregado com sucesso:", modelPath);
    return model;
  } catch (error) {
    console.error("❌ Falha ao carregar modelo:", error);
    throw error;
  }
}

/**
 * Realiza pré-processamento da imagem para entrada do modelo.
 * @param imagePath Caminho da imagem recebida via upload.
 * @param imgSize Tamanho padrão de entrada da rede (ex: 224x224).
 */
async function preprocessImage(imagePath: string, imgSize = 224): Promise<tf.Tensor4D> {
  const buffer = await sharp(imagePath)
    .resize(imgSize, imgSize)
    .removeAlpha()
    .toColourspace("rgb")
    .toBuffer();

  const imageTensor = tf.node.decodeImage(buffer, 3)
    .expandDims(0)
    .div(255.0) as tf.Tensor4D;

  return imageTensor;
}

/**
 * Executa a inferência no modelo carregado.
 * @param model Modelo TensorFlow previamente carregado.
 * @param imagePath Caminho da imagem a ser analisada.
 * @returns Resultado da predição e probabilidades.
 */
export async function predictImage(model: tf.LayersModel, imagePath: string) {
  try {
    const inputTensor = await preprocessImage(imagePath);
    const predictions = model.predict(inputTensor) as tf.Tensor;
    const data = await predictions.data();

    const result = {
      rawOutput: Array.from(data),
      predictedClass: data.indexOf(Math.max(...data)),
      confidence: Math.max(...data)
    };

    console.log("🧩 Predição concluída:", result);
    return result;
  } catch (error) {
    console.error("Erro ao realizar predição:", error);
    throw error;
  }
}
