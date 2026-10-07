# My Doc Based RAG Bot

A sleek, premium-designed Retrieval-Augmented Generation (RAG) assistant built to answer questions based entirely on the PDF documents you upload. 

Built with **LangChain**, **ChromaDB**, **Google's Gemini API**, and a completely custom **Streamlit UI** to deliver a modern, app-like experience.

---

## 🚀 Setup & Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API key
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```
*(You can get a free key at [Google AI Studio](https://aistudio.google.com/apikey))*

### 3. Launch the app
```bash
streamlit run app.py
```

### 4. Upload your PDFs
Once the app launches in your browser, simply use the "Add a new PDF" panel to upload any documents into the knowledge base. No coding required!

---

## 🛠️ Tech Stack
- **LangChain**
- **ChromaDB** (Local Vector Store)
- **Gemini Embeddings & Gemini 2.5 Flash-Lite**
- **Streamlit** (Custom Styled)

---
*Built by Aman Kumar Gupta.*