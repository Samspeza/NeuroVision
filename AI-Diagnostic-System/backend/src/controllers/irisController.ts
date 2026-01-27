import * as tf from "@tensorflow/tfjs";
import fs from "fs";
import path from "path";
import sharp from "sharp";

let model: tf.GraphModel | null = null;

const loadModel = async (): Promise<tf.GraphModel> => {
  if (!model) {
    const modelPath = path.join(__dirname, "../../../ml/models/model.json");
    if (!fs.existsSync(modelPath)) {
      throw new Error("Modelo TensorFlow.js não encontrado em /ml/models.");
    }
    model = await tf.loadGraphModel(`file://${modelPath}`);
    console.log(" Modelo TensorFlow.js carregado na memória.");
  }
  return model;
};

export const predictIris = async (imagePath: string): Promise<any> => {
  const model = await loadModel();

  const { data, info } = await sharp(fs.readFileSync(imagePath))
    .resize(224, 224)
    .removeAlpha()       
    .raw()             
    .toBuffer({ resolveWithObject: true });

  const imageTensor = tf.tensor3d(
    new Uint8Array(data),
    [info.height, info.width, info.channels],
    "int32"
  );

  const inputTensor = imageTensor
    .expandDims(0)
    .toFloat()
    .div(tf.scalar(255));

  const prediction = model.predict(inputTensor) as tf.Tensor;

  const result = await prediction.array();

  imageTensor.dispose();
  inputTensor.dispose();
  prediction.dispose();

  return result;
};