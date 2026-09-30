"""
SkillBridge skill taxonomy.

Each skill has:
  id, name, category, estimated hours to reach job-ready basics,
  aliases (case-insensitive regex fragments) and cs (case-sensitive fragments),
  family  - skills in the same family can satisfy "X or Y" requirements,
  implies - having this skill is evidence of these broader skills,
  prereqs - what to learn first if it is missing,
  desc    - one line used for semantic (embedding) matching,
  res     - free learning resources (title, url or None for practice-based),
  project - a small "proof of skill" project idea.
"""

LANG, AI, DATA, BACK, FRONT, CLOUD, DB, SOFT = (
    "Languages", "AI & ML", "Data", "Backend", "Frontend & Mobile",
    "Cloud & DevOps", "Databases", "Ways of working",
)

# A trailing context used for short, ambiguous language names ("R", "Go").
_LANG_CTX = r"(?=\s*(?:[,/;)]|\.(?:\s|$)|$|\s+(?:programming|language|and|or|developer|services|microservices|studio)\b))"

SKILLS = []


def sk(id, name, cat, hours, ci=(), cs=(), fam=None, implies=(), prereqs=(),
       desc="", res=(), project=""):
    SKILLS.append(dict(id=id, name=name, cat=cat, hours=hours, ci=list(ci), cs=list(cs),
                       fam=fam, implies=list(implies), prereqs=list(prereqs),
                       desc=desc or name, res=list(res), project=project))


# ---------------------------------------------------------------- Languages
sk("python", "Python", LANG, 40, ci=[r"python\s?3?"], fam="lang",
   desc="Python programming for scripting, data work and backend services",
   res=[("Official Python tutorial", "https://docs.python.org/3/tutorial/"),
        ("Kaggle Learn: Python", "https://www.kaggle.com/learn/python")],
   project="A CLI tool that cleans a messy CSV and prints a summary report, with pytest tests")
sk("java", "Java", LANG, 40, ci=[r"java", r"j2ee", r"jvm"], fam="lang",
   desc="Java programming language and the JVM ecosystem",
   res=[("dev.java: Learn Java", "https://dev.java/learn/")],
   project="A small inventory service in Java with unit tests and a README")
sk("csharp", "C#", LANG, 40, ci=[r"c#", r"c sharp"], fam="lang",
   desc="C# programming language on .NET",
   res=[("Microsoft Learn: C#", "https://learn.microsoft.com/en-us/dotnet/csharp/")],
   project="A C# console app that parses and validates invoices")
sk("cpp", "C++", LANG, 45, ci=[r"c\+\+", r"cpp"], fam="lang",
   desc="C++ systems programming with memory management and performance tuning",
   res=[("LearnCpp.com", "https://www.learncpp.com/")],
   project="A fast text-search tool in C++ benchmarked against grep")
sk("go", "Go", LANG, 30, ci=[r"golang"], cs=[r"Go" + _LANG_CTX], fam="lang",
   desc="Go (Golang) for concurrent backend services",
   res=[("A Tour of Go", "https://go.dev/tour/")],
   project="A concurrent URL health-checker in Go with goroutines")
sk("rust", "Rust", LANG, 45, cs=[r"Rust"], ci=[r"rustlang"], fam="lang",
   desc="Rust systems programming with ownership and memory safety",
   res=[("The Rust Book", "https://doc.rust-lang.org/book/")],
   project="A Rust CLI that parses log files safely and fast")
sk("r", "R", LANG, 30, ci=[r"rstudio", r"tidyverse", r"ggplot2?", r"dplyr", r"r programming"],
   cs=[r"R" + _LANG_CTX], fam="lang",
   desc="R language for statistics and data analysis",
   res=[("R for Data Science (free book)", "https://r4ds.hadley.nz/")],
   project="An R Markdown report analysing a public dataset with ggplot2 charts")
sk("kotlin", "Kotlin", LANG, 30, ci=[r"kotlin"], fam="lang",
   desc="Kotlin for Android and JVM backend development",
   res=[("Kotlin docs: Getting started", "https://kotlinlang.org/docs/getting-started.html")],
   project="A Kotlin REST endpoint or Android screen with tests")
sk("scala", "Scala", LANG, 35, ci=[r"scala"], fam="lang",
   desc="Scala functional programming, often with Spark",
   res=[("Tour of Scala", "https://docs.scala-lang.org/tour/tour-of-scala.html")],
   project="A Scala job that aggregates a dataset with Spark")
sk("php", "PHP", LANG, 30, ci=[r"php", r"laravel"], fam="lang",
   desc="PHP and Laravel web development",
   res=[("PHP manual: Getting started", "https://www.php.net/manual/en/getting-started.php")],
   project="A Laravel CRUD app with authentication")
sk("ruby", "Ruby", LANG, 30, ci=[r"ruby", r"ruby on rails", r"rails"], fam="lang",
   desc="Ruby and Ruby on Rails web development",
   res=[("Ruby in Twenty Minutes", "https://www.ruby-lang.org/en/documentation/quickstart/")],
   project="A Rails app with one resource, tests and deployment")
sk("javascript", "JavaScript", LANG, 40, ci=[r"javascript", r"es6\+?", r"ecmascript", r"vanilla js", r"jquery"],
   cs=[r"JS"], fam="lang",
   desc="JavaScript programming for web browsers and Node.js",
   res=[("The Modern JavaScript Tutorial", "https://javascript.info/")],
   project="An interactive to-do app in vanilla JS with local filtering and sorting")
sk("typescript", "TypeScript", LANG, 15, ci=[r"typescript"], fam="lang", implies=["javascript"],
   prereqs=["javascript"], desc="TypeScript static typing for JavaScript applications",
   res=[("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html")],
   project="Convert a small JS project to strict TypeScript")

# ---------------------------------------------------------------- AI & ML
sk("ml", "Machine learning", AI, 35,
   ci=[r"machine learning", r"predictive model(?:l)?ing", r"supervised learning", r"unsupervised learning",
       r"classification models?", r"regression models?", r"xgboost", r"lightgbm", r"random forests?",
       r"gradient boosting", r"clustering"],
   cs=[r"ML"], prereqs=["python"],
   desc="Machine learning: training, validating and improving predictive models",
   res=[("Kaggle Learn: Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning"),
        ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course")],
   project="Predict house prices or churn end to end: baseline, better model, error analysis")
sk("sklearn", "scikit-learn", AI, 20, ci=[r"scikit[- ]?learn", r"sklearn"], implies=["ml", "python"],
   prereqs=["python"], desc="scikit-learn library for classical machine learning in Python",
   res=[("scikit-learn: Getting started", "https://scikit-learn.org/stable/getting_started.html")],
   project="A scikit-learn pipeline with preprocessing, cross-validation and a saved model")
sk("deep_learning", "Deep learning", AI, 30,
   ci=[r"deep learning", r"neural networks?", r"transformer models?"], cs=[r"CNNs?", r"RNNs?", r"LSTMs?"],
   implies=["ml"], prereqs=["ml"],
   desc="Deep learning with neural networks for vision, text or tabular data",
   res=[("fast.ai: Practical Deep Learning", "https://course.fast.ai/")],
   project="Fine-tune a small image or text classifier and report accuracy vs a baseline")
sk("pytorch", "PyTorch", AI, 25, ci=[r"py ?torch", r"torch"], fam="dl_fw",
   implies=["deep_learning", "python"], prereqs=["python"],
   desc="PyTorch framework for building and training neural networks",
   res=[("PyTorch: Learn the Basics", "https://docs.pytorch.org/tutorials/beginner/basics/intro.html")],
   project="Train a PyTorch model from scratch with a custom Dataset and training loop")
sk("tensorflow", "TensorFlow", AI, 25, ci=[r"tensor ?flow", r"tf\.keras"], fam="dl_fw",
   implies=["deep_learning", "python"], prereqs=["python"],
   desc="TensorFlow framework for training and serving neural networks",
   res=[("TensorFlow tutorials", "https://www.tensorflow.org/tutorials")],
   project="A TensorFlow model exported and served with a small prediction script")
sk("keras", "Keras", AI, 12, ci=[r"keras"], fam="dl_fw", implies=["deep_learning", "python"],
   desc="Keras high-level deep learning API",
   res=[("Keras: Getting started", "https://keras.io/getting_started/")],
   project="A Keras classifier with callbacks and a learning-curve plot")
sk("nlp", "NLP", AI, 25,
   ci=[r"nlp", r"natural language processing", r"text classification", r"named entity recognition",
       r"sentiment analysis", r"text mining", r"spacy", r"nltk"], cs=[r"NER"],
   implies=["ml"], prereqs=["ml"],
   desc="Natural language processing: text classification, entity extraction and text analytics",
   res=[("Hugging Face LLM course", "https://huggingface.co/learn/llm-course/chapter1/1")],
   project="A sentiment or ticket-routing classifier on real text with an error analysis")
sk("hf", "Hugging Face Transformers", AI, 15,
   ci=[r"hugging ?face", r"transformers library", r"hf transformers", r"hugging face hub"],
   implies=["deep_learning", "python"], prereqs=["python"],
   desc="Hugging Face Transformers and Hub for pretrained models",
   res=[("Transformers documentation", "https://huggingface.co/docs/transformers/index")],
   project="Wrap a Hub model in a pipeline and publish a demo Space")
sk("llm", "LLMs & generative AI", AI, 20,
   ci=[r"llms?", r"large language models?", r"generative ai", r"gen ?ai", r"gpt[- ]?\d?(?:\.\d)?", r"chatgpt",
       r"foundation models?", r"llama ?\d?(?:\.\d)?", r"mistral", r"open[- ]source llms?", r"openai api"],
   prereqs=["python"],
   desc="Building applications with large language models and generative AI",
   res=[("Hugging Face LLM course", "https://huggingface.co/learn/llm-course/chapter1/1"),
        ("Prompt Engineering Guide", "https://www.promptingguide.ai/")],
   project="An LLM-powered tool with structured JSON output and a small evaluation set")
sk("rag", "RAG (retrieval-augmented generation)", AI, 15,
   ci=[r"retrieval[- ]augmented generation", r"rag pipelines?"], cs=[r"RAG"],
   implies=["llm"], prereqs=["llm"],
   desc="Retrieval-augmented generation: grounding LLM answers in retrieved documents",
   res=[("HF Cookbook: Advanced RAG", "https://huggingface.co/learn/cookbook/en/advanced_rag")],
   project="Q&A over 50 PDFs with citations, plus a 20-question accuracy check")
sk("prompt", "Prompt engineering", AI, 6,
   ci=[r"prompt engineering", r"prompt design", r"prompting", r"few[- ]shot", r"chain[- ]of[- ]thought"],
   desc="Designing and testing prompts for reliable LLM behaviour",
   res=[("Prompt Engineering Guide", "https://www.promptingguide.ai/")],
   project="A prompt test-suite: 30 inputs, expected outputs, and a pass-rate table across 3 prompt versions")
sk("agents", "AI agents & tool calling", AI, 15,
   ci=[r"ai agents?", r"agentic", r"llm agents?", r"multi[- ]agent", r"tool[- ]calling", r"function[- ]calling",
       r"langgraph", r"crew ?ai", r"autogen", r"model context protocol"], cs=[r"MCP"],
   implies=["llm"], prereqs=["llm"],
   desc="LLM agents that plan and call tools or APIs",
   res=[("HF Agents course", "https://huggingface.co/learn/agents-course/unit0/introduction")],
   project="An agent that answers questions by calling two real APIs, with logged traces")
sk("langchain", "LangChain", AI, 12, ci=[r"lang ?chain"], fam="llm_fw", implies=["llm", "python"],
   prereqs=["llm"], desc="LangChain framework for LLM applications",
   res=[("LangChain docs", "https://docs.langchain.com/")],
   project="A LangChain retrieval chain with a custom prompt and source citations")
sk("llamaindex", "LlamaIndex", AI, 10, ci=[r"llama ?index"], fam="llm_fw", implies=["llm", "python"],
   prereqs=["llm"], desc="LlamaIndex framework for indexing data for LLMs",
   res=[("LlamaIndex docs", "https://developers.llamaindex.ai/python/framework/")],
   project="A LlamaIndex query engine over your own notes")
sk("vector", "Vector search & embeddings", DB, 10,
   ci=[r"vector (?:databases?|dbs?|stores?|search|similarity search)", r"faiss", r"pinecone", r"qdrant",
       r"weaviate", r"chroma(?:db)?", r"milvus", r"pgvector", r"embeddings?", r"semantic search",
       r"sentence[- ]transformers", r"similarity search"],
   desc="Embeddings and vector databases for semantic search",
   res=[("Qdrant documentation", "https://qdrant.tech/documentation/")],
   project="Semantic search over 10k product descriptions with a relevance spot-check")
sk("model_eval", "Model evaluation", AI, 10,
   ci=[r"model evaluation", r"evaluation metrics", r"cross[- ]validation", r"precision(?:/| and )recall",
       r"f1[- ]score", r"roc[- ]auc", r"llm evaluation", r"evals? (?:frameworks?|pipelines?|harness)",
       r"offline evaluation", r"benchmarking models"],
   implies=["ml"],
   desc="Evaluating models with the right metrics, validation splits and error analysis",
   res=[("scikit-learn: Model evaluation", "https://scikit-learn.org/stable/modules/model_evaluation.html")],
   project="An evaluation report comparing 3 models with confusion matrices and failure cases")
sk("fine_tuning", "Fine-tuning (LoRA/PEFT)", AI, 20,
   ci=[r"fine[- ]?tun(?:e|ed|es|ing)", r"q?lora", r"peft", r"instruction tuning", r"rlhf"],
   implies=["deep_learning"], prereqs=["hf"],
   desc="Fine-tuning pretrained models with LoRA, PEFT or instruction tuning",
   res=[("Hugging Face PEFT docs", "https://huggingface.co/docs/peft/index")],
   project="LoRA fine-tune a small open model on 1k examples and compare with the base model")
sk("cv", "Computer vision", AI, 30,
   ci=[r"computer vision", r"image classification", r"object detection", r"image segmentation", r"opencv",
       r"yolo(?:v\d+)?", r"image processing"],
   implies=["ml"], prereqs=["deep_learning"],
   desc="Computer vision: image classification, detection and segmentation",
   res=[("Kaggle Learn: Computer Vision", "https://www.kaggle.com/learn/computer-vision")],
   project="An object detector for a custom class with 200 labelled images")
sk("speech", "Speech AI", AI, 20,
   ci=[r"speech recognition", r"speech[- ]to[- ]text", r"text[- ]to[- ]speech", r"whisper", r"audio processing"],
   cs=[r"ASR", r"TTS"], implies=["ml"], prereqs=["deep_learning"],
   desc="Speech recognition and speech synthesis",
   res=[("Hugging Face Audio course", "https://huggingface.co/learn/audio-course/chapter0/introduction")],
   project="Transcribe and summarise meeting audio with Whisper, with word error rate on a sample")
sk("ocr", "OCR & document AI", AI, 12,
   ci=[r"optical character recognition", r"document ai", r"document understanding", r"tesseract",
       r"document parsing", r"invoice extraction"], cs=[r"OCR"],
   desc="Extracting text and fields from scanned documents",
   res=[("Tesseract documentation", "https://tesseract-ocr.github.io/tessdoc/")],
   project="Extract fields from 30 receipts and measure field-level accuracy")
sk("mlops", "MLOps & model deployment", AI, 20,
   ci=[r"mlops", r"model deployment", r"model serving", r"model monitoring", r"ml pipelines?",
       r"machine learning pipelines?", r"kubeflow", r"bentoml", r"deploy(?:ed|ing)? (?:ml |machine learning )?models?",
       r"ml systems? in production", r"models? (?:into|to|in) production", r"productioni[sz]"],
   implies=["ml"], prereqs=["docker"],
   desc="MLOps: deploying, versioning and monitoring machine learning models in production",
   res=[("Made With ML", "https://madewithml.com/"),
        ("DataTalksClub MLOps Zoomcamp", "https://github.com/DataTalksClub/mlops-zoomcamp")],
   project="Serve a model behind an API in Docker with CI and a drift check")
sk("tracking", "Experiment tracking (MLflow)", AI, 6,
   ci=[r"ml ?flow", r"weights (?:&|and) biases", r"wandb", r"experiment tracking", r"dvc"],
   implies=["ml"], desc="Tracking experiments, parameters and model versions",
   res=[("MLflow documentation", "https://mlflow.org/docs/latest/")],
   project="Log 10 training runs to MLflow and register the best model")
sk("model_opt", "Model optimization & serving", AI, 15,
   ci=[r"onnx", r"quantization", r"tensorrt", r"model optimi[sz]ation", r"distillation", r"pruning", r"vllm",
       r"llama\.cpp", r"ollama", r"inference optimi[sz]ation"],
   prereqs=["deep_learning"], desc="Making models smaller and faster to serve: quantization, ONNX, vLLM",
   res=[("ONNX Runtime docs", "https://onnxruntime.ai/docs/")],
   project="Quantize a model, then compare latency and accuracy before and after")
sk("cuda", "CUDA / GPU computing", AI, 30, ci=[r"cuda", r"gpu (?:programming|computing|optimi[sz]ation|kernels?)"],
   desc="GPU programming and optimization with CUDA",
   res=[("NVIDIA CUDA C++ Programming Guide", "https://docs.nvidia.com/cuda/cuda-c-programming-guide/")],
   project="Write and benchmark a CUDA kernel for matrix multiply")
sk("responsible_ai", "Responsible AI", AI, 8,
   ci=[r"responsible ai", r"ai ethics", r"fairness", r"explainab(?:le|ility)", r"interpretab(?:le|ility)", r"shap",
       r"ai safety", r"guardrails", r"bias mitigation"],
   desc="Fairness, explainability and safety of AI systems",
   res=[("Google ML Crash Course: Fairness", "https://developers.google.com/machine-learning/crash-course/fairness")],
   project="A model card with SHAP explanations and a fairness check across groups")
sk("prototyping", "ML demos (Gradio/Streamlit)", AI, 5, ci=[r"streamlit", r"gradio", r"ml demos?"],
   implies=["python"], desc="Building quick ML demo apps with Gradio or Streamlit",
   res=[("Gradio quickstart", "https://www.gradio.app/guides/quickstart")],
   project="Publish a Gradio demo of one of your models on Hugging Face Spaces")
sk("stats", "Statistics", DATA, 30,
   ci=[r"statistics", r"statistical (?:analysis|model(?:l)?ing|methods|significance|inference)", r"hypothesis testing",
       r"probability", r"regression analysis", r"inferential", r"bayesian"],
   desc="Statistics: distributions, hypothesis testing and regression",
   res=[("OpenIntro Statistics (free book)", "https://www.openintro.org/book/os/"),
        ("Khan Academy: Statistics", "https://www.khanacademy.org/math/statistics-probability")],
   project="Answer 3 business questions from a public dataset with confidence intervals")
sk("ab_testing", "A/B testing", DATA, 10,
   ci=[r"a/b test(?:s|ing)?", r"ab test(?:s|ing)", r"experimentation", r"split test(?:s|ing)", r"controlled experiments"],
   implies=["stats"], prereqs=["stats"],
   desc="Designing and analysing A/B tests and product experiments",
   res=[("Khan Academy: Significance tests", "https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample")],
   project="Analyse a simulated A/B test: sample size, significance, and a written recommendation")
sk("math", "Math for ML", AI, 30, ci=[r"linear algebra", r"calculus", r"mathematics", r"optimization theory"],
   desc="Linear algebra, calculus and probability for machine learning",
   res=[("3Blue1Brown: Linear algebra", "https://www.3blue1brown.com/topics/linear-algebra")],
   project="Implement linear regression with gradient descent in NumPy and explain each step")
sk("time_series", "Time-series forecasting", DATA, 15,
   ci=[r"time[- ]series", r"forecasting", r"arima", r"prophet"], implies=["stats"],
   desc="Forecasting and time-series analysis",
   res=[("Kaggle Learn: Time Series", "https://www.kaggle.com/learn/time-series")],
   project="Forecast 12 weeks of sales and compare against a naive baseline")
sk("feature_eng", "Feature engineering", AI, 10,
   ci=[r"feature engineering", r"feature selection", r"feature stores?"], implies=["ml"],
   desc="Creating and selecting features that improve models",
   res=[("Kaggle Learn: Feature Engineering", "https://www.kaggle.com/learn/feature-engineering")],
   project="Improve a baseline model by 5%+ using only new features, documented")
sk("recsys", "Recommender systems", AI, 20,
   ci=[r"recommend(?:er|ation) (?:systems?|engines?)", r"collaborative filtering", r"personali[sz]ation"],
   implies=["ml"], prereqs=["ml"], desc="Recommender systems and personalization",
   res=[("Google: Recommendation systems course", "https://developers.google.com/machine-learning/recommendation")],
   project="A movie recommender with offline precision@10")
sk("rl", "Reinforcement learning", AI, 30, ci=[r"reinforcement learning"], cs=[r"RL"], implies=["ml"],
   prereqs=["deep_learning"], desc="Reinforcement learning agents and policies",
   res=[("Hugging Face Deep RL course", "https://huggingface.co/learn/deep-rl-course/unit0/introduction")],
   project="Train an agent on a Gymnasium environment and plot reward over time")

# ---------------------------------------------------------------- Data
sk("pandas", "pandas", DATA, 15, ci=[r"pandas", r"dataframes?", r"polars"], implies=["python"],
   prereqs=["python"], desc="pandas for data manipulation and analysis in Python",
   res=[("Kaggle Learn: Pandas", "https://www.kaggle.com/learn/pandas")],
   project="Clean and analyse a messy public dataset; publish the notebook")
sk("numpy", "NumPy", DATA, 8, ci=[r"numpy", r"scipy"], implies=["python"], prereqs=["python"],
   desc="NumPy numerical computing and arrays",
   res=[("NumPy: Learn", "https://numpy.org/learn/")],
   project="Vectorise a slow loop-based script and measure the speed-up")
sk("dataviz", "Data visualization", DATA, 12,
   ci=[r"data visuali[sz]ation", r"visuali[sz]ations?", r"dashboards?", r"matplotlib", r"seaborn", r"plotly",
       r"d3(?:\.js)?"],
   desc="Data visualization and dashboards that communicate insights",
   res=[("Kaggle Learn: Data Visualization", "https://www.kaggle.com/learn/data-visualization")],
   project="A 1-page dashboard answering one clear business question")
sk("data_cleaning", "Data cleaning", DATA, 8,
   ci=[r"data cleaning", r"data cleansing", r"data wrangling", r"data preprocessing", r"data preparation",
       r"data quality", r"data validation"],
   desc="Cleaning, validating and preparing raw data",
   res=[("Kaggle Learn: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning")],
   project="A reusable cleaning script with data-quality checks and a before/after report")
sk("etl", "ETL & data pipelines", DATA, 15,
   ci=[r"etl pipelines?", r"data pipelines?", r"data ingestion", r"data integration", r"ssis", r"informatica",
       r"fivetran"], cs=[r"ETL", r"ELT"],
   desc="Building ETL/ELT data pipelines that move and transform data",
   res=[("DataTalksClub Data Engineering Zoomcamp", "https://github.com/DataTalksClub/data-engineering-zoomcamp")],
   project="A daily pipeline from a public API into Postgres with logging and retries")
sk("warehouse", "Data warehousing", DATA, 15,
   ci=[r"data warehous(?:e|es|ing)", r"snowflake", r"redshift", r"big ?query", r"synapse", r"star schema",
       r"dimensional model(?:l)?ing", r"data lakes?", r"lakehouse"],
   implies=["sql"], prereqs=["sql"], desc="Data warehouses such as Snowflake, BigQuery or Redshift",
   res=[("BigQuery overview", "https://docs.cloud.google.com/bigquery/docs/introduction")],
   project="Model a small star schema and write 5 analytical queries on it")
sk("spark", "Spark & big data", DATA, 20,
   ci=[r"spark", r"pyspark", r"hadoop", r"hive", r"databricks", r"big data", r"mapreduce"],
   prereqs=["python"], desc="Distributed data processing with Apache Spark and big-data tools",
   res=[("Spark quick start", "https://spark.apache.org/docs/latest/quick-start.html")],
   project="Process a multi-GB dataset with PySpark and compare with pandas")
sk("airflow", "Workflow orchestration (Airflow)", DATA, 12,
   ci=[r"airflow", r"prefect", r"dagster", r"luigi", r"(?:workflow|data) orchestration"], implies=["etl"],
   prereqs=["python"], desc="Scheduling and orchestrating data workflows with Airflow",
   res=[("Airflow tutorial", "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html")],
   project="An Airflow DAG with 3 tasks, retries and a failure alert")
sk("dbt", "dbt", DATA, 10, ci=[r"dbt"], implies=["sql"], prereqs=["sql"],
   desc="dbt for SQL-based data transformation and testing",
   res=[("dbt Learn (free courses)", "https://learn.getdbt.com/")],
   project="A dbt project with staging and mart models plus tests")
sk("kafka", "Kafka & streaming", DATA, 15,
   ci=[r"kafka", r"kinesis", r"stream(?:ing)? processing", r"flink", r"real[- ]time (?:data|streaming|pipelines?)",
       r"event streaming"],
   desc="Real-time data streaming with Kafka or similar",
   res=[("Kafka quickstart", "https://kafka.apache.org/quickstart")],
   project="A producer/consumer pair that computes live rolling metrics")
sk("excel", "Excel", DATA, 10,
   ci=[r"ms excel", r"microsoft excel", r"spreadsheets?", r"[vx]lookups?", r"pivot tables?", r"google sheets"],
   cs=[r"Excel"], desc="Excel and spreadsheets: formulas, lookups and pivot tables",
   res=[("Microsoft: Excel help & learning", "https://support.microsoft.com/en-us/excel")],
   project="A self-updating monthly report with pivots and lookups")
sk("powerbi", "Power BI", DATA, 15, ci=[r"power ?bi", r"dax", r"power query"], fam="bi", implies=["dataviz"],
   desc="Power BI dashboards and DAX",
   res=[("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi")],
   project="A Power BI dashboard with 3 DAX measures and drill-through")
sk("tableau", "Tableau", DATA, 15, ci=[r"tableau"], fam="bi", implies=["dataviz"],
   desc="Tableau dashboards and visual analytics",
   res=[("Tableau free training", "https://www.tableau.com/learn/training")],
   project="A Tableau Public dashboard on an open dataset")
sk("looker", "Looker", DATA, 12, ci=[r"looker", r"lookml", r"looker studio", r"data studio"], fam="bi",
   implies=["dataviz"], desc="Looker and Looker Studio reporting",
   res=[("Data Studio (Looker Studio) docs", "https://docs.cloud.google.com/data-studio")],
   project="A Looker Studio report connected to a live Google Sheet")
sk("bi", "Business intelligence & KPIs", DATA, 8,
   ci=[r"business intelligence", r"metrics definition", r"kpi dashboards?"], cs=[r"(?<!Power )BI", r"KPIs?"],
   desc="Business intelligence: defining KPIs and reporting on them",
   res=[("Practice", None)],
   project="Define 5 KPIs for a business you know and build a one-page KPI tracker")

# ---------------------------------------------------------------- Backend
sk("rest", "REST APIs", BACK, 10,
   ci=[r"rest(?:ful)?(?: apis?| services| web services)", r"api (?:design|development|integrations?)",
       r"web apis?", r"http apis?", r"openapi", r"swagger",
       r"(?:build|built|building|develop(?:ed|ing)?|design(?:ed|ing)?|integrat(?:e|ed|ing)|expos(?:e|ed|ing)) (?:\w+ ){0,2}apis?"],
   cs=[r"REST"], desc="Designing and building REST APIs",
   res=[("Microsoft: Web API design best practices", "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design")],
   project="A documented REST API with auth, validation and pagination")
sk("fastapi", "FastAPI", BACK, 10, ci=[r"fast ?api"], fam="web_fw", implies=["python", "rest"],
   prereqs=["python"], desc="FastAPI Python web framework",
   res=[("FastAPI tutorial", "https://fastapi.tiangolo.com/tutorial/")],
   project="A FastAPI service with typed endpoints, tests and OpenAPI docs")
sk("flask", "Flask", BACK, 10, ci=[r"flask"], fam="web_fw", implies=["python", "rest"], prereqs=["python"],
   desc="Flask Python web framework",
   res=[("Flask tutorial", "https://flask.palletsprojects.com/en/stable/tutorial/")],
   project="A Flask app with login and a database")
sk("django", "Django", BACK, 20, ci=[r"django", r"django rest framework"], cs=[r"DRF"], fam="web_fw",
   implies=["python", "rest"], prereqs=["python"], desc="Django Python web framework",
   res=[("Django tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/")],
   project="A Django app with admin, auth and a REST endpoint")
sk("nodejs", "Node.js", BACK, 20, ci=[r"node\.?js", r"node js", r"nest\.?js"], fam=("web_fw", "lang"),
   implies=["javascript"], prereqs=["javascript"], desc="Node.js server-side JavaScript",
   res=[("Node.js: Learn", "https://nodejs.org/en/learn")],
   project="A Node.js API with input validation and tests")
sk("express", "Express.js", BACK, 8, ci=[r"express\.?js", r"express framework", r"node(?:\.js)?\s*/\s*express"],
   cs=[r"(?<!American )Express(?!\s+[a-z])"],
   fam="web_fw", implies=["nodejs", "rest"], prereqs=["nodejs"], desc="Express.js web framework for Node",
   res=[("Express: Getting started", "https://expressjs.com/en/starter/installing.html")],
   project="An Express REST API with middleware and error handling")
sk("spring", "Spring Boot", BACK, 25, ci=[r"spring ?boot", r"spring (?:framework|mvc|cloud)", r"hibernate"],
   fam="web_fw", implies=["java", "rest"], prereqs=["java"], desc="Spring Boot Java backend framework",
   res=[("Spring guides", "https://spring.io/guides")],
   project="A Spring Boot service with JPA, validation and tests")
sk("dotnet", ".NET / ASP.NET", BACK, 25, ci=[r"\.net(?: core)?", r"asp\.net(?: core)?", r"dotnet", r"entity framework"],
   fam="web_fw", implies=["csharp"], prereqs=["csharp"], desc="ASP.NET Core backend development",
   res=[("ASP.NET Core docs", "https://learn.microsoft.com/en-us/aspnet/core/")],
   project="An ASP.NET Core minimal API with EF Core")
sk("graphql", "GraphQL", BACK, 10, ci=[r"graphql", r"apollo"], desc="GraphQL APIs and schemas",
   res=[("GraphQL: Learn", "https://graphql.org/learn/")],
   project="A GraphQL API over an existing REST service")
sk("microservices", "Microservices", BACK, 15,
   ci=[r"micro-?services?(?: architecture)?", r"service[- ]oriented architecture"], cs=[r"SOA"],
   prereqs=["rest"], desc="Designing and running microservice architectures",
   res=[("microservices.io patterns", "https://microservices.io/")],
   project="Split a monolith demo into 2 services that talk over HTTP and a queue")
sk("system_design", "System design", BACK, 25,
   ci=[r"system design", r"distributed systems?", r"scalable (?:systems|architectures?|services|backends?)",
       r"software architecture", r"high[- ]availability", r"fault[- ]toleran(?:t|ce)", r"large[- ]scale systems"],
   desc="Designing scalable, reliable distributed systems",
   res=[("System Design Primer", "https://github.com/donnemartin/system-design-primer")],
   project="Write a design doc for a URL shortener at 10k req/s, with trade-offs")
sk("testing", "Automated testing", BACK, 12,
   ci=[r"unit test(?:s|ing)?", r"integration test(?:s|ing)?", r"automated test(?:s|ing)", r"test automation",
       r"pytest", r"jest", r"junit", r"mocha", r"cypress", r"selenium", r"playwright", r"test[- ]driven",
       r"unittest", r"end[- ]to[- ]end test(?:s|ing)", r"e2e test(?:s|ing)"], cs=[r"TDD"],
   desc="Writing unit, integration and end-to-end tests",
   res=[("pytest: Get started", "https://docs.pytest.org/en/stable/getting-started.html")],
   project="Add a test suite to an old project and reach 80% coverage")
sk("caching", "Caching (Redis)", BACK, 6, ci=[r"redis", r"memcached", r"caching"],
   desc="Caching with Redis to make services faster",
   res=[("Redis docs", "https://redis.io/docs/latest/")],
   project="Add Redis caching to an API and measure latency before and after")
sk("queues", "Message queues", BACK, 10,
   ci=[r"rabbitmq", r"message (?:queues?|brokers?|queuing)", r"celery", r"pub/?sub", r"activemq",
       r"event[- ]driven(?: architecture)?"], cs=[r"SQS"],
   desc="Asynchronous processing with message queues and event-driven design",
   res=[("RabbitMQ tutorials", "https://www.rabbitmq.com/tutorials")],
   project="Move a slow request into a background worker with retries")
sk("grpc", "gRPC", BACK, 8, ci=[r"grpc", r"protobuf", r"protocol buffers"], desc="gRPC and Protocol Buffers",
   res=[("gRPC introduction", "https://grpc.io/docs/what-is-grpc/introduction/")],
   project="A gRPC service and client with a streaming endpoint")
sk("security", "Web security & auth", BACK, 12,
   ci=[r"oauth ?2?(?:\.0)?", r"authentication", r"authori[sz]ation", r"owasp", r"application security",
       r"secure coding", r"encryption", r"security best practices"], cs=[r"JWT", r"SSO", r"IAM"],
   desc="Authentication, authorization and secure coding (OWASP)",
   res=[("OWASP Top 10", "https://owasp.org/www-project-top-ten/")],
   project="Add OAuth login and fix 3 OWASP issues in a demo app")
sk("oop", "OOP & design patterns", BACK, 15,
   ci=[r"object[- ]oriented(?: programming| design)?", r"design patterns", r"solid principles", r"clean code",
       r"clean architecture"], cs=[r"OOP", r"SOLID"],
   desc="Object-oriented design, SOLID principles and design patterns",
   res=[("Refactoring.Guru: Design patterns", "https://refactoring.guru/design-patterns")],
   project="Refactor a messy script into classes using 2 named patterns")
sk("dsa", "Data structures & algorithms", BACK, 40,
   ci=[r"data structures", r"algorithms", r"leetcode", r"competitive programming", r"big[- ]o", r"time complexity"],
   cs=[r"DSA"], desc="Data structures, algorithms and complexity",
   res=[("NeetCode roadmap", "https://neetcode.io/roadmap")],
   project="Solve 40 curated problems and write up 5 patterns you learned")

# ---------------------------------------------------------------- Frontend & mobile
sk("html_css", "HTML & CSS", FRONT, 20,
   ci=[r"html5?", r"css3?", r"sass", r"scss", r"responsive (?:web )?design", r"flexbox", r"css grid", r"bootstrap"],
   desc="HTML and CSS for responsive web pages",
   res=[("web.dev: Learn CSS", "https://web.dev/learn/css"), ("web.dev: Learn HTML", "https://web.dev/learn/html")],
   project="Rebuild a real landing page responsively from a screenshot")
sk("react", "React", FRONT, 30, ci=[r"react\.?js", r"reactjs", r"react hooks", r"jsx"], cs=[r"React"],
   fam="fe_fw", implies=["javascript", "html_css"], prereqs=["javascript"],
   desc="React for building component-based user interfaces",
   res=[("react.dev: Learn", "https://react.dev/learn")],
   project="A React app that consumes a public API with loading and error states")
sk("nextjs", "Next.js", FRONT, 15, ci=[r"next\.?js", r"nextjs"], implies=["react", "javascript"],
   prereqs=["react"], desc="Next.js React framework with server rendering",
   res=[("Next.js Learn", "https://nextjs.org/learn")],
   project="A Next.js site with dynamic routes and server-side data fetching")
sk("vue", "Vue", FRONT, 25, ci=[r"vue(?:\.?js)?", r"nuxt(?:\.?js)?"], fam="fe_fw",
   implies=["javascript", "html_css"], prereqs=["javascript"], desc="Vue.js front-end framework",
   res=[("Vue tutorial", "https://vuejs.org/tutorial/")],
   project="A Vue dashboard with routing and a store")
sk("angular", "Angular", FRONT, 30, ci=[r"angular(?:js|\.js)?"], fam="fe_fw",
   implies=["typescript", "html_css"], prereqs=["typescript"], desc="Angular front-end framework",
   res=[("Angular tutorials", "https://angular.dev/tutorials")],
   project="An Angular app with a form, validation and an HTTP service")
sk("svelte", "Svelte", FRONT, 15, ci=[r"svelte(?:kit)?"], fam="fe_fw", implies=["javascript"],
   prereqs=["javascript"], desc="Svelte front-end framework",
   res=[("Svelte tutorial", "https://svelte.dev/tutorial")],
   project="A SvelteKit app with one form action")
sk("tailwind", "Tailwind CSS", FRONT, 6, ci=[r"tailwind(?: ?css)?"], implies=["html_css"],
   desc="Tailwind utility-first CSS",
   res=[("Tailwind docs", "https://tailwindcss.com/docs")],
   project="Restyle an existing page with Tailwind and a dark mode")
sk("state_mgmt", "State management (Redux)", FRONT, 8,
   ci=[r"redux", r"zustand", r"mobx", r"state management", r"react query", r"tanstack query"],
   prereqs=["react"], desc="Front-end state management with Redux or similar",
   res=[("Redux Essentials", "https://redux.js.org/tutorials/essentials/part-1-overview-concepts")],
   project="Add a global store with persisted state to a React app")
sk("a11y", "Accessibility", FRONT, 8, ci=[r"accessibility", r"a11y", r"wcag"], cs=[r"ARIA"],
   desc="Web accessibility (WCAG)",
   res=[("web.dev: Learn Accessibility", "https://web.dev/learn/accessibility")],
   project="Audit a site with Lighthouse and fix every accessibility issue")
sk("ux", "UI/UX design (Figma)", FRONT, 12,
   ci=[r"figma", r"ui/ux", r"ux/ui", r"user experience", r"wire-?frames?", r"wireframing", r"user research",
       r"usability testing", r"design systems?"],
   desc="UI/UX design, wireframing and prototyping in Figma",
   res=[("Figma: Resource library", "https://www.figma.com/resource-library/")],
   project="Redesign one painful screen of an app you use, with a before/after")
sk("flutter", "Flutter", FRONT, 35, ci=[r"flutter", r"dart"], fam="mobile",
   desc="Flutter and Dart cross-platform mobile apps",
   res=[("Flutter docs", "https://docs.flutter.dev/")],
   project="A Flutter app with 3 screens and an API call")
sk("react_native", "React Native", FRONT, 30, ci=[r"react native"], fam="mobile", implies=["react", "javascript"],
   prereqs=["react"], desc="React Native cross-platform mobile apps",
   res=[("React Native: Get started", "https://reactnative.dev/docs/getting-started")],
   project="A React Native app published to Expo")
sk("android", "Android", FRONT, 35, ci=[r"android(?: sdk| development)?", r"jetpack compose"], fam="mobile",
   desc="Native Android development",
   res=[("Android Developers: Courses", "https://developer.android.com/courses")],
   project="A Compose app with a list, detail screen and local storage")
sk("ios", "iOS (Swift)", FRONT, 35, ci=[r"swift ?ui", r"xcode", r"uikit"], cs=[r"iOS", r"Swift"], fam="mobile",
   desc="Native iOS development with Swift and SwiftUI",
   res=[("Apple: SwiftUI tutorials", "https://developer.apple.com/tutorials/swiftui")],
   project="A SwiftUI app with navigation and persistence")

# ---------------------------------------------------------------- Cloud & DevOps
sk("docker", "Docker", CLOUD, 12,
   ci=[r"docker", r"containeri[sz](?:ation|ed|ing)", r"containers?", r"dockerfiles?", r"docker[- ]compose", r"podman"],
   desc="Docker containers for packaging and running applications",
   res=[("Docker: Get started", "https://docs.docker.com/get-started/")],
   project="Containerise an app with a multi-stage Dockerfile and docker-compose")
sk("kubernetes", "Kubernetes", CLOUD, 20, ci=[r"kubernetes", r"k8s", r"helm", r"openshift"],
   cs=[r"EKS", r"GKE", r"AKS"], implies=["docker"], prereqs=["docker"],
   desc="Kubernetes container orchestration",
   res=[("Kubernetes basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/")],
   project="Deploy an app to a local kind cluster with a Deployment, Service and autoscaling")
sk("aws", "AWS", CLOUD, 24,
   ci=[r"amazon web services", r"aws lambda", r"sagemaker", r"cloudformation", r"cloudwatch", r"aws glue"],
   cs=[r"AWS", r"EC2", r"S3"], fam="cloud", implies=["cloud"],
   desc="Amazon Web Services cloud (EC2, S3, Lambda and more)",
   res=[("AWS Skill Builder (free courses)", "https://skillbuilder.aws/")],
   project="Deploy an app on AWS free tier with S3, a Lambda function and IAM least-privilege")
sk("azure", "Azure", CLOUD, 24, ci=[r"azure", r"microsoft azure"], fam="cloud", implies=["cloud"],
   desc="Microsoft Azure cloud",
   res=[("Microsoft Learn: Azure", "https://learn.microsoft.com/en-us/training/azure/")],
   project="Deploy an app to Azure App Service with a managed database")
sk("gcp", "Google Cloud", CLOUD, 24, ci=[r"google cloud(?: platform)?", r"vertex ai", r"cloud run"],
   cs=[r"GCP"], fam="cloud", implies=["cloud"], desc="Google Cloud Platform",
   res=[("Google Cloud: Get started", "https://docs.cloud.google.com/docs/get-started")],
   project="Deploy a container to Cloud Run with a BigQuery-backed endpoint")
sk("cloud", "Cloud fundamentals", CLOUD, 8,
   ci=[r"cloud computing", r"cloud platforms?", r"cloud[- ]native", r"cloud (?:services|infrastructure|environments?|providers?)",
       r"public cloud"],
   desc="Cloud computing fundamentals: compute, storage, networking and IAM",
   res=[("AWS Skill Builder: Cloud Practitioner Essentials", "https://skillbuilder.aws/")],
   project="Draw and explain the cloud architecture of one of your projects")
sk("iac", "Infrastructure as code (Terraform)", CLOUD, 15,
   ci=[r"terraform", r"infrastructure[- ]as[- ]code", r"pulumi", r"ansible", r"bicep"], cs=[r"IaC"],
   prereqs=["cloud"], desc="Infrastructure as code with Terraform",
   res=[("Terraform tutorials", "https://developer.hashicorp.com/terraform/tutorials")],
   project="Provision your project's cloud resources with Terraform, then destroy and recreate")
sk("ci_cd", "CI/CD", CLOUD, 10,
   ci=[r"ci ?/ ?cd", r"continuous integration", r"continuous (?:delivery|deployment)", r"github actions",
       r"gitlab ci", r"jenkins", r"circleci", r"argo ?cd", r"azure devops", r"(?:build|deployment) pipelines?"],
   desc="Continuous integration and delivery pipelines",
   res=[("GitHub Actions docs", "https://docs.github.com/en/actions")],
   project="A GitHub Actions workflow that tests, builds a Docker image and deploys")
sk("git", "Git", CLOUD, 6, ci=[r"git", r"github", r"gitlab", r"bitbucket", r"version control", r"pull requests?"],
   desc="Git version control and collaborative workflows",
   res=[("Pro Git book", "https://git-scm.com/book/en/v2")],
   project="Contribute a small fix to an open-source repo through a pull request")
sk("linux", "Linux & shell", CLOUD, 12,
   ci=[r"linux", r"unix", r"bash", r"shell scripting", r"shell scripts?", r"command[- ]line", r"ubuntu"],
   desc="Linux, the command line and shell scripting",
   res=[("MIT Missing Semester", "https://missing.csail.mit.edu/")],
   project="A bash script that backs up, compresses and rotates a folder on a schedule")
sk("monitoring", "Monitoring & observability", CLOUD, 10,
   ci=[r"monitoring", r"observability", r"prometheus", r"grafana", r"datadog", r"new relic", r"elk(?: stack)?",
       r"opentelemetry", r"alerting", r"sentry"],
   desc="Monitoring, logging, metrics and alerting",
   res=[("Prometheus overview", "https://prometheus.io/docs/introduction/overview/")],
   project="Add metrics and a Grafana dashboard with one alert to your API")
sk("serverless", "Serverless", CLOUD, 10, ci=[r"serverless", r"aws lambda", r"cloud functions", r"azure functions",
                                               r"lambda functions"],
   implies=["cloud"], desc="Serverless functions and event-driven cloud apps",
   res=[("AWS Lambda developer guide", "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html")],
   project="A serverless function triggered by a file upload")

# ---------------------------------------------------------------- Databases
sk("sql", "SQL", DB, 20,
   ci=[r"sql", r"t-sql", r"pl/sql", r"relational databases?", r"sql queries"], cs=[r"RDBMS"],
   desc="SQL queries: joins, aggregations, window functions",
   res=[("Kaggle Learn: Intro to SQL", "https://www.kaggle.com/learn/intro-to-sql"),
        ("SQLBolt interactive lessons", "https://sqlbolt.com/")],
   project="Answer 10 business questions on a sample database using joins and window functions")
sk("postgres", "PostgreSQL", DB, 10, ci=[r"postgres(?:ql)?", r"psql"], fam="sql_db", implies=["sql"],
   prereqs=["sql"], desc="PostgreSQL relational database",
   res=[("PostgreSQL tutorial", "https://www.postgresql.org/docs/current/tutorial.html")],
   project="Design a Postgres schema with indexes and explain a slow query")
sk("mysql", "MySQL", DB, 8, ci=[r"mysql", r"mariadb"], fam="sql_db", implies=["sql"], prereqs=["sql"],
   desc="MySQL relational database",
   res=[("MySQL documentation", "https://dev.mysql.com/doc/")],
   project="Migrate a small app from SQLite to MySQL")
sk("sqlserver", "SQL Server", DB, 10, ci=[r"sql server", r"mssql", r"ms sql", r"ssms"], fam="sql_db",
   implies=["sql"], prereqs=["sql"], desc="Microsoft SQL Server",
   res=[("SQL Server docs", "https://learn.microsoft.com/en-us/sql/sql-server/")],
   project="Write stored procedures and a scheduled job in SQL Server")
sk("oracle", "Oracle Database", DB, 12, ci=[r"oracle(?: database| db)", r"pl/sql"], fam="sql_db", implies=["sql"],
   prereqs=["sql"], desc="Oracle Database and PL/SQL",
   res=[("Oracle Dev Gym (free)", "https://devgym.oracle.com/")],
   project="PL/SQL procedures for a reporting workflow")
sk("mongodb", "MongoDB", DB, 10, ci=[r"mongo ?db", r"mongoose", r"mongo"], fam="nosql_db", implies=["nosql"],
   desc="MongoDB document database",
   res=[("MongoDB University (free)", "https://learn.mongodb.com/")],
   project="Model a product catalogue in MongoDB with aggregation queries")
sk("nosql", "NoSQL databases", DB, 10,
   ci=[r"nosql", r"dynamo ?db", r"cassandra", r"couchbase", r"firestore", r"firebase", r"document databases?",
       r"key[- ]value stores?", r"cosmos ?db"],
   fam="nosql_db", desc="NoSQL databases such as DynamoDB, Cassandra or Firestore",
   res=[("DynamoDB developer guide", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html")],
   project="Design access patterns for a chat app in DynamoDB")
sk("search", "Elasticsearch", DB, 12, ci=[r"elastic ?search", r"opensearch", r"solr", r"full[- ]text search", r"lucene"],
   desc="Full-text search with Elasticsearch or OpenSearch",
   res=[("Elastic docs", "https://www.elastic.co/docs")],
   project="Search over 100k documents with filters and highlighting")
sk("data_modeling", "Data modeling", DB, 12,
   ci=[r"data model(?:l)?ing", r"schema design", r"database design", r"normali[sz]ation", r"er diagrams?",
       r"entity[- ]relationship"],
   desc="Designing database schemas and data models",
   res=[("PostgreSQL: Data definition", "https://www.postgresql.org/docs/current/ddl.html")],
   project="Design and justify a normalised schema for a booking system")

# ---------------------------------------------------------------- Ways of working
sk("agile", "Agile / Scrum", SOFT, 4, ci=[r"agile", r"scrum", r"kanban", r"sprints?", r"jira", r"stand-?ups?"],
   desc="Agile ways of working: Scrum, sprints and Kanban",
   res=[("The Scrum Guide", "https://scrumguides.org/")],
   project="Run your next project in 1-week sprints with a public board")
sk("communication", "Communication", SOFT, 8,
   ci=[r"communication(?: skills)?", r"communicat(?:e|ed|ing)", r"present(?:ed|ing) (?:findings|results|insights|to)",
       r"presentations?", r"public speaking", r"technical writing", r"documentation", r"storytelling",
       r"written and verbal", r"verbal and written", r"articulate"],
   desc="Clear written and verbal communication of technical work",
   res=[("Google Technical Writing courses", "https://developers.google.com/tech-writing")],
   project="Write a 1-page project summary and record a 3-minute walkthrough video")
sk("stakeholders", "Stakeholder management", SOFT, 6,
   ci=[r"stakeholders?", r"cross[- ]functional", r"client[- ]facing", r"business partners",
       r"work(?:ed|ing)? (?:closely )?with product"],
   desc="Working with stakeholders and cross-functional teams",
   res=[("Practice", None)],
   project="Interview a stakeholder, write their requirements, and get sign-off")
sk("leadership", "Leadership & mentoring", SOFT, 10,
   ci=[r"leadership", r"led (?:a |the )?(?:team|squad|group)", r"team lead(?:er)?", r"mentor(?:ed|ing|ship|s)?",
       r"managed (?:a )?team", r"people management", r"tech lead", r"coached"],
   desc="Leading teams and mentoring others",
   res=[("Practice", None)],
   project="Mentor a junior or peer through one project and document the outcome")
sk("pm", "Project management", SOFT, 10,
   ci=[r"project management", r"project manager", r"managed (?:the )?(?:project|delivery|timeline)s?", r"roadmaps?",
       r"prioriti[sz](?:e|ed|ing|ation)", r"timelines", r"deadlines"], cs=[r"PMP"],
   desc="Planning, prioritising and delivering projects on time",
   res=[("Practice", None)],
   project="Plan a 4-week project with milestones and report progress weekly")
sk("problem_solving", "Problem solving", SOFT, 10,
   ci=[r"problem[- ]solving", r"analytical (?:skills|thinking|mindset)", r"critical thinking", r"troubleshoot(?:ing|ed)?",
       r"debugg(?:ing|ed)", r"root[- ]cause analysis", r"solv(?:e|ed|ing) complex problems"],
   desc="Structured problem solving, debugging and root-cause analysis",
   res=[("Practice", None)],
   project="Write a root-cause analysis for a real bug you fixed")
sk("product", "Product thinking", SOFT, 8,
   ci=[r"product (?:sense|thinking|mindset)", r"user[- ]centric", r"customer empathy", r"product[- ]minded",
       r"business acumen", r"business impact"],
   desc="Understanding users and business impact when building products",
   res=[("Practice", None)],
   project="Write a one-page product brief: user, problem, metric, solution")


# -------------------------------------------------------------------------
# Adjacent skills: knowing one makes learning the other faster.
# (set of skill ids, fraction of learning time saved)
ADJACENT = [
    ({"pytorch", "tensorflow", "keras"}, 0.5),
    ({"aws", "azure", "gcp"}, 0.5),
    ({"postgres", "mysql", "sqlserver", "oracle"}, 0.6),
    ({"fastapi", "flask", "django"}, 0.45),
    ({"nodejs", "express", "fastapi", "flask", "django", "spring", "dotnet"}, 0.25),
    ({"react", "vue", "angular", "svelte"}, 0.4),
    ({"react", "nextjs"}, 0.5),
    ({"react", "react_native"}, 0.5),
    ({"powerbi", "tableau", "looker"}, 0.5),
    ({"excel", "powerbi", "tableau", "looker"}, 0.2),
    ({"langchain", "llamaindex"}, 0.5),
    ({"java", "csharp", "kotlin", "scala"}, 0.35),
    ({"javascript", "typescript"}, 0.5),
    ({"python", "r"}, 0.3),
    ({"cpp", "rust", "go"}, 0.25),
    ({"python", "go", "java", "javascript"}, 0.15),
    ({"mongodb", "nosql", "search"}, 0.3),
    ({"airflow", "dbt", "etl"}, 0.3),
    ({"spark", "warehouse", "etl"}, 0.25),
    ({"kafka", "queues"}, 0.4),
    ({"docker", "kubernetes"}, 0.3),
    ({"flutter", "react_native", "android", "ios"}, 0.3),
    ({"ml", "deep_learning"}, 0.3),
    ({"deep_learning", "cv", "nlp", "speech"}, 0.3),
    ({"nlp", "llm"}, 0.35),
    ({"rag", "vector"}, 0.4),
    ({"rag", "agents", "langchain", "llamaindex"}, 0.3),
    ({"hf", "fine_tuning", "pytorch"}, 0.3),
    ({"mlops", "docker", "ci_cd"}, 0.3),
    ({"mlops", "tracking"}, 0.4),
    ({"stats", "ab_testing"}, 0.4),
    ({"html_css", "tailwind"}, 0.5),
    ({"rest", "graphql", "grpc"}, 0.3),
    ({"iac", "cloud", "aws", "azure", "gcp"}, 0.2),
    ({"sql", "data_modeling", "warehouse"}, 0.3),
    ({"pandas", "sql", "spark"}, 0.2),
    ({"dataviz", "powerbi", "tableau", "looker"}, 0.3),
]

SKILL_BY_ID = {s["id"]: s for s in SKILLS}
CATEGORIES = [LANG, AI, DATA, BACK, FRONT, CLOUD, DB, SOFT]
