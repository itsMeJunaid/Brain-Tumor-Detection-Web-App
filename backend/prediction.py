# import tensorflow as tf
# import numpy as np
# import cv2
# from tensorflow.keras.applications.resnet50 import preprocess_input
# from PIL import Image
# import io
# import os

# MODEL_PATH = "model/best_model.h5"
# model = None

# def load_model():
#     global model
#     if model is None:
#         model = tf.keras.models.load_model(MODEL_PATH)
#     return model

# def make_gradcam_heatmap(img_array, model, last_conv_layer_name):
#     # Use the model input as-is to match the expected structure
#     grad_model = tf.keras.models.Model(
#         inputs=model.inputs,  # <-- use model.inputs (supports nested inputs)
#         outputs=[model.get_layer(last_conv_layer_name).output, model.output]
#     )

#     with tf.GradientTape() as tape:
#         conv_outputs, predictions = grad_model(img_array, training=False)
        
#         # If predictions is a list, take the first output
#         if isinstance(predictions, list):
#             predictions = predictions[0]

#         pred_index = tf.argmax(predictions[0])
#         class_channel = predictions[:, pred_index]

#     grads = tape.gradient(class_channel, conv_outputs)
#     pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

#     conv_outputs = conv_outputs[0]
#     heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)
#     heatmap = np.maximum(heatmap, 0)

#     # Convert to NumPy safely
#     if isinstance(heatmap, tf.Tensor):
#         heatmap = heatmap.numpy()
    
#     heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1.0
#     return heatmap

# def find_last_conv_layer(model):
#     # Try to find base model if it exists
#     base_model = None
#     for layer in model.layers:
#         if isinstance(layer, tf.keras.Model):
#             base_model = layer
#             break
#     if base_model is None:
#         base_model = model
    
#     for layer in reversed(base_model.layers):
#         if isinstance(layer, tf.keras.layers.Conv2D):
#             return layer.name, base_model
    
#     raise ValueError("No convolutional layer found for Grad-CAM!")

# async def predict_brain_tumor(image_bytes: bytes, save_path: str, gradcam_path: str):
#     loaded_model = load_model()

#     # Save uploaded image
#     img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     img = img.resize((224, 224))
#     img.save(save_path)

#     # Preprocess for prediction
#     img_array = np.array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array = preprocess_input(img_array.astype(np.float32))

#     # Prediction
#     preds = loaded_model.predict(img_array, verbose=0)
#     conf = float(preds[0][0])
#     label = "Tumor" if conf > 0.5 else "No Tumor"
#     conf_pct = conf * 100 if conf > 0.5 else (1 - conf) * 100

#     # Grad-CAM
#     try:
#         last_conv_layer_name, base_model = find_last_conv_layer(loaded_model)
#         heatmap = make_gradcam_heatmap(img_array, base_model, last_conv_layer_name)

#         img_orig = cv2.imread(save_path)
#         img_orig = cv2.resize(img_orig, (224, 224))

#         heatmap_resized = cv2.resize(heatmap, (img_orig.shape[1], img_orig.shape[0]))
#         heatmap_resized = np.uint8(255 * heatmap_resized)
#         heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
#         superimposed = cv2.addWeighted(img_orig, 0.6, heatmap_colored, 0.4, 0)

#         cv2.imwrite(gradcam_path, superimposed)
#     except Exception as e:
#         print(f"Grad-CAM generation failed: {str(e)}")
#         import shutil
#         shutil.copy(save_path, gradcam_path)

#     return label, conf_pct


import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image
import io
import os
import shutil

MODEL_PATH = "model/best_model.h5"
model = None

def load_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
    return model

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, tumor=True):
    """
    Generates Grad-CAM heatmap.
    tumor=True  -> Tumor detected
    tumor=False -> No Tumor
    """
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array, training=False)
        if isinstance(predictions, list):
            predictions = predictions[0]

        # Binary classification
        if tumor:
            class_channel = predictions[:, 0]      # Tumor
        else:
            class_channel = 1 - predictions[:, 0]  # No Tumor

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    heatmap = np.maximum(heatmap, 0)

    if isinstance(heatmap, tf.Tensor):
        heatmap = heatmap.numpy()

    heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1.0
    return heatmap

def find_last_conv_layer(model):
    base_model = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):
            base_model = layer
            break
    if base_model is None:
        base_model = model
    
    for layer in reversed(base_model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return layer.name, base_model
    
    raise ValueError("No convolutional layer found for Grad-CAM!")

async def predict_brain_tumor(image_bytes: bytes, save_path: str, gradcam_path: str):
    loaded_model = load_model()

    # Save uploaded image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img.save(save_path)

    # Preprocess for prediction
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array.astype(np.float32))

    # Prediction
    preds = loaded_model.predict(img_array, verbose=0)
    conf = float(preds[0][0])
    tumor_flag = conf > 0.5
    label = "Tumor Detected" if tumor_flag else "No Tumor Detected"
    conf_pct = conf * 100 if tumor_flag else (1 - conf) * 100

    # Grad-CAM
    try:
        last_conv_layer_name, base_model = find_last_conv_layer(loaded_model)
        heatmap = make_gradcam_heatmap(img_array, base_model, last_conv_layer_name, tumor=tumor_flag)

        img_orig = cv2.imread(save_path)
        img_orig = cv2.resize(img_orig, (224, 224))

        if tumor_flag:
            # Normal Grad-CAM overlay
            heatmap_resized = cv2.resize(heatmap, (img_orig.shape[1], img_orig.shape[0]))
            heatmap_resized = np.uint8(255 * heatmap_resized)
            heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
            superimposed = cv2.addWeighted(img_orig, 0.6, heatmap_colored, 0.4, 0)
        else:
            # Minimal overlay for No Tumor
            superimposed = img_orig.copy()

        # Add label text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(superimposed, label, (10, 25), font, 0.8, (0, 255, 0) if not tumor_flag else (0,0,255), 2)

        cv2.imwrite(gradcam_path, superimposed)

    except Exception as e:
        print(f"Grad-CAM generation failed: {str(e)}")
        shutil.copy(save_path, gradcam_path)

    return label, conf_pct
