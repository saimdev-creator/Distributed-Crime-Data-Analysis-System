# Distributed Crime Data Analysis System (DCDAS)
## �Course Information
**Course Title:** Parallel Distributed Computing
**Class:** BSCS 6th Semester (Morning)
**Session:** 2023–2027
**Submitted To:** Sir Usman Mohyuddin
**Department:** Computing & Emerging Technology--
## �Project Title
### Distributed Crime Data Analysis System--
## �TeamMembers
| Name | Roll No | Role |
|------|--------|------|
| Muhammad Usaid Iqbal | 09 | Group Leader |
| Muhammad Hassan | 51 | Data Cleaning & Partitioning |
| Farrukh Sajjad | 32 | Networking & Cluster Setup |
| M. Saim Rizwan | 27 | Distributed Logic, Master/Worker, Dashboard |
| Muhammad Ahmed Saleem | 61 | Documentation & Presentation |--
## �Project Overview
The **Distributed Crime Data Analysis System (DCDAS)** is a scalable and fault-tolerant distributed
computing system designed to process large-scale UK crime datasets efficiently using **Parallel and
Distributed Computing (PDC)** concepts.
The system follows a **Master–Worker architecture** where a central Master Node distributes data
chunks to multiple Worker Nodes via **TCP socket communication with zlib compression**.--
## �KeyFeatures- Distributed Master–Worker Architecture- Dataset partitioning into 10 balanced chunks- TCP socket-based communication- zlib compression for fast transfer- Load balancing across nodes- Fault tolerance with auto recovery- Real-time Streamlit dashboard- Hardware monitoring & analytics--
## �SystemWorkflow
1. Dataset is loaded and cleaned
2. Feature engineering is applied
3. Data is split into 10 chunks
4. Master assigns chunks to workers
5. Workers process data in parallel
6. Results are merged
7. Dashboard displays analytics--
## �Dataset Information- Source: UK Police Crime Data (data.police.uk)- Records: 700,160- Time Period: 2023– 2026- Original Columns: 11- Engineered Columns: 21--
## �SystemArchitecture- **Master Node:** Task distribution, coordination, result merging- **Worker Nodes:** Parallel data processing- **Dashboard:** Real-time visualization (Streamlit)- **Communication:** TCP Sockets + Compression--
## �DataProcessing- Data Cleaning- Feature Engineering- Data Partitioning- Transformation for analytics--
## �Project Structure
DCDAS/
├──datasets/
│├──raw/
│└──processed/
├──preprocessing/
│├──clean.py
│├──transform.py
│└──partitioner.py
├──distributed/
│├──master.py
│└──worker.py
├──visualization/
│└──dashboard.py
├──outputs/
└──README.md
--
## �Dashboard Features- Crime Type Distribution- Monthly Trends- Crime Hotspots Map- Police Force Comparison- Hardware Monitoring- Task Scheduling View--
## ⚙Technologies Used- Python 3.11- Pandas & NumPy- TCP Sockets- zlib Compression- Streamlit- Plotly- Threading--
## ⚡ Performance Results- Total Records: 700,160- Processing Time: ~63.81 seconds- Chunks: 10- Workers: 3- Fault Events: 0--
## �PDCConceptsImplemented- Data Partitioning- Parallel Processing- Load Balancing- Fault Tolerance- Distributed Computing- Thread Safety- Compression-based Communication--
## �FutureImprovements- Docker containerization- Kafka / RabbitMQ integration- Machine Learning prediction models- Database integration (PostgreSQL)- Auto-scaling workers- Secure encrypted communication--
## �References- https://data.police.uk- https://docs.python.org/3/howto/sockets.html- https://docs.streamlit.io- https://plotly.com/python/- https://pandas.pydata.org- Distributed Systems: Tanenbaum & Van Steen- Distributed Systems: Coulouris et al.--
## �Conclusion
This project demonstrates how distributed computing can significantly improve performance in
processing large-scale datasets while ensuring scalability, fault tolerance, and real-time analytics
