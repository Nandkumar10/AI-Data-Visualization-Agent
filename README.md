# 📊 AI Data Visualization Agent

An AI-powered data analysis app that allows users to **upload any CSV dataset, ask questions about it in plain English, and receive charts and insights** — all without writing a single line of code — using **Together AI LLMs** and a secure **E2B Code Execution Sandbox**.

---

## 🧠 About

This project takes a CSV file uploaded by the user, sends their question to a large language model, and lets the AI write and execute Python visualization code automatically.

- ✔ Understands your dataset context  
- ✔ Generates and runs Python code behind the scenes  
- ✔ Returns charts, graphs, and data insights instantly  

Instead of asking users to write visualization code manually, this system uses an **LLM to generate the code** and a **secure E2B sandbox to execute it safely in the cloud**.  
This makes data exploration faster, more accessible, and available to anyone — not just developers.

---

## 🚀 Features

- ✔ Upload any CSV dataset  
- ✔ Preview your data instantly in the app  
- ✔ Ask questions in plain English  
- ✔ AI generates Python visualization code automatically  
- ✔ Code runs securely in an isolated cloud sandbox  
- ✔ Renders charts, tables, and text results  
- ✔ Choose from multiple LLM models  
- ✔ Clean and interactive Streamlit-based interface  

---

## 🧱 Tech Stack

- **Python**
- **Streamlit (User Interface)**
- **Together AI (LLM API)**
- **E2B Code Interpreter (Secure Sandbox)**
- **Pandas (Data Handling)**
- **Matplotlib / Plotly / PIL (Visualization Rendering)**

---

## 🛠 How It Works

1. User enters their Together AI and E2B API keys in the sidebar.
2. User uploads a CSV file.
3. A preview of the dataset is shown in the app.
4. User types a question about their data.
5. The question and dataset path are sent to the selected LLM.
6. The LLM generates Python code to answer the question.
7. The code is uploaded and executed inside the E2B sandbox.
8. Results — charts, tables, or text — are displayed back in the app.

---

## 🧪 Example Questions You Can Ask

- "Compare the average cost between different categories."
- "Show me the trend in sales over time."
- "Which category has the highest revenue?"
- "Plot a distribution of customer ages."
- "What is the correlation between price and rating?"

---

## 🤔 Why E2B Sandbox Instead of Running Code Locally?

In this project, **E2B** was used instead of executing code directly on the local machine because running AI-generated code locally poses serious **security risks**.

---

### ✅ Why E2B Was Chosen

This project involves:

- An LLM generating Python code dynamically  
- That code reading and processing user-uploaded files  
- Producing matplotlib, plotly, or pandas outputs  
- Returning results back to the Streamlit UI  

This requires a **safe, isolated, and reliable execution environment**, which E2B provides using:

- Cloud-based sandboxed containers  
- File read/write support inside the sandbox  
- Stdout/stderr capture  
- Support for rich output types (PNG, figures, dataframes)  

E2B handles all execution safely without exposing the host machine to any risk.

---

### 🧠 Why Local Execution Was Not Used

Running AI-generated code locally is risky because:

- The LLM could generate harmful or unintended code  
- Local file system could be accessed or modified  
- No isolation between the AI code and the host environment  
- Debugging sandbox errors is harder without proper capture  

Since this project:

- Executes dynamically generated code from an LLM  
- Needs safe file handling inside an isolated environment  
- Requires capturing rich output types like charts and tables  
- Must be reliable and repeatable across different machines  

Running code locally would have introduced unnecessary security and stability risks.

---

## 🎯 Design Decision

The goal of this project was to:

- Make data analysis accessible to non-technical users  
- Keep the architecture simple and easy to follow  
- Focus on safe AI code execution and clean result rendering  
- Make the system beginner-friendly and easy to extend  

Therefore, **Together AI + E2B was the most appropriate and efficient choice** for this use case.

---

## 📌 Future Improvements

- Add conversational memory to support follow-up questions  
- Support multiple file uploads and merging datasets  
- Add auto-suggested questions based on dataset columns  
- Include export options for generated charts  
- Deploy as a hosted web application  
- Add support for Excel and JSON file formats  

---

## 📜 License

This project is open-source and available under the MIT License.
