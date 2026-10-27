"""A tiny stand-in for LeRobot, used ONLY when the real one is not installed (it needs Python 3.12+).

It copies the contract from LeRobot's own source (robots/robot.py, teleoperators/teleoperator.py) and its
"Bring Your Own Hardware" guide: the same abstract members and the same register_subclass registry. CI runs
the same tests against the real LeRobot, so any drift between this file and LeRobot shows up there.
"""
