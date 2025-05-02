# BUD Claims Summarizer

A web application built with Streamlit that allows users to select PDF files stored in a Google Cloud Storage (GCS) bucket and generate summaries using Google's Gemini AI model via Vertex AI.

## Features

*   Lists PDF files from a specified GCS bucket.
*   Allows users to select a file from the list via a dropdown menu.
*   Generates a text summary of the selected PDF file using the `gemini-2.0-flash-001` model on Vertex AI.
*   Displays the generated summary directly in the web interface.
*   Streams the summary output as it's generated.

## Prerequisites (Local Development)

*   Python 3.12 or higher.

*   Access to a Google Cloud project with:
    *   Vertex AI API enabled.
    *   Cloud Storage API enabled.
*   A Google Cloud Storage bucket containing the PDF files you want to summarize.
*   Authenticated Google Cloud credentials in your environment. The application uses Application Default Credentials (ADC). You can set this up by running:
    ```bash
    gcloud auth application-default login
    ```

## Setup (Local Development)

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **Create `requirements.txt`:** Create a file named `requirements.txt` in the project root with the following content:
    ```
    streamlit
    google-cloud-storage
    google-generativeai
    google-cloud-aiplatform
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    The application requires the name of the GCS bucket containing the PDF files. Set the `BUCKET_NAME` environment variable:
    ```bash
    export BUCKET_NAME="your-gcs-bucket-name"
    ```
    Replace `"your-gcs-bucket-name"` with the actual name of your bucket.

5.  **Configure Google Cloud Project (if necessary):**
    The application currently uses the hardcoded Google Cloud project ID `genaillentsearch` and location `us-central1` for Vertex AI operations (see the `generate` function in `main.py`). Ensure your authenticated credentials have access to this project and location, or modify the script to use environment variables or ADC's default project.

6.  **Ensure Logo Exists:** The application tries to load `image/logo.png`. Make sure this path and file exist relative to `main.py`, or remove/update the `st.image` line in `main.py`.

## Running the Application (Local Development)

1.  Navigate to the directory containing `main.py`.
2.  Run the Streamlit application:
    ```bash
    streamlit run main.py
    ```
3.  Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).

## Dependencies

*   streamlit
*   google-cloud-storage
*   google-generativeai
*   google-cloud-aiplatform

## Deployment with Cloud Build and Cloud Run

You can build a container image for this application using Google Cloud Build and deploy it as a serverless web app using Google Cloud Run.

### Prerequisites for Deployment

1.  **Enable APIs:** Ensure the following APIs are enabled in your Google Cloud project:
    *   Cloud Build API (`cloudbuild.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud Run Admin API (`run.googleapis.com`)
    *   Vertex AI API (`aiplatform.googleapis.com`)
    *   Cloud Storage API (`storage.googleapis.com`)
    ```bash
    gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com storage.googleapis.com --project=YOUR_PROJECT_ID
    ```
2.  **Permissions:**
    *   Grant the **Cloud Build Service Account** (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`) the `roles/artifactregistry.writer` role to push images to Artifact Registry. You might need additional roles (`roles/cloudrun.admin`, `roles/iam.serviceAccountUser`) if Cloud Build directly deploys to Cloud Run (not shown in this example).
    *   Create or identify a **Service Account for Cloud Run** to run the service. This service account needs roles to access GCS and Vertex AI:
        *   `roles/storage.objectViewer` (to list and read from the GCS bucket)
        *   `roles/aiplatform.user` (to interact with Vertex AI Gemini)
3.  **Artifact Registry Repository:** Create a Docker repository in Artifact Registry:
    ```bash
    export REGION="us-central1" # Or your preferred region
    export AR_REPO="my-streamlit-apps" # Choose a repository name
    export PROJECT_ID=$(gcloud config get-value project)
    gcloud artifacts repositories create "$AR_REPO" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for Streamlit apps" \
        --project="$PROJECT_ID"
    ```

### Configuration Files

Ensure the following files exist in your project root directory:
1.  **`main.py`**: Your application code.
2.  **`requirements.txt`**: Lists Python dependencies (see content above).
3.  **`Dockerfile`**: Defines the container build process (see content above). Ensure the `image/logo.png` file exists or adjust `main.py`.
4.  **`cloudbuild.yaml`**: Defines the build steps for Cloud Build (see content above).

### Build with Cloud Build

Submit the build to Cloud Build from your project's root directory. Replace placeholders with your values.

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1" # Use the same region as your AR repo
export AR_REPO="my-streamlit-apps" # Use the repo name created earlier
export AR_HOSTNAME="${REGION}-docker.pkg.dev"
export SERVICE_NAME="bud-claims-summarizer" # Choose a name for your Cloud Run service

gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_AR_HOSTNAME="$AR_HOSTNAME",_AR_REPO="$AR_REPO",_SERVICE_NAME="$SERVICE_NAME",COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo 'latest') \
  --project="$PROJECT_ID"
```
*(Note: `COMMIT_SHA` uses the short git commit hash if available, otherwise defaults to 'latest'. Adjust if not using git.)*

### Deploy to Cloud Run

Deploy the image built by Cloud Build to Cloud Run.

```bash
# --- Required Variables ---
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1" # Use the same region as build/AR repo
export AR_REPO="my-streamlit-apps" # Use the repo name created earlier
export AR_HOSTNAME="${REGION}-docker.pkg.dev"
export SERVICE_NAME="bud-claims-summarizer" # Use the same service name as build
export IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo 'latest') # Match the build tag

# --- Deployment Specific Variables ---
export CLOUD_RUN_SERVICE_ACCOUNT="your-cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com" # Replace with your Cloud Run SA email
export BUCKET_NAME="your-gcs-bucket-name" # Replace with your actual bucket name

gcloud run deploy "$SERVICE_NAME" \
  --image "$AR_HOSTNAME/$PROJECT_ID/$AR_REPO/$SERVICE_NAME:$IMAGE_TAG" \
  --platform managed \
  --region "$REGION" \
  --service-account="$CLOUD_RUN_SERVICE_ACCOUNT" \
  --set-env-vars="BUCKET_NAME=$BUCKET_NAME" \
  --port 8080 \
  --allow-unauthenticated \
  --project="$PROJECT_ID"
# Use --no-allow-unauthenticated for private access
```

After deployment, Cloud Run will provide a URL to access your Streamlit application.

**Important:** The Cloud Run service needs its assigned Service Account (`CLOUD_RUN_SERVICE_ACCOUNT`) to have the necessary IAM permissions (Storage Object Viewer, Vertex AI User) to access the GCS bucket (`BUCKET_NAME`) and the Vertex AI endpoint (in project `genaillentsearch`, location `us-central1` as currently hardcoded in `main.py`). Consider parameterizing the project and location in `main.py` using environment variables for better flexibility in deployment.