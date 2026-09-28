# Distributed Crime Data Analysis System (DCDAS)

## 📚 Course Information

* **Course Title:** Parallel Distributed Computing
* **Class:** BSCS 6th Semester (Morning)
* **Session:** 2023–2027
* **Submitted To:** Sir Usman Mohyuddin
* **Department:** Computing & Emerging Technology

## 📌 Project Title

**Distributed Crime Data Analysis System (DCDAS)**

## 👥 Team Members

| Name                  | Roll No | Role                                        |
| --------------------- | ------: | ------------------------------------------- |
| Muhammad Usaid Iqbal  |      09 | Group Leader                                |
| Muhammad Hassan       |      51 | Data Cleaning & Partitioning                |
| Farrukh Sajjad        |      32 | Networking & Cluster Setup                  |
| M. Saim Rizwan        |      27 | Distributed Logic, Master/Worker, Dashboard |
| Muhammad Ahmed Saleem |      61 | Documentation & Presentation                |

## 📖 Project Overview

The **Distributed Crime Data Analysis System (DCDAS)** is a scalable and fault-tolerant distributed computing system designed to process large-scale UK crime datasets efficiently using **Parallel and Distributed Computing (PDC)** concepts.

The system follows a **Master–Worker architecture**, where a central Master Node distributes data chunks to multiple Worker Nodes through **TCP socket communication with zlib compression**.

## ✨ Key Features

* Distributed Master–Worker Architecture
* Dataset partitioning into 10 balanced chunks
* TCP socket-based communication
* zlib compression for efficient data transfer
* Load balancing across worker nodes
* Fault tolerance with auto-recovery
* Real-time Streamlit dashboard
* Hardware monitoring and analytics

## 🔄 System Workflow

1. Dataset is loaded and cleaned
2. Feature engineering is applied
3. Data is divided into 10 chunks
4. Master Node assigns chunks to workers
5. Workers process data in parallel
6. Results are merged
7. Dashboard displays analytics

## 📊 Dataset Information

* **Source:** UK Police Crime Data — data.police.uk
* **Records:** 700,160
* **Time Period:** 2023–2026
* **Original Columns:** 11
* **Engineered Columns:** 21

## 🏗️ System Architecture

### Master Node

* Task distribution
* Worker coordination
* Result merging

### Worker Nodes

* Parallel data processing
* Chunk-based computation

### Dashboard

* Real-time data visualization using Streamlit
* Crime analytics and system monitoring

### Communication

* TCP Sockets
* zlib Compression

## ⚙️ Data Processing

The system performs the following data processing operations:

* Data Cleaning
* Feature Engineering
* Data Partitioning
* Data Transformation
* Distributed Data Processing

## 📁 Project Structure

```text
DCDAS/
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── preprocessing/
│   ├── clean.py
│   ├── transform.py
│   └── partitioner.py
│
├── distributed/
│   ├── master.py
│   └── worker.py
│
├── visualization/
│   └── dashboard.py
│
├── outputs/
│
└── README.md
```

## 📈 Dashboard Features

* Crime Type Distribution
* Monthly Crime Trends
* Crime Hotspots Map
* Police Force Comparison
* Hardware Monitoring
* Task Scheduling View

## 🛠️ Technologies Used

* **Python 3.11**
* **Pandas**
* **NumPy**
* **TCP Sockets**
* **zlib Compression**
* **Streamlit**
* **Plotly**
* **Threading**

## ⚡ Performance Results

| Metric           |         Result |
| ---------------- | -------------: |
| Total Records    |        700,160 |
| Processing Time  | ~63.81 seconds |
| Number of Chunks |             10 |
| Workers          |              3 |
| Fault Events     |              0 |

## 🧠 PDC Concepts Implemented

* Data Partitioning
* Parallel Processing
* Load Balancing
* Fault Tolerance
* Distributed Computing
* Thread Safety
* Compression-Based Communication

## 🚀 Future Improvements

* Docker Containerization
* Kafka / RabbitMQ Integration
* Machine Learning Prediction Models
* PostgreSQL Database Integration
* Auto-Scaling Workers
* Secure Encrypted Communication

## 📚 References

* [UK Police Crime Data](https://data.police.uk/)
* [Python Socket Programming](https://docs.python.org/3/howto/sockets.html)
* [Streamlit Documentation](https://docs.streamlit.io/)
* [Plotly Documentation](https://plotly.com/python/)
* [Pandas Documentation](https://pandas.pydata.org/)
* Tanenbaum & Van Steen — *Distributed Systems*
* Coulouris et al. — *Distributed Systems*

## 📝 Conclusion

The **Distributed Crime Data Analysis System (DCDAS)** demonstrates how distributed computing concepts can be applied to process large-scale datasets efficiently.

By using a **Master–Worker architecture, parallel processing, data partitioning, load balancing, fault tolerance, and compressed network communication**, the system provides a practical implementation of Parallel and Distributed Computing concepts along with real-time crime data analytics.
