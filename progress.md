Project Progress Template

Project Title
(Try to choose a catchy title. Max 20 words).

ResGuard: Dynamic Resource Management System

Student/Team Information

Team Name:Team # (Mentor needs to assign)

Team member 1 (Team Lead)(Lakshya Kumar: student ID: email, picture):
Team member 2(Chitrance Dogra: student ID: email, picture):
Team member 3(Aman Rana: student ID: email, picture):
Team member 4(Anshuman Riar: student ID: email, picture):
(Please fill in student IDs, emails, and picture details)

Project Abstract (2 pts)
(Brief restatement of your project’s main goal. Max 300 words).

ResGuard is a dynamic resource management system designed to monitor and control system resources (CPU, memory, disk, network) effectively. It aims to prevent system overloads and ensure fair resource distribution among concurrent tasks, potentially utilizing Banker's Algorithm for safe state checking. The system features a desktop application for detailed monitoring and management, a web dashboard for remote oversight, a configurable alerting system to notify users of critical resource levels, and an auto-scaling mechanism to adapt to varying workloads. The goal is to provide a robust and user-friendly platform for managing system resources efficiently.

Updated Project Approach and Architecture (2 pts)
(Describe your current approach, including system design, communication protocols, libraries used, etc. Max 300 words).

The system is built with a modular Python backend.
**System Design:**
-   `SystemMonitor`: Uses `psutil` for real-time collection of CPU, memory, disk, and network metrics.
-   `ResourceManager`: Manages resource allocation, likely implementing Banker's algorithm for deadlock avoidance.
-   `ThreadManager`: Handles concurrent execution of tasks, ensuring they request and release resources through the `ResourceManager`.
-   `AlertingSystem`: Monitors resource usage against user-defined thresholds and generates alerts.
-   `AutoScaler`: (Optional, if fully implemented) Adjusts resource allocations based on predefined rules or reactive monitoring.
-   `Config`: Manages system configuration via a `config.json` file, allowing customization of various parameters.
-   **Desktop Application**: Built with `tkinter`, providing a GUI for monitoring, resource requests, and settings management.
-   **Web Dashboard**: Built with `Flask` and `Dash`/`Plotly` for remote monitoring.

**Communication Protocols:** Internal components interact via Python object methods. The web dashboard uses HTTP/S.

**Libraries Used:** `psutil`, `tkinter`, `Flask`, `Dash`, `Plotly`, `numpy`, `pandas`, `requests`, `jinja2`.

Tasks Completed (7 pts)
(Describe the main tasks that have been assigned and already completed. Max 250 words).

Task Completed                               | Team Member
---------------------------------------------|------------------------------------
Core System Monitoring (`SystemMonitor`)     | (Assign Member)
Core Resource Management Logic (`ResourceManager`) | (Assign Member)
Concurrent Task Management (`ThreadManager`)   | (Assign Member)
Alerting System (`AlertingSystem`)           | (Assign Member)
Configuration Management (`Config`)          | (Assign Member)
Desktop App: Main UI & Dashboard             | (Assign Member)
Desktop App: Login & Settings Dialogs        | (Assign Member)
Web Dashboard: Basic Structure & Login       | (Assign Member)
Project Setup & Dependency Management        | (Assign Member)
Initial implementation of Auto-Scaling       | (Assign Member)

Challenges/Roadblocks (7 pts)
(Describe the challenges that you have faced or are facing so far and how you plan to solve them. Max 300 words).

(To be identified and detailed by the team. Examples:
-   Complexity in ensuring thread safety for resource management.
-   Integrating diverse UI components smoothly.
-   Designing an effective and non-intrusive alerting mechanism.
-   Optimizing performance for real-time data display.)

Tasks Pending (7 pts)
(Describe the main tasks that you still need to complete. Max 250 words).

Task Pending                                     | Team Member (to complete the task)
-------------------------------------------------|------------------------------------
Web Dashboard: Full Interactive Features         | (Assign Member)
Comprehensive Unit & Integration Testing         | (Assign Member)
End-to-End System Testing                        | (Assign Member)
Refinement of Auto-Scaling Logic & Rules         | (Assign Member)
Advanced Alerting Notifications (e.g., email)    | (Assign Member)
Detailed User and Developer Documentation        | (Assign Member)
Performance Optimization & Bug Fixing            | (Assign Member)
User Acceptance Testing (UAT)                    | (Assign Member)
Final Packaging and Deployment Strategy          | (Assign Member)

Project Outcome/Deliverables (2 pts)
(Describe what are the key outcomes / deliverables of the project. Max 200 words).

-   A fully functional ResGuard application providing dynamic resource management.
-   A user-friendly desktop application for real-time system monitoring, resource allocation, and configuration.
-   A web-based dashboard for remote monitoring of system status.
-   An integrated alerting system to notify users of critical resource conditions.
-   (If fully implemented) An auto-scaling feature to adapt to resource demands.
-   Complete source code hosted on a Git repository.
-   Comprehensive project documentation, including user and developer guides.

Progress Overview (2 pts)
(Summarize how much of the project is done, what's behind schedule, what's ahead of schedule. Max 200 words).

The project has made significant progress, with core backend functionalities (monitoring, resource management, task handling, alerting, configuration) largely implemented. The desktop application provides a robust interface for most features. The web dashboard's foundational elements are in place.
Key areas for upcoming focus include completing the web dashboard's interactivity, thorough testing across all modules, and refining advanced features like auto-scaling. Documentation and final polish are also pending.
(Team to specify if any parts are ahead or behind schedule).

Codebase Information (2 pts)
(Repository link, branch, and information about important commits.)

-   **Repository Link**: https://github.com/lakshyakumar90/Resguard--Resource-Management-System
-   **Branch**: (e.g., `main`, `develop` - Please specify current primary branch)
-   **Important Commits**: (Team to list a few key commits, e.g., "Implemented core alerting module", "Initial desktop UI integration")

Testing and Validation Status (2 pts)
(Provide information about any tests conducted)

Test Type                     | Status
------------------------------|--------------------------------------------------------------------
Configuration Validation      | Implemented (via `Config.validate()`)
Unit Tests                    | (To be detailed by team - e.g., In Progress, Partially Complete)
Integration Tests             | (To be detailed by team - e.g., Planned, Partially Complete)
Desktop UI Testing (Manual)   | (To be detailed by team - e.g., Ongoing)
Web Dashboard Testing (Manual)| (To be detailed by team - e.g., Planned)
End-to-End (E2E) Testing      | (To be detailed by team - e.g., Planned)

(Please provide more specific details on the status of each test type, tools used if any, and key findings.)



