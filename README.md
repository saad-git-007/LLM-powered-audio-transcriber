# LLM Audio Transcriber (Streamlit + OpenAI)

A web application built with Streamlit to transcribe English audio files using OpenAI's `gpt-4o-mini-transcribe` model via its API. It handles various audio formats, automatically chunks large files for processing, and displays the resulting transcription.


## Features

* **Audio Upload:** Supports various common audio formats (MP3, WAV, M4A, OGG, FLAC, etc.).
* **Transcription:** Uses OpenAI's `gpt-4o-mini-transcribe` model for accurate English transcription.
* **Format Conversion:** Leverages `pydub` to handle different input formats.
* **Automatic Chunking:** Splits audio longer than approximately 10 minutes into smaller chunks before sending to the API, allowing processing of large files.
* **Progress Indicator:** Displays a progress bar during the transcription of multiple chunks.
* **Simple UI:** Easy-to-use web interface built with Streamlit.

## Technology Stack

* **Backend:** Python
* **Frontend:** Streamlit
* **Audio Processing:** pydub
* **Transcription Service:** OpenAI API
* **System Dependencies:** ffmpeg (required by pydub)

## Setup and Run Locally

Follow these steps to run the application on your local machine.

**Prerequisites:**

* Python 3.8 or higher
* pip (Python package installer)
* Git
* ffmpeg:
    * **Debian/Ubuntu:** `sudo apt update && sudo apt install ffmpeg`
    * **macOS (Homebrew):** `brew install ffmpeg`
    * **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html), install, and add to system PATH.

**Installation:**

1.  **Clone the repository:**
    ```bash
    # Replace with your actual repository URL if different
    git clone [https://github.com/saad-git-007/streamlit-audio-transcriber.git](https://github.com/saad-git-007/streamlit-audio-transcriber.git)
    cd streamlit-audio-transcriber
    ```
    *(Or clone from the Hugging Face Space repo if using that as primary)*

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    # On Linux/macOS
    source venv/bin/activate
    # On Windows
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure OpenAI API Key:** You need to provide your OpenAI API key. Choose one method:
    * **Method A (Recommended for Local):** Create a Streamlit secrets file.
        * Create the directory: `mkdir .streamlit`
        * Create the file: `nano .streamlit/secrets.toml` (or use another text editor)
        * Add your key inside: `OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`
        * Save the file. (Ensure `.streamlit/` is in your `.gitignore` file).
    * **Method B (Fallback for Local):** The app includes a fallback input field in the sidebar to enter the key when run locally *if* the secrets file is not found.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

6.  Open your web browser to the local URL provided (usually `http://localhost:8501`).

## Deployment

This application was deployed using Hugging Face Spaces. The deployment requires the following files:

* `app.py`: The main Streamlit application script.
* `requirements.txt`: Lists Python package dependencies.
* `packages.txt`: Lists system-level dependencies (`ffmpeg`) to be installed via `apt-get` on Hugging Face.

For deployment on platforms like Hugging Face Spaces, the OpenAI API key **must** be configured as a secret named `OPENAI_API_KEY` within the platform's secrets management settings.

## Usage

1.  Launch the application (either locally or via the deployment URL).
2.  If running locally using Fallback Method B, enter your OpenAI API key in the sidebar input box when prompted.
3.  Use the "Choose an audio file..." button to upload an English audio file from your computer.
4.  An audio player will appear to preview the file.
5.  Click the "Transcribe Audio" button.
6.  Wait for the progress bar (if the file is split into chunks) and processing indicators to complete.
7.  The transcription text will appear in the text area below.

## License

This project is licensed under the Apache 2.0 License.
