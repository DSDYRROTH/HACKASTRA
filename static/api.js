/**
 * Sign Language Detection API Client
 * This file provides methods to connect with a sign language detection backend service
 */

class SignLanguageAPI {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.apiKey = null;
        this.isConnected = false;
        this.streamInterval = null;
    }

    /**
     * Initialize API connection with authentication
     * @param {string} apiKey - API key for authentication
     * @returns {Promise<boolean>} - Connection success status
     */
    async initialize(apiKey) {
        this.apiKey = apiKey;
        
        try {
            const response = await fetch(`${this.baseUrl}/auth`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.sessionId;
                this.isConnected = true;
                console.log('API connection established');
                return true;
            } else {
                console.error('Failed to authenticate with API');
                return false;
            }
        } catch (error) {
            console.error('API connection error:', error);
            return false;
        }
    }

    /**
     * Start detection session
     * @returns {Promise<object>} - Session information
     */
    async startSession() {
        if (!this.isConnected) {
            throw new Error('API not connected. Call initialize() first');
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    config: {
                        detectionThreshold: 0.75,
                        returnSignImages: true
                    }
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Detection session started:', data);
                return data;
            } else {
                console.error('Failed to start detection session');
                throw new Error('Failed to start detection session');
            }
        } catch (error) {
            console.error('Start session error:', error);
            throw error;
        }
    }

    /**
     * Process a single video frame for sign detection
     * @param {Blob} imageBlob - Video frame as blob data
     * @returns {Promise<object>} - Detection results
     */
    async processFrame(imageBlob) {
        if (!this.isConnected) {
            throw new Error('API not connected. Call initialize() first');
        }
        
        try {
            const formData = new FormData();
            formData.append('image', imageBlob, 'frame.jpg');
            formData.append('sessionId', this.sessionId);
            
            const response = await fetch(`${this.baseUrl}/detect`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                console.error('Frame processing failed');
                return { error: 'Frame processing failed', detected: [] };
            }
        } catch (error) {
            console.error('Process frame error:', error);
            return { error: error.message, detected: [] };
        }
    }

    /**
     * Start continuous frame processing from video element
     * @param {HTMLVideoElement} videoElement - Video element to capture frames from
     * @param {Function} callback - Callback function receiving detection results
     * @param {number} interval - Interval between frame captures in ms (default: 500ms)
     */
    startContinuousDetection(videoElement, callback, interval = 500) {
        if (!this.isConnected) {
            throw new Error('API not connected. Call initialize() first');
        }
        
        // Create canvas for frame capture
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        // Set appropriate dimensions
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        // Stop any existing interval
        this.stopContinuousDetection();
        
        // Start new detection interval
        this.streamInterval = setInterval(async () => {
            // Only process if video is playing
            if (videoElement.paused || videoElement.ended) {
                return;
            }
            
            // Draw current frame to canvas
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            
            // Convert to blob
            canvas.toBlob(async (blob) => {
                // Process the frame
                const result = await this.processFrame(blob);
                
                // Call the callback with results
                callback(result);
            }, 'image/jpeg', 0.8);
            
        }, interval);
    }

    /**
     * Stop continuous frame processing
     */
    stopContinuousDetection() {
        if (this.streamInterval) {
            clearInterval(this.streamInterval);
            this.streamInterval = null;
        }
    }

    /**
     * End detection session
     * @returns {Promise<boolean>} - Success status
     */
    async endSession() {
        if (!this.isConnected || !this.sessionId) {
            return false;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/sessions/${this.sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                console.log('Session ended successfully');
                this.stopContinuousDetection();
                return true;
            } else {
                console.error('Failed to end session properly');
                return false;
            }
        } catch (error) {
            console.error('End session error:', error);
            return false;
        }
    }
}

// Create global instance for easy access
const signLanguageAPI = new SignLanguageAPI();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SignLanguageAPI, signLanguageAPI };
} 