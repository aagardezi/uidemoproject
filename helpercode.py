import google.auth

def get_project_id():
    """Gets the current GCP project ID.

    Returns:
        The project ID as a string.
    """

    try:
        _, project_id = google.auth.default()
        return project_id
    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"Error: Could not determine the project ID. {e}")
        return None