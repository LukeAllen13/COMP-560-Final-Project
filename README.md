# COMP-560-Final-Project
Final project for COMP 560

## How to run:
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
cd frontend
npm install
npm run dev

## Description...
Our project is a fully interactive chess engine built from scratch using AI concepts covered in class. Our main goal was to create a system that not only plays chess using adversarial search, but also demonstrates core course ideas such as heuristic eval, zero-sum modeling, and inteligent decision-making under uncertainty. The project includes a custom rules engine, a modern frontend, and an optional LLM-based "referee" feature which was inspired by projects that combine symbolic AI with generative models. 

Backend:
The backend (FastAPI + Python) contains the move generator, board representation, search algorithm, and evaluation function. Legal move generation, check/checkmate detection, and static evaluation all follow the algorithms we've seen. The AI player uses depth-limited minimax with AB pruning to select moves, while the evaluation function models a zero-sum utility signal based on material balance. We also added one custom super-knight to each side to add a bit of fun! 

Frontend: 
The frontend (React + Typescript) renders theboard, tracks interactions, and displays the engine's standing through an evaluation bar that updates after each move. This visualizes the heuristic value of the position as the search sees it. The optional referee mode, powered by Ollama, allows users to request natural-language explanations of positions, blending symbolic and generative AI to deepen understanding. 

PVP: 
We added a toggle on/off for the AI, so you can play vs someone else (on the same device). 
