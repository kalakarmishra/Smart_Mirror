
import cv2
from fer import FER
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize FER detector
detector = FER(mtcnn=True)

# Define a simple mapping for emotions to numeric scores
emotion_scores = {
    "angry": -2,
    "disgust": -2,
    "fear": -1,
    "sad": -1,
    "neutral": 0,
    "surprise": 1,
    "happy": 2
}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect emotions in the frame
    result = detector.detect_emotions(frame)

    # Collect scores for average mood
    scores = []

    for face in result:
        (x, y, w, h) = face["box"]
        emotions = face["emotions"]
        dominant_emotion = max(emotions, key=emotions.get)

        # Draw rectangle and text for each face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, dominant_emotion, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Add score for average mood
        scores.append(emotion_scores.get(dominant_emotion, 0))

    # Calculate average mood if faces detected
    if scores:
        avg_score = np.mean(scores)
        if avg_score >= 1.5:
            avg_mood = "Very Happy 😀"
        elif avg_score >= 0.5:
            avg_mood = "Happy 🙂"
        elif avg_score >= -0.5:
            avg_mood = "Neutral 😐"
        elif avg_score >= -1.5:
            avg_mood = "Sad 🙁"
        else:
            avg_mood = "Very Sad 😢"
        cv2.putText(frame, f"Average Mood: {avg_mood}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show frame
    cv2.imshow("Mood Detection", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()