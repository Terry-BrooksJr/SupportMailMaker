
# SupportMailMaker

SupportMailMaker is an intelligent parser and formatter designed specifically for Learnosity SupportMail. It simplifies the process of structuring support emails by providing efficient parsing, templating, and formatting tools. This project aims to enhance productivity and ensure consistent communication within the support workflow.

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Docker Support](#docker-support)
6. [Contributing](#contributing)
7. [License](#license)
8. [Acknowledgments](#acknowledgments)

---

## Features

- **Efficient Parsing:** Automatically extracts and formats key details from Learnosity SupportMail.
- **Customizable Templates:** Allows you to define and use email templates tailored to your workflow.
- **Gradio UI Integration:** Provides a user-friendly interface for parsing and formatting operations.
- **Dockerized Deployment:** Includes a Docker setup for seamless deployment in any environment.

---

## Getting Started

Follow these instructions to set up the project on your local machine and get it running.

### Prerequisites

Ensure you have the following tools installed:

- Python 3.9 or higher
- Docker (optional but recommended)
- pip (Python package manager)

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Terry-BrooksJr/SupportMailMaker.git
   cd SupportMailMaker
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   python -m support_mail_maker
   ```

---

## Usage

### Command-Line Interface

You can use the CLI to parse and format Learnosity SupportMail:

```bash
python -m support_mail_maker --input example_email.txt --output formatted_email.txt
```

### Gradio Interface

To use the Gradio-based web interface:

1. Start the application:
   ```bash
   python -m support_mail_maker --gradio
   ```

2. Open the provided URL in your browser to access the interface.

---

## Docker Support

SupportMailMaker comes with a pre-configured Docker setup.

1. **Build the Docker Image:**
   ```bash
   docker build -t supportmailmaker .
   ```

2. **Run the Docker Container:** ***You must publish port 7500m and map it to the host machine***
   ```bash
   docker run -p 7860:7860 supportmailmaker
   ```

3. Access the Gradio interface at `http://localhost:7500`.


---

## Contributing

## Roadmap

- Full CLI with Go's CLI Libray Cobra
- Add Ability to upload a template 
---

## Contributing
We welcome contributions! To get started:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
4. Push the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.


---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Learnosity:** For providing the inspiration and use case for this project.
- **Gradio:** For the powerful UI framework.

Feel free to open an issue or contact us if you have questions or feedback! 🚀
