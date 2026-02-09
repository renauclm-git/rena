# Digits MLP Demo

This project trains a simple multilayer perceptron on the scikit-learn digits dataset and exposes the model through a Flask API with a React drawing interface.

## Project structure

- `backend/`: Flask API that trains and serves the digits model.
- `frontend/`: React UI with a canvas-based drawing surface.
- `scripts/install.sh`: Installs backend + frontend dependencies.
- `scripts/init.sh`: Installs dependencies and starts both servers.

## Quick start

1. Install dependencies:
   ```bash
   ./scripts/install.sh
   ```
2. Start the project:
   ```bash
   ./scripts/init.sh
   ```

The backend runs on `http://localhost:5000` and the frontend runs on `http://localhost:5173`.

## API

- `GET /api/health`: basic health check.
- `POST /api/predict`: send an array of 64 pixel values (8x8) to receive the predicted digit and probability distribution.

Example request body:

```json
{
  "pixels": [0, 0, 0, 4, 8, 2, 0, 0]
}
```
