from sklearn.externals import joblib
import json


class Main(object):

    def __init__(self):
        self.model = joblib.load('SMSClassifier.pkl')

    def predict(self,X,features_names=None):

        #X = json.loads(X)

        textcat = self.model.get_pipe('textcat')

        # Use the model's tokenizer to tokenize each input text
        docs = [self.model.tokenizer(text) for text in X]
    
        # Use textcat to get the scores for each doc
        scores, _ = textcat.predict(docs)
    
        # From the scores, find the class with the highest score/probability
        predicted_class = scores.argmax(axis=1)

        #print([textcat.labels[label] for label in predicted_class])

        return json.dumps([textcat.labels[label] for label in predicted_class])