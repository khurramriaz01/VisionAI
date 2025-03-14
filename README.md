# VisionAI: AI That Sees, Listens, and Assists.

![Demo Image](demo.png)

## Introduction
VisionAI is an AI-powered software solution that seamlessly integrates speech recognition, computer vision, and natural language processing to enhance user interactions. Designed to process voice and image inputs from any connected camera and microphone, the system leverages the Gemini API to generate AI-driven responses, which are delivered through high-quality synthesized speech. This technology aims to improve accessibility, efficiency, and user experience across various applications.

## Features
- **Speech Recognition:** Converts spoken language into text using Google's Speech Recognition API.
- **Computer Vision:** Captures and analyzes images using OpenCV and the Gemini API.
- **Natural Language Processing:** Generates AI-driven responses using the Gemini API.
- **Text-to-Speech:** Converts AI-generated text into natural-sounding speech using pyttsx3.
- **Real-time Processing:** Provides instant responses through a user-friendly interface.
- **Interactive GUI:** Built with Tkinter for seamless user interaction.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- pip package manager
- Webcam and Microphone enabled on your device

### Dependencies
Install the required dependencies using:
```sh
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key:
```sh
GEMINI_API_KEY=your_api_key_here
```

## Usage
Run the application using:
```sh
python visionai.py
```

### How It Works
1. The system starts and initializes the camera and microphone.
2. The user speaks a command or query.
3. Speech is converted into text and analyzed by the Gemini AI.
4. The system captures an image (if necessary) and processes visual context.
5. AI generates a response based on the input data.
6. The response is displayed in the chat panel and spoken aloud.

## Future Enhancements
- **Multi-Language Support:** Expanding speech recognition and synthesis for global users.
- **Cloud Integration:** Storing and retrieving data from cloud services.
- **Gesture Recognition:** Enhancing user experience through hand gesture commands.

## Contributors
- **Khurram Riaz Bhutto** *(Project Developer)*

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

