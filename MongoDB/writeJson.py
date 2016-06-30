def writeJson(filePath, oneLineDict):
    import json

    with open(filePath, 'a') as file:
        file.write(json.dumps(oneLineDict))
        file.write('\n')
