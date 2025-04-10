# Real-Time Sign Language Alphabet Detection System

This is a web-based interactive interface for a real-time sign language alphabet detection AI system. The application uses a webcam feed to detect and translate American Sign Language (ASL) alphabet gestures into text.

## Features

- Interactive web interface with modern UI design
- Real-time webcam integration
- Visual feedback of detected alphabet letters with corresponding sign images
- Hover preview of sign language gestures for each alphabet letter
- Complete A-Z alphabet detection with visual examples
- Responsive design that works on both desktop and mobile devices
- Dark mode support with user preference saving
- Automatic theme detection based on system preferences

## Project Structure

- `index.html` - Landing page with alphabet display and hover preview functionality
- `detection.html` - Main application page with webcam integration and sign detection
- `styles.css` - External stylesheet for both pages with theme support
- `images/signs/` - Directory containing sign language alphabet images

## How It Works

1. The user navigates to the landing page where they can see all alphabet letters
2. Hovering over any letter shows a preview of the corresponding sign language gesture
3. Clicking "Start Detection" navigates to the detection page
4. The detection page requests webcam access
5. Once granted, the webcam feed is displayed on the left side
6. The AI system (simulated in this demo) detects sign language alphabet gestures
7. Detected letters appear on the right panel along with their sign language images

## Image Preview Functionality

- Hover over any letter on the home page to see the ASL sign
- The preview displays in a tooltip above the letter
- Each detected letter in the detection page shows both the letter and its sign
- High-contrast visuals ensure signs are easy to see in both light and dark modes

## Dark Mode

The application supports both light and dark themes:
- Click the sun/moon icon in the top-right corner to toggle between themes
- Your preference is saved in local storage and persists between sessions
- The application automatically detects your system's color scheme preference on first visit

## Note

This is a demonstration project. In a real implementation, the random letter generation would be replaced with actual AI model inference to analyze video frames and detect real sign language alphabet gestures.

## Getting Started

To run this application locally:

1. Clone this repository
2. Open `index.html` in a modern web browser
3. Allow camera access when prompted on the detection page
4. Hover over letters to see sign language gestures

## Requirements

- A modern web browser with JavaScript enabled
- A webcam
- Permission to access the webcam

## Future Improvements

- Integration with a real machine learning model for sign language detection
- Add word formation and sentence building capabilities
- User accounts to track learning progress
- Gamification features to help users learn sign language
- Theme customization options beyond light/dark mode
- Enhanced visual feedback for detected gestures 