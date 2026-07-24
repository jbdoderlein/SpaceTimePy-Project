#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
declare -A CODE_TOTALS=()

if ! command -v cloc >/dev/null 2>&1; then
    echo "Error: cloc is not installed or is not available in PATH." >&2
    exit 1
fi

section() {
    printf '\n============================================================\n'
    printf '%s\n' "$1"
    printf '============================================================\n'
}

language_summary() {
    cloc --quiet --csv "$@" |
        awk -F, '
            $2 == "Python" { python += $5 }
            $2 == "TypeScript" { typescript += $5 }
            $2 == "JavaScript" { javascript += $5 }
            END {
                separator = ""
                if (python > 0) {
                    printf "%d(Python)", python
                    separator = " + "
                }
                if (typescript > 0) {
                    printf "%s%d(TS)", separator, typescript
                    separator = " + "
                }
                if (javascript > 0) {
                    printf "%s%d(JS)", separator, javascript
                    separator = " + "
                }
                if (separator == "") {
                    printf "0"
                }
                printf "\n"
            }
        '
}

count_files() {
    local title="$1"
    shift

    local files=("$@")
    local file
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "Error: expected source file not found: $file" >&2
            exit 1
        fi
    done

    section "$title"
    cloc --quiet "${files[@]}"
    CODE_TOTALS["$title"]="$(language_summary "${files[@]}")"
}

section "Core library"
cloc --quiet "$PROJECT_ROOT/SpaceTimePy/src"
CODE_TOTALS["Core library"]="$(language_summary "$PROJECT_ROOT/SpaceTimePy/src")"

# Pygame
#
# gameexplorer.py owns the Tk/Pillow/code-view presentation. The remaining
# production modules adapt Pygame capture, values, execution, and replay to
# SpaceTimePy.
count_files "Pygame — SpaceTime adaptation" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/__init__.py" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/decorators.py" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/picklers.py" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/replay.py" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/utils.py"

count_files "Pygame — visualization/UI" \
    "$PROJECT_ROOT/spacetimepy-pygame/src/spacetimepy_pygame/gameexplorer.py"

# Notebook + sampling workflow
#
# The two SamplingMiningWorkflowDSL files are the domain-side SpaceTime
# adaptation introduced for recording/replaying workflows. Jupyter kernel
# templates and combination logic form the notebook-to-SpaceTime bridge.
# generated/kernel-sources.ts is deliberately excluded because it is generated
# from the Python templates below and would count the same implementation twice.
count_files "Notebook + sampling — SpaceTime adaptation" \
    "$PROJECT_ROOT/SamplingMiningWorkflowDSL/src/sampling_mining_workflows_dsl/SpaceTimeWorkflowBuilder.py" \
    "$PROJECT_ROOT/SamplingMiningWorkflowDSL/src/sampling_mining_workflows_dsl/operator/SpaceTimeOperatorBuilder.py" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/spacetimepy_jupyterlab/__init__.py" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/combinations.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/kernel-code.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/kernel/finish-workflow-recording.py" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/kernel/reexecute-variant.py" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/kernel/trace-query.py" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/kernel/workflow-summary.py"

count_files "Notebook + sampling — visualization/UI" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/index.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/trace-tree.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/trace-view.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/src/types.ts" \
    "$PROJECT_ROOT/spacetimepy-jupyterlab/style/index.css"

# VS Code
#
# Extension lifecycle, API/database management, debugger integration, capture,
# source discovery, and the bundled Python runtime are adaptation code.
# CodeLens providers and trace timeline/panel rendering are presentation code.
count_files "VS Code — SpaceTime adaptation" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/api.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/config.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/database.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/debuggerHotswap.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/extension.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/functionCapture.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/pythonFunctions.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/serverManager.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/types.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/python/spacetimepy_vscode_runtime/__init__.py" \
    "$PROJECT_ROOT/spacetimepy-vscode/python/spacetimepy_vscode_runtime/hotswap.py" \
    "$PROJECT_ROOT/spacetimepy-vscode/python/spacetimepy_vscode_runtime/launch.py" \
    "$PROJECT_ROOT/spacetimepy-vscode/python/spacetimepy_vscode_runtime/replay.py"

count_files "VS Code — visualization/UI" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/functionLaunchCodeLens.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/recordedExecutionCodeLens.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/traceExplorerPanel.ts" \
    "$PROJECT_ROOT/spacetimepy-vscode/src/traceTimeline.ts"

section "Code-line summary"
printf '%-24s %22s %22s\n' \
    "Domain" "SpaceTime adaptation" "Visualization/UI"
printf '%-24s %22s %22s\n' \
    "Core library" "${CODE_TOTALS["Core library"]}" "-"
printf '%-24s %22s %22s\n' \
    "Pygame" \
    "${CODE_TOTALS["Pygame — SpaceTime adaptation"]}" \
    "${CODE_TOTALS["Pygame — visualization/UI"]}"
printf '%-24s %22s %22s\n' \
    "Notebook + sampling" \
    "${CODE_TOTALS["Notebook + sampling — SpaceTime adaptation"]}" \
    "${CODE_TOTALS["Notebook + sampling — visualization/UI"]}"
printf '%-24s %22s %22s\n' \
    "VS Code" \
    "${CODE_TOTALS["VS Code — SpaceTime adaptation"]}" \
    "${CODE_TOTALS["VS Code — visualization/UI"]}"

section "Counting policy"
cat <<'EOF'
Production source only. Tests, documentation, dependency lockfiles, compiled
output, vendored dependencies, and generated duplicate sources are excluded.
Each application source file appears in exactly one category. The final summary
counts only Python, TypeScript, and JavaScript; detailed sections still show
every language detected by cloc.
EOF
