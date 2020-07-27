import pandas as pd 
import joblib
import os

class Main(object): 
   def __init__(self):
       self.model_path = './SMSClassifier.pkl' 
       self.model = joblib.load(self.model_path)
      
   def train(self, training_directory):
       (X,y) = self.load_data(os.path.join(training_directory, 'train.csv'))
       self.model.fit(X,y)

   def evaluate(self, evaluation_directory):
       (X,y) = self.load_data(os.path.join(evaluation_directory, 'evaluate.csv'))
       return self.model.score(X,y)

   def save(self):
       joblib.dump(self.model, self.model_path)

   def load_data(self, path):
       # The last column in csv file is the target column for prediction.
       df = pd.read_csv(path)
       X = df.iloc[:, :-1].get_values()
       y = df.iloc[:, 'y'].get_values()
       return X,y