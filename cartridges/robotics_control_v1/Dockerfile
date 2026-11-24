
FROM python:3.11-slim

# Prevent interactive prompts and set headless rendering for MuJoCo
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MUJOCO_GL=egl

# Install minimal system dependencies for headless physics simulation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root sandbox user for untrusted candidate control loops
RUN useradd -m -u 1000 sandbox
WORKDIR /cartridge

# Install deterministic physics and math packages
RUN pip install --no-cache-dir \
    mujoco==3.2.3 \
    numpy==1.26.4 \
    scipy==1.13.1

# Copy cartridge specification and evaluator into the container
COPY perturbations.json evaluator.py ./

USER sandbox

# Run the deterministic evaluation entrypoint
CMD ["python", "evaluator.py"]
Use code with caution.

Quick Save Reminder

• Windows Notepad: Set Save as type to All Files (*.*), type Dockerfile (with a capital D and no .txt), and save.
• Mac TextEdit: Switch to Plain Text (Cmd + Shift + T), uncheck "If no extension is provided, use '.txt'", type Dockerfile, and save.
Would you like me to generate perturbations.json and evaluator.py for robotics_control_v1 next, or do you already have those two saved?
