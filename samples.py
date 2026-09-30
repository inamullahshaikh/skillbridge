"""Sample resumes and job descriptions (all people and companies are fictional)."""

RESUMES = {
    "Sara Malik: data analyst": """SARA MALIK
Lahore, Pakistan | sara.malik@example.com | github.com/sara-malik-demo

SUMMARY
Data analyst with nearly 3 years of experience turning messy data into decisions. Comfortable with Python, SQL and dashboards, and I have started building machine learning models.

EXPERIENCE
Data Analyst, BrightCart (e-commerce) | Jan 2024 - Present
- Wrote SQL queries on PostgreSQL and Python/pandas scripts that automated weekly sales reporting, saving 6 hours a week.
- Built Power BI dashboards that 3 regional managers use to track KPIs.
- Trained a churn prediction model with scikit-learn (random forest) that lifted retention-campaign response by 12%.
- Presented findings to marketing and operations stakeholders every month.

Junior Data Analyst Intern, Numeris Labs | Jun 2023 - Dec 2023
- Cleaned and validated survey datasets with pandas and Excel pivot tables.
- Automated data ingestion from Google Sheets into a MySQL database.

PROJECTS
- Product review classifier: TF-IDF + logistic regression, served through a small Flask API.
- Store sales forecasting with Prophet for 50 stores, compared against a naive baseline.

SKILLS
Python, SQL, pandas, NumPy, scikit-learn, Power BI, Excel, Git, Flask
Familiar with: Docker, TensorFlow

EDUCATION
BS Computer Science, University of the Punjab | 2019 - 2023
""",
    "Omar Farooq: front-end developer": """OMAR FAROOQ
Karachi | omar.farooq@example.com

PROFILE
Front-end developer who ships fast, accessible web apps.

WORK EXPERIENCE
Frontend Developer, Pixelgate Studio | Mar 2022 - Present
- Built customer dashboards in React and TypeScript used by 20k monthly users.
- Created reusable components with Tailwind CSS and raised the Lighthouse accessibility score from 72 to 98.
- Integrated REST APIs from a Node.js backend and wrote Jest unit tests.
- Worked in two-week Scrum sprints with designers in Figma.

Web Developer, Freelance | 2020 - 2022
- Delivered 15 responsive websites with HTML, CSS and JavaScript for small businesses.

SKILLS
JavaScript, TypeScript, React, Redux, HTML/CSS, Tailwind, Git, GitHub Actions
Basic: Express.js, MongoDB

EDUCATION
BSc Software Engineering, NED University | 2016 - 2020
""",
}

JOBS = {
    "Junior ML Engineer": """Junior Machine Learning Engineer
Nimbus Health AI | Remote

About the role
You'll help us turn clinical and operational data into ML models that run in production.

What you'll do
- Build, evaluate and deploy machine learning models for patient-flow forecasting.
- Develop data pipelines and REST APIs with FastAPI that serve model predictions.
- Work with product and clinical stakeholders to define success metrics.

Requirements
- 1+ years of experience in data science, ML or software engineering.
- Strong Python and SQL.
- Hands-on experience with scikit-learn and a deep learning framework such as PyTorch or TensorFlow.
- Experience with Docker and Git.
- Experience with a cloud platform (AWS, GCP or Azure).
- Solid grasp of statistics and model evaluation (cross-validation, precision/recall).
- Bachelor's degree in Computer Science, Statistics or a related field.

Nice to have
- Experience with LLMs, RAG or vector databases.
- MLOps tooling such as MLflow, and CI/CD pipelines.
- Kubernetes.

What we offer
- Learning budget, flexible hours and health insurance.
""",
    "Data Analyst": """Data Analyst
Karvaan Retail | Karachi (hybrid)

What you'll do
- Own weekly and monthly performance reporting for the category team.
- Design and analyse A/B tests for pricing and promotions.
- Turn questions from stakeholders into clear dashboards and recommendations.

Requirements
- 2+ years of experience as a data or business analyst.
- Advanced SQL (joins, window functions) and Excel.
- Dashboarding in Power BI or Tableau.
- Working knowledge of statistics and hypothesis testing.
- Python with pandas for analysis.
- Excellent written and verbal communication.

Nice to have
- dbt or experience with a data warehouse like BigQuery or Snowflake.
- Experience in retail or e-commerce analytics.
""",
    "AI Engineer (LLM apps)": """AI Engineer (LLM Applications)
Lumen Labs | Islamabad or remote

About the role
We build assistants that help customer-support teams answer faster. You'll take LLM features from prototype to production.

Responsibilities
- Build retrieval-augmented generation (RAG) pipelines over customer knowledge bases.
- Design prompts, tool calling and guardrails, and measure quality with an evaluation harness.
- Ship services with FastAPI and Docker, and monitor them in production.

Requirements
- 3+ years of software engineering experience, including 1+ year with LLMs.
- Strong Python.
- Hands-on with LangChain or LlamaIndex.
- Experience with vector databases (e.g. Qdrant, pgvector, Pinecone).
- Prompt engineering and LLM evaluation.
- REST API design; Docker.

Nice to have
- Fine-tuning open models with LoRA/PEFT.
- AI agents and function calling.
- AWS or GCP.
""",
    "Full-stack developer": """Full-Stack Developer (React / Node.js)
Tessera Fintech | Lahore

What you'll do
- Build features end to end across our React front end and Node.js services.
- Design REST APIs and PostgreSQL schemas.
- Write tests and keep our CI/CD pipeline green.

Requirements
- 3+ years of professional experience building web applications.
- React and TypeScript.
- Node.js with Express.
- PostgreSQL and SQL data modeling.
- Docker, Git and CI/CD (GitHub Actions).
- Unit and integration testing.

Nice to have
- Next.js.
- AWS.
- GraphQL.
""",
}
