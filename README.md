# Installation
1. Clone the repository.
```bash
git clone https://github.com/SorcierMaheP/OpenKuro.git
# OR via SSH
git clone git@github.com:SorcierMaheP/OpenKuro.git
```  
2. Ensure you navigate to the root folder of the cloned repo. Create a venv and activate it.
```bash
python -m venv <name_of_venv>
# Following activation command will change for Windows/MacOS or other shells
. <name_of_venv>/bin/activate
```
3. Install the requirements
```bash
pip install -r requirements.txt
```
4. Copy the default_workspace/config.example.yaml into default_workspace/config.user.yaml and add required information (model in litellm format, api key, api base url, etc).
```bash
cp default_workspace/config.example.yaml default_workspace/config.user.yaml
# Edit the user config yaml file
```
5. Make changes to AGENT.md files for different agents in default_workspace/agents folder, if needed.
6. Run the command to start a chat session.
```bash
python -m src.cli.main chat
```
# Baseline commits

This section links to specific baseline commits in the repository. Each commit represents a distinct stage in the development of the bot.

0. [Step 00 - Chat Loop](https://github.com/SorcierMaheP/OpenKuro/commit/fc6c38ffa267a1183ff739d84c4874b43a15fd42)

# Media

This folder contains screenshots of the chat session across different steps of building the bot.

These images are intended to help illustrate the workflow and outputs at various steps.