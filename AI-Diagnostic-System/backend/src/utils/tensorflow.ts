import * as tf from "@tensorflow/tfjs-node";
import fs from "fs";
import path from "path";
import sharp from "sharp";

/* =====================================================
 * Tipagens e Interfaces
 * ===================================================== */

export interface ModelConfig {
  inputSize: number;
  normalize: boolean;
  mean?: number[];
  std?: number[];
}

export interface PredictionResult {
  rawOutput: number[];
  predictedClass: number;
  confidence: number;
}

export interface ImagePreprocessOptions {
  inputSize: number;
  normalize: boolean;
  mean?: number[];
  std?: number[];
}

function validateFileExists(filePath: string, errorMessage: string): void {
  if (!fs.existsSync(filePath)) {
    throw new Error(errorMessage);
  }
}

function softmax(logits: number[]): number[] {
  const maxLogit = Math.max(...logits);
  const exps = logits.map(v => Math.exp(v - maxLogit));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map(v => v / sum);
}

export async function loadModel(
  modelPath: string
): Promise<tf.LayersModel> {
  validateFileExists(modelPath, `Modelo não encontrado: ${modelPath}`);

  const ext = path.extname(modelPath);
  let modelUri: string;

  if (ext === ".h5") {
    modelUri = `file://${modelPath}`;
  } else {
    validateFileExists(
      path.join(modelPath, "model.json"),
      `model.json não encontrado em: ${modelPath}`
    );
    modelUri = `file://${modelPath}/model.json`;
  }

  const model = await tf.loadLayersModel(modelUri);
  model.summary();

  console.log(" Modelo carregado com sucesso:", modelUri);
  return model;
}

async function preprocessImage(
  imagePath: string,
  options: ImagePreprocessOptions
): Promise<tf.Tensor4D> {
  validateFileExists(imagePath, `Imagem não encontrada: ${imagePath}`);

  const { inputSize, normalize, mean, std } = options;

  const buffer = await sharp(imagePath)
    .resize(inputSize, inputSize, { fit: "cover" })
    .removeAlpha()
    .toColourspace("rgb")
    .raw()
    .toBuffer();

  let tensor = tf.tensor3d(
    new Uint8Array(buffer),
    [inputSize, inputSize, 3]
  ).expandDims(0);

  tensor = tensor.toFloat();

  if (normalize) {
    if (mean && std) {
      const meanTensor = tf.tensor(mean).reshape([1, 1, 1, 3]);
      const stdTensor = tf.tensor(std).reshape([1, 1, 1, 3]);
      tensor = tensor.sub(meanTensor).div(stdTensor);
    } else {
      tensor = tensor.div(255.0);
    }
  }

  return tensor as tf.Tensor4D;
}

export async function predictImage(
  model: tf.LayersModel,
  imagePath: string,
  config: ModelConfig
): Promise<PredictionResult> {
  let inputTensor: tf.Tensor4D | null = null;
  let outputTensor: tf.Tensor | null = null;

  try {
    inputTensor = await preprocessImage(imagePath, {
      inputSize: config.inputSize,
      normalize: config.normalize,
      mean: config.mean,
      std: config.std
    });

    outputTensor = model.predict(inputTensor) as tf.Tensor;

    const raw = Array.from(await outputTensor.data());
    const probabilities = softmax(raw);

    const confidence = Math.max(...probabilities);
    const predictedClass = probabilities.indexOf(confidence);

    const result: PredictionResult = {
      rawOutput: probabilities,
      predictedClass,
      confidence
    };

    console.log("🧠 Inferência finalizada:", result);
    return result;
  } finally {
    inputTensor?.dispose();
    outputTensor?.dispose();
  }
}
