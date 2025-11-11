import * as tf from "@tensorflow/tfjs-node";
import fs from "fs";
import path from "path";
import sharp from "sharp";

let model: tf.GraphModel | null = null;

/**
 * Carrega o modelo TensorFlow.js do diretório local, se ainda não estiver carregado.
 */
const loadModel = async (): Promise<tf.GraphModel> => {
  if (!model) {
    const modelPath = path.join(__dirname, "../../../ml/models/model.json");
    if (!fs.existsSync(modelPath)) {
      throw new Error("Modelo TensorFlow.js não encontrado em /ml/models.");
    }
    model = await tf.loadGraphModel(`file://${modelPath}`);
    console.log("✅ Modelo TensorFlow.js carregado na memória.");
  }
  return model;
};

/**
 * Função de predição da íris.
 * @param imagePath Caminho da imagem enviada
 */
export const predictIris = async (imagePath: string): Promise<any> => {
  try {
    const model = await loadModel();

    // Pré-processamento da imagem
    const imageBuffer = fs.readFileSync(imagePath);
    const processed = await sharp(imageBuffer)
      .resize(224, 224)
      .toFormat("png")
      .toBuffer();

    const tensor = tf.node.decodeImage(processed)
      .expandDims(0)
      .toFloat()
      .div(tf.scalar(255));

    // P
