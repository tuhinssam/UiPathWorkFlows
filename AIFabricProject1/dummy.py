from sklearn.externals import joblib
import json
SMSClassifier = joblib.load('SMSClassifier.pkl')

#predict using the trained model
def predict(model, texts): 
    #texts = json.loads(texts)
    # Use the model's tokenizer to tokenize each input text
    docs = [model.tokenizer(text) for text in texts]
    
    # Use textcat to get the scores for each doc
    textcat = model.get_pipe('textcat')
    scores, _ = textcat.predict(docs)
    
    # From the scores, find the class with the highest score/probability
    predicted_class = scores.argmax(axis=1)

    return json.dumps([textcat.labels[label] for label in predicted_class])

textcat = SMSClassifier.get_pipe('textcat')
predictions = predict(SMSClassifier, ["Are you ready for the tea party????? It's gonna be wild",
         "FreeMsg Hey there darling it's been 3 week's now and no word back! I'd like some fun you up for it still? Tb ok! XxX std chgs to send, å£1.50 to rcv"])
print(predictions)