#This script evaluates Claude's predictions against our ground_truth
#Metrics:
#Accuracy - How many did Claude get right
#Precision - Out of the "attacks" as predicted by Claude, how many were right?
#Recall - Out of all the real attacks from the dataset, how many did Claude claim right?
#F1 score - Overall balance of precision and recall

import json
from sklearn.metrics import precision_score, accuracy_score, f1_score, recall_score, classification_report

records =[]
with open("results/classifications.jsonl", "r") as f:
    for row in f:
        records.append(json.loads(row))

#Extracting ground truth and prediction from records[]. records[] is basically the classifications.jsonl returned by Claude
y_true =[]
y_pred = []

for r in records:
    groundTruth = str(r["ground_truth"]["is_attack"]).lower()
    ClaudePred = r.get("prediction",{})

    if "error" in ClaudePred:
        continue

    y_true.append(groundTruth)
    y_pred.append(str(ClaudePred.get("is_attack", "false")).lower())#Conversion is done for matching the values

#Printing the metrics
print(f"Total evaluated: {len(y_true)}")
print(f"Accuracy: {accuracy_score(y_true, y_pred):.2%}")
print(f"Precision: {precision_score(y_true, y_pred, pos_label='true'):.2%}")
print(f"Recall: {recall_score(y_true, y_pred, pos_label='true'):.2%}")
print(f"F1 Score: {f1_score(y_true, y_pred, pos_label='true'):.2%}")
print("\nFull Report:")
print(classification_report(y_true, y_pred))