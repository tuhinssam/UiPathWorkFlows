from sklearn.externals import joblib
import json
SMSClassifier = joblib.load('SMSClassifier.pkl')

#predict using the trained model
def predict(model, texts): 
    #texts = json.loads(texts)
    #print(texts)
    # Use the model's tokenizer to tokenize each input text
    docs = [model.tokenizer(text) for text in texts]
    print(docs)
    
    # Use textcat to get the scores for each doc
    textcat = model.get_pipe('textcat')
    scores, _ = textcat.predict(docs)
    
    # From the scores, find the class with the highest score/probability
    predicted_class = scores.argmax(axis=1)

    return json.dumps([textcat.labels[label] for label in predicted_class])

def predict1(model, X):
    #X = json.loads(X)

    textcat = model.get_pipe('textcat')
    # Use the model's tokenizer to tokenize each input text
    doc = model.tokenizer(X)
    
    # Use textcat to get the scores for each doc
    scores, _ = textcat.predict([doc])
    
    # From the scores, find the class with the highest score/probability
    predicted_class = scores.argmax(axis=1)

    #print([textcat.labels[label] for label in predicted_class])

    return json.dumps(textcat.labels[predicted_class])


predictions = predict(SMSClassifier, ["Are you ready for the tea party????? It's gonna be wild"])
print(predictions)

