Here is a `README.md` file for deploying and using the application `the-quarries`:

### `README.md`

# The Quarries

The Quarries is a Flask-based web application that integrates SQLite for data management and interacts with external APIs. It supports the creation and management of notes, a search function for stored data, and dynamic content generation from APIs.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation and Deployment](#installation-and-deployment)
   - [Using Docker Compose](#using-docker-compose)
   - [Manually with Docker](#manually-with-docker)
4. [How to Use](#how-to-use)
5. [Endpoints](#endpoints)
6. [Contributing](#contributing)
7. [License](#license)

## Features

- Search and display stored notes.
- Dynamic content fetching from external APIs.
- SQLite3 database integration.
- Notes management (create, update, delete, and view).
- Exporting data in various formats.

## Prerequisites

- Docker and Docker Compose installed on your system.
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (for pushing the image to GitHub Container Registry).

## Installation and Deployment

### Using Docker Compose

1. Clone the repository:

   ```bash
   git clone https://github.com/scrummycpro/the-quarries.git
   cd the-quarries
   ```

2. Build and start the application with Docker Compose:

   ```bash
   docker-compose up -d
   ```

   This command will:
   - Start the Flask application on port `3033`.
   - Automatically restart the container if it stops (thanks to the `always` restart policy).
   - Mount the `responses` directory from your local machine to the container for persistent database storage.

3. The application will be accessible at:

   ```
   http://localhost:3033
   ```

### Manually with Docker

1. Build the Docker image:

   ```bash
   docker build -t the-quarries .
   ```

2. Run the Docker container:

   ```bash
   docker run -d -p 3033:5005 -v $(pwd)/responses:/app/responses --name the-quarries the-quarries
   ```

   The application will be available at `http://localhost:3033`.

## How to Use

1. Access the application via your browser at `http://localhost:3033`.
2. Use the navigation options to:
   - Search for content stored in the database.
   - Manage notes by adding, viewing, updating, and deleting notes.
   - Export specific data entries to a file.
3. The application interacts with external APIs to fetch dynamic data for your session.

## Endpoints

- `/`: Fetches and displays random content from an API.
- `/search`: Allows keyword searches in the database.
- `/notes`: Displays, adds, and manages notes.
- `/export/<int:id>`: Exports a specific database entry to a `.txt` file.
- `/login` & `/register`: User authentication and registration system.

### Sample API Interaction

The application fetches data from external sources like [Sefaria API](https://www.sefaria.org/api) for random topics and texts. The responses are processed and displayed dynamically.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to create an issue or submit a pull request.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License.

---

This README provides clear instructions on deploying the application with Docker and Docker Compose, as well as a summary of how to use the application and its features.

# Kubernetes

The container needs this command to run 

```sh
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/scrummycpro/the-quarries:latest --push .

```
## Then :

```sh
kubectl delete pod the-quarries-pod
kubectl run the-quarries-pod --image=ghcr.io/scrummycpro/the-quarries:latest \
  --image-pull-policy=Always \
  --overrides='{ "spec": { "imagePullSecrets": [{ "name": "ghcr-secret" }] } }'

```