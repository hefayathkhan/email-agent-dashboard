# 📬 Autonomous Email-to-Action Agent Dashboard

An AI-powered workflow automation system designed for corporate finance and accounts payable teams. This application automatically ingests incoming emails, classifies intent (e.g., invoices, payment queries, disputes, spam), dispatches automated ERP and status actions, and maintains an interactive audit log with real-time analytics.

---

## 🌟 Key Features

* **Automated Intent Classification:** Uses structured LLM prompts to analyze email subject lines and body text, categorizing incoming messages into distinct actionable intents.
* **Smart Action Engine:** Automatically dispatches context-aware downstream actions (e.g., triggering ERP entry for invoices, drafting auto-replies, or routing disputes to human review).
* **Interactive Dashboard:** Built with Streamlit, offering a clean corporate UI to monitor real-time email feeds, confidence metrics, and agent actions.
* **Audit Trail & Analytics:** Interactive Plotly charts track agent volume, category distributions, and step-by-step decision audit logs for governance.

---

## 🛠️ Tech Stack

* **Frontend / UI:** Streamlit, Plotly
* **Backend & Logic:** Python 3.10+, Pydantic
* **AI & NLP:** OpenAI API (GPT Models)
* **Data Handling:** Pandas

---

## 🚀 Getting Started Locally

### 1. Prerequisites
Ensure you have Python installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/hefayathkhan/email-agent-dashboard.git](https://github.com/hefayathkhan/email-agent-dashboard.git)
cd email-agent-dashboard
