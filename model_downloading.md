# 🧠 Brain Tumor Detection Model (Docker Hosted)

This Docker image (`mrzikomo/brain-tumore-api`) hosts a pre-trained **Keras/TensorFlow model (`best_model.h5`)** using **FastAPI**.  
It allows developers to easily **download the model** from Docker Hub and integrate it into their own backend.

---

## 🚀 Step 1: Pull the Docker Image

Pull the pre-built image from Docker Hub:

docker pull mrzikomo/brain-tumore-api:latest

## 🏃 Step 2: Run the Container

Run the API server locally:


docker run -d -p 8000:8000 mrzikomo/brain-tumore-api:latest


## Step 3: Access the API

Open your browser and go to:


## Step 4: Download the Model File

Now, download the model (best_model.h5) from the container.

Option 1 – Browser:

## Step 5: Save the Model in Your Project

After downloading, move or copy the model into your backend project folder:

## Step 6: Use the Model in Your Backend Code

Example usage in Python:

```bash