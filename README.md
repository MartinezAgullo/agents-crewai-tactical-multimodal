agents-crewai-tactical-multimodal
=================================

This project is a demonstration of a multi-agent system built with the CrewAI framework. The system is designed to simulate a tactical military analysis pipeline.

It takes a text-based field report as input and a crew of specialized AI agents performs the following tasks:

1.  **Threat Analysis:** Identifies and lists hostile entities from the report.

2.  **Situation Report:** Formats the analysis into a professional, concise report.

3.  **Tactical Response:** Suggests a strategic and well-reasoned response to the identified threats.

The outputs of each step are saved to a dedicated output folder for review.

Setup and Installation
----------------------

Follow these steps to set up the project and install the necessary dependencies.

1.  **Python Version**: This project was developed and tested with **Python 3.11.9**. It's recommended to use this version or a compatible one, as it's well-suited for the AI/ML ecosystem.

2.  **Create Environment File**: In the root directory of your project, create a file named `.env` and add your OpenAI API key:

    ```
    OPENAI_API_KEY=your_key_here

    ```

3.  **Set up the `uv` Environment**: First, create a new virtual environment and then activate it.

    ```
    uv venv
    source .venv/bin/activate

    ```

4.  **Install Dependencies**: Use `uv` to install the required Python packages from the `pyproject.toml` file:

    ```
    uv pip install

    ```

How to Run
----------

After completing the setup, you can run the crew from the root directory with the following command:

```
uv run python src/main.py

```

The terminal will display the agents' thought processes, and the final output will be saved as markdown files in the `output/` directory.