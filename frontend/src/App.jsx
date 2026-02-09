import { useEffect, useRef, useState } from "react";

const CANVAS_SIZE = 280;
const GRID_SIZE = 8;
const defaultProbabilities = Array.from({ length: 10 }, (_, idx) => ({
  digit: idx,
  value: 0,
}));

const App = () => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [probabilities, setProbabilities] = useState(defaultProbabilities);
  const [status, setStatus] = useState("Draw a digit and press Predict.");

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = CANVAS_SIZE;
    canvas.height = CANVAS_SIZE;
    const context = canvas.getContext("2d");
    context.lineWidth = 20;
    context.lineCap = "round";
    context.strokeStyle = "#111827";
    resetCanvas();
  }, []);

  const resetCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    setPrediction(null);
    setProbabilities(defaultProbabilities);
    setStatus("Canvas cleared. Draw a digit and press Predict.");
  };

  const getCanvasPosition = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  const handlePointerDown = (event) => {
    const context = canvasRef.current.getContext("2d");
    const { x, y } = getCanvasPosition(event);
    context.beginPath();
    context.moveTo(x, y);
    setIsDrawing(true);
  };

  const handlePointerMove = (event) => {
    if (!isDrawing) return;
    const context = canvasRef.current.getContext("2d");
    const { x, y } = getCanvasPosition(event);
    context.lineTo(x, y);
    context.stroke();
  };

  const handlePointerUp = () => {
    setIsDrawing(false);
  };

  const getPixels = () => {
    const canvas = canvasRef.current;
    const downscaled = document.createElement("canvas");
    downscaled.width = GRID_SIZE;
    downscaled.height = GRID_SIZE;
    const downCtx = downscaled.getContext("2d");
    downCtx.imageSmoothingEnabled = true;
    downCtx.drawImage(canvas, 0, 0, GRID_SIZE, GRID_SIZE);

    const imageData = downCtx.getImageData(0, 0, GRID_SIZE, GRID_SIZE).data;
    const pixels = [];

    for (let i = 0; i < imageData.length; i += 4) {
      const r = imageData[i];
      const g = imageData[i + 1];
      const b = imageData[i + 2];
      const intensity = 1 - (r + g + b) / (3 * 255);
      pixels.push(Number((intensity * 16).toFixed(4)));
    }

    return pixels;
  };

  const handlePredict = async () => {
    setStatus("Sending pixels to the model...");
    try {
      const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pixels: getPixels() }),
      });

      if (!response.ok) {
        const errorPayload = await response.json();
        throw new Error(errorPayload.error || "Prediction failed.");
      }

      const data = await response.json();
      setPrediction(data.prediction);
      const probabilityList = Object.entries(data.probabilities).map(
        ([digit, value]) => ({ digit: Number(digit), value })
      );
      probabilityList.sort((a, b) => a.digit - b.digit);
      setProbabilities(probabilityList);
      setStatus("Prediction complete.");
    } catch (error) {
      setStatus(error.message);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">Digits MLP Demo</p>
          <h1>Digit Prediction Studio</h1>
        </div>
        <p className="subtitle">
          Draw a digit (0-9) on the left. The model will infer the most likely
          class and show the full probability distribution.
        </p>
      </header>

      <main className="panel-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Draw</h2>
            <div className="panel-actions">
              <button type="button" onClick={resetCanvas} className="ghost">
                Clear
              </button>
              <button type="button" onClick={handlePredict}>
                Predict
              </button>
            </div>
          </div>
          <div className="canvas-wrap">
            <canvas
              ref={canvasRef}
              className="draw-canvas"
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerLeave={handlePointerUp}
            />
            <div className="grid-overlay" aria-hidden="true">
              {Array.from({ length: GRID_SIZE * GRID_SIZE }).map((_, idx) => (
                <span key={idx} />
              ))}
            </div>
          </div>
          <p className="status">{status}</p>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Prediction</h2>
            <span className="tag">
              {prediction === null ? "Awaiting input" : `Digit ${prediction}`}
            </span>
          </div>
          <div className="prediction-card">
            <span className="prediction-label">Top Result</span>
            <p className="prediction-value">
              {prediction === null ? "--" : prediction}
            </p>
          </div>
          <div className="probability-list">
            {probabilities.map((item) => (
              <div key={item.digit} className="probability-row">
                <span className="digit">{item.digit}</span>
                <div className="bar">
                  <div
                    className="bar-fill"
                    style={{ width: `${Math.round(item.value * 100)}%` }}
                  />
                </div>
                <span className="percent">
                  {(item.value * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>
          Backend: Flask + scikit-learn. Frontend: React with an HTML5 canvas
          drawing surface.
        </p>
      </footer>
    </div>
  );
};

export default App;
