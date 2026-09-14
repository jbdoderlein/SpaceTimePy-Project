# Live workflow validation

Date: 2026-09-14. Related issue: https://github.com/jbdoderlein/SpaceTimePy-Project/issues/1.

The integration tests use real DSL operators, real SpaceTime checkpoints, and the extension's Python request templates.
The workflow contains a commit filter, a language filter, and seeded random sampling.
The tests count operator executions, input loads, and output writes.

| Action | Commit filter | Language filter | Sampling | Input loads | Output writes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial live execution | 1 | 1 | 1 | 1 | 1 |
| Change sample size | 0 | 0 | 1 | 0 | 1 |
| Change language filter | 0 | 1 | 1 | 0 | 1 |
| Change commit filter | 1 | 1 | 1 | 0 | 1 |
| Read recorded history | 0 | 0 | 0 | 0 | 0 |

The tests also check these results:

- Resumed output equals fresh output with the same explicit seed.
- The restored sampling checkpoint contains the computed filtered elements.
- Child execution preserves the original workflow results and the parent checkpoint.
- Multiple changes start execution at the earliest changed operator.
- An edit after branch selection uses the selected branch as its parent.
- Invalid source, unsupported edits, and failed execution preserve successful history.
- A later valid edit succeeds after a failed execution.
- Ordinary workflow execution does not create a live recording.

Four Python tests passed, including a test in a real IPython kernel.
The kernel test checks the MIME signal, source attachment, child replay, stage size, and branch connection.
Four TypeScript tests passed. These tests check branch restoration without kernel execution, request ordering, stale responses, invalid-source handling, and restart cleanup.
The extension build passed.

The visual JupyterLab interaction check remains incomplete.
JupyterLab started with the extension enabled, but the computer-use tool reported that no browser was available.
No performance measurements or paper changes form part of this validation.
