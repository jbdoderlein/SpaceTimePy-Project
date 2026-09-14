# SpaceTimePy-Project
A repo combining all SpaceTimePy related repo with VSCode configuration.


## Install

```bash
git clone --recurse-submodules https://github.com/jbdoderlein/SpaceTimePy-Project
cd SpaceTimePy-Project
uv venv
uv sync
source .venv/bin/activate
```

## Demos

### Pygame

First play the first game session to collect the initial trace :

```bash
cd demo
python flappy.py
```

Then you can launch the tool with

```bash
uv run -m spacetimepy_pygame.gameexplorer flappy.db
```

![Screenshot](img/pygame.png)

### Sampling Workflow (JupyterLab)

First start the jupyter-lab server

```bash
jupyter-lab demo/workflow.ipynb
```

Open `workflow.ipynb` in JupyterLab. Execute the setup cells and the workflow cell.
The SpaceTime side panel opens after `execute_live_workflow()`.
Edit an existing operator argument. Save the notebook to create a branch from its execution checkpoint.
Select a recorded branch to restore its source and results without execution.
Keep the input context, operator count, and operator order fixed.

![Screenshot](img/workflow.png)

### Omniscient Live Debugger (VSCode)

First start the vscode with extension inside

```bash
./launch_vscode .
```

Then open the file `demo/binary_search.py`

![Screenshot](img/vscode.png)

You can additionaly see the trace web explorer by launching : 

```bash
web-spacetimepy .vscode/spacetimepy.db --port 8001
```
