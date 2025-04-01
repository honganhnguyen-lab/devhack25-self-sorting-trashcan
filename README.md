# Devhack25-self-sorting-trashcan

## Inspiration
The growing waste crisis inspired us to create an AI-powered automated waste sorting system. With over 2 billion tons of waste generated annually, improper disposal remains a major issue. While education helps, human error is inevitable. We wanted to build a solution that makes waste sorting accurate, efficient, and effortless.

## What It Does
SORT DESU NE uses AI image recognition to classify waste in real time and directs it into the correct bin using automated mechanical sorting. This reduces human error and ensures proper waste disposal in homes, public spaces, and institutions.

## How We Built It
AI Model: Trained on a dataset of various waste categories for accurate classification. Model based on pytorch 2.6.0 with ResNet18 model. Then we save as an ONNX format model to run in a low performance windows devices.
Hardware: Stepper motors (NEMA 17) controlled via TB6600 drivers to automate sorting.
Software: AI inference integrated with real-time mechanical control for seamless operation. Go through socket module to communicate model result and motor control signals. We also use Flask to build up our simple website to demo live detection result. 
Frameworks & Tools: Python, OpenCV for image recognition, and microcontroller-based motor control.

## Challenges We Ran Into
Dataset Limitations: Finding a diverse dataset for AI training.
Hardware Integration: Synchronizing AI outputs with motor movements.
Sorting Speed: Optimizing response time for real-world usability.

## Accomplishments That We're Proud Of
Successfully trained an AI model to distinguish waste types.
Developed a functional prototype with real-time automated sorting.
Built an end-to-end system integrating AI, hardware, and software.


![Screenshot 2025-03-31 171434](https://github.com/user-attachments/assets/f1bcbe54-adc3-42fc-9447-387dc741d936)
<small>Streaming and detection result on demo page.</small>
