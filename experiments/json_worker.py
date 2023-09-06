import json, requests

data = {"president": {"name": "Zaphod Beeblebrox", "species": "Betelgeusian"}}

with open("data.json", "w") as write_file:
    json.dump(data, write_file)

string = json.dumps(data, indent=4, separators=(", ", ": "))
print(string)

with open("data.json", "r") as read_file:
    data = json.load(read_file)

print(data)

response = requests.get("https://jsonplaceholder.typicode.com/todos")
todos = json.loads(response.text)
print(todos)

print(type(todos))
    