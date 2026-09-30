AURA

Adaptive User-aware Reasoning Assistant

AURA is an always-on personal AI assistant designed to understand the user's context, remember ongoing activities, and interact naturally throughout everyday life.

Instead of behaving like a collection of disconnected commands or skills, AURA is designed as a persistent assistant that can adapt to what the user is doing — whether they are studying, working, cooking, planning their day, or simply asking a question.

The long-term vision is a JARVIS-like personal AI that can perceive context, communicate naturally, remember useful information, and proactively assist the user.

---

🚀 Hackathon

AURA is being developed for the Nebius × NVIDIA Global AI Hackathon 2026.

Track: Personal AI

The hackathon MVP focuses on demonstrating a small number of meaningful real-world interactions while keeping the architecture extensible for future capabilities.

---

✨ Vision

AURA aims to move beyond traditional chatbot interactions.

Instead of requiring the user to explicitly enter a mode such as:

«"Start cooking mode"»

AURA should eventually understand context naturally.

For example:

- The user starts preparing food.
- AURA recognizes that cooking may be happening.
- It asks whether the user wants assistance.
- The user selects a recipe.
- AURA guides them through the recipe step by step.
- AURA can observe the cooking process through permitted camera input.
- It can start timers and provide reminders.
- It can warn the user when an action may require attention.

The same underlying assistant can adapt to studying, working, planning, shopping, and other everyday activities.

---

🧠 Core Ideas

Context Awareness

AURA should understand what the user is currently doing rather than relying entirely on explicit commands.

Persistent Memory

Useful information and ongoing activities should persist across interactions so conversations feel continuous rather than isolated.

Natural Interaction

AURA is designed around real-time voice interaction instead of being limited to a traditional text chat interface.

Multimodal Perception

With user permission, AURA can eventually use camera and screen context to better understand the environment.

Proactive Assistance

AURA should be able to surface useful reminders, actions, and information when context makes them relevant.

Extensible Intelligence

The architecture should allow new routines and capabilities to be added without turning the user experience into a collection of separate "skills."

---

🖥️ Current Frontend

The frontend is built with:

- React
- TypeScript
- Vite
- CSS

The current interface is designed around a dark, cinematic, futuristic aesthetic.

Key UI elements include:

- Central AURA identity
- Animated space-inspired background
- Subtle star and atmospheric motion
- Breathing/glowing AURA typography
- Animated reasoning indicators
- Glass-style conversation bar
- Voice interaction controls
- Bottom navigation
- Responsive layout

The visual direction intentionally uses a predominantly black background with restrained blue-white illumination rather than a heavily blue interface.

---

🏗️ Architecture

AURA is being developed as a multi-component system:

                    ┌─────────────────────┐
                    │       AURA UI       │
                    │   React + Vite      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Voice / Sensing   │
                    │ Camera + Audio +    │
                    │ Interaction Input   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   AURA Agent Layer  │
                    │ Reasoning + Context │
                    │ Memory + Planning   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Nebius / NVIDIA   │
                    │ AI Infrastructure   │
                    │ Models + Inference  │
                    └─────────────────────┘

The frontend communicates with the backend through an API layer. The backend is responsible for reasoning, model interaction, context, memory, and agent behavior.

---

📁 Project Structure

aura/
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
│
└── README.md

---

🛠️ Development

Frontend

Navigate to the frontend:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The Vite development server will normally be available at:

http://localhost:5173

---

Backend

Navigate to the backend:

cd backend

Create and activate a Python virtual environment:

python -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure environment variables using:

.env

based on:

.env.example

The backend currently exposes a basic health endpoint and will be expanded as the AURA agent architecture develops.

---

🌌 MVP Direction

The hackathon MVP is intentionally scoped.

The goal is to demonstrate a convincing slice of the larger AURA vision rather than attempting to build a complete JARVIS system in one month.

Potential MVP interactions include:

Study / Work Context

AURA can understand when the user is working or studying and provide contextual assistance.

Cooking Assistant

AURA can guide the user through a recipe, maintain the current step, manage timers, and use permitted visual context during the process.

Everyday Assistance

AURA can help with tasks such as planning, reminders, groceries, and contextual actions.

These experiences should feel like capabilities of one assistant, not separate applications.

---

👥 Team

AURA is being developed collaboratively with separate areas of responsibility:

Area| Owner
Frontend / UI| Bharath
Backend / Agent / Memory| Anant
Voice / Sensing| Vishal

The components are developed on separate Git branches and integrated as the system evolves.

---

🌿 Branches

Current development branches include:

main
anant/backend
bharath/frontend
vishal/voice-sensing

Frontend development is currently being done on:

bharath/frontend

---

🎯 Long-Term Goal

AURA is not intended to be just another chatbot.

The goal is to build a personal AI that gradually becomes aware of the user's routines, preferences, activities, and environment — while keeping the user in control of what it can see, hear, remember, and act upon.

The eventual experience should feel less like:

«"Opening an AI app"»

and more like:

«Having an AI assistant present throughout your day.»

---

📜 Status

🚧 Active development

The current repository contains the initial AURA interface and backend foundation. Voice interaction, sensing, agent reasoning, memory, and deeper integrations are being developed incrementally.