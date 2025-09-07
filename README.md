# Fishki - German Vocabulary Flashcards

A Streamlit application for practicing German vocabulary using flashcards and spaced repetition.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## Features

-   Deck & Word Management
-   Learn, Review, and Quiz modes
-   Spaced Repetition System (SRS) based on a modified SM-2 algorithm.
-   CSV Import/Export
-   SQLite backend for local storage.

## Keyboard Shortcuts

-   **Spacebar**: Flip the current card.
-   **1**: Grade card as "Again".
-   **2**: Grade card as "Hard".
-   **3**: Grade card as "Good".
-   **4**: Grade card as "Easy".
-   **Enter**: Submit answer in typing quiz.

## Troubleshooting

-   **pyttsx3 issues**: If you encounter errors related to text-to-speech, ensure you have the necessary system-level dependencies installed.
    -   **macOS**: No special dependencies needed.
    -   **Windows**: No special dependencies needed.
    -   **Linux**: `espeak` and `ffmpeg` might be required (`sudo apt-get install espeak ffmpeg`).
    If TTS is not working, audio features will be gracefully disabled.
