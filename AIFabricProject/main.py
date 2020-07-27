from sklearn.externals import joblib
import json


class Main(object):

    def __init__(self):
        self.model = joblib.load('SMSClassifier.pkl')

    def predict(self,texts,features_names=None):

        #X = json.loads(X)

        # Use the model's tokenizer to tokenize each input text
        docs = [self.model.tokenizer(text) for text in texts]
    
        # Use textcat to get the scores for each doc
        textcat = self.model.get_pipe('textcat')
        scores, _ = textcat.predict(docs)
    
        # From the scores, find the class with the highest score/probability
        predicted_class = scores.argmax(axis=1)

        #print([textcat.labels[label] for label in predicted_class])

        return json.dumps([textcat.labels[label] for label in predicted_class])

#cls = Main()
#print(cls.predict(["U dun say so early hor... U c already then say...","England v Macedonia - dont miss the goals/team news. Txt ur national team to 87077 eg ENGLAND to 87077 Try:WALES, SCOTLAND 4txt/Ì¼1.20 POBOXox36504W45WQ 16+"]))
if __name__ == '__main__':
   # Test the ML Package locally
   obj = Main()
   print(obj.predict(["U dun say so early hor... U c already then say...","England v Macedonia - dont miss the goals/team news. Txt ur national team to 87077 eg ENGLAND to 87077 Try:WALES, SCOTLAND 4txt/Ì¼1.20 POBOXox36504W45WQ 16+"]))