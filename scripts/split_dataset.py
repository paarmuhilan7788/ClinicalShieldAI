import json
import random

#Loading the json file
with open("data/attacks_v1.json") as f:
    data = json.load(f)

#Splitting the data into attack list and legitimate list. This is based on the column is_attack==True/False
attack_rows = [r for r in data if r["is_attack"] == "true"]
legit_rows = [r for r in data if r["is_attack"] == "false"]

#Shuffling both the lists so that the split isn't ordered
random.shuffle(attack_rows)
random.shuffle(legit_rows)

#Split - 80/20
attack_split = int(len(attack_rows) * 0.8) #determines where to terminate the list
legit_split = int(len(legit_rows) * 0.8) #same as above

attack_train = attack_rows[:attack_split]
attack_test = attack_rows[attack_split:]
legit_train = legit_rows[:legit_split]
legit_test = legit_rows[legit_split:]

#Combining the training and testing data
train_data = attack_train + legit_train
test_data = attack_test + legit_test

#Re-shuffling
random.shuffle(train_data)
random.shuffle(test_data)

#Saving as train and test
with open("data/attack_train.json", "w") as f:
    json.dump(train_data, f , indent=2)

with open("data/attack_test.json", "w") as f:
    json.dump(test_data, f, indent=2)

print(f"no.of rows for training : {len(train_data)}")
print(f"no.of rows for testing : {len(test_data)}")
print(f"Combined tally : {len(train_data) + len(test_data)}")