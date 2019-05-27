import json

def test_json():
    print 'start'
    f= open("static/test.json","r")
    txt = f.read()
    f.close()
    myObj = json.loads(txt)
    print json.JSONEncoder().encode(myObj)
