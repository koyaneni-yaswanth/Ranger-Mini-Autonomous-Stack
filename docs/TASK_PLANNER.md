# Hierarchical Task Planning & Ambiguity Resolution

## 1. Hierarchical Task Network (HTN)
High-level semantic requests are decomposed into ordered Directed Acyclic Graphs (DAGs) of executable subtasks:
```text
"Find the red cube, pick it up, and place it on the table"
  1. LocateObject(color='red', class='cube')
  2. ApproachTarget(standoff=0.48m)
  3. Pick(class='cube')
  4. VerifyGrasp()
  5. Transport()
  6. NavigateToStation(station='target_station')
  7. Place(station='target_station')
  8. VerifyPlace()
  9. Dock()
```

## 2. Ambiguity Handling
If multiple items match a vague request (e.g. *"Bring me the box"* when a red box and a blue box are present), the planner returns an ambiguity alert:
*"I see two boxes (red box and blue box). Which one do you mean?"*
