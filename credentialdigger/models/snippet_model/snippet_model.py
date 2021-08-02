import tensorflow as tf
from ..base_model import BaseModel


class SnippetModel(BaseModel):

    def __init__(self,
                 model='melisande1/pw1',
                 tokenizer='microsoft/codebert-base-mlm'):
        """ This class classifies a discovery as a false positive according to
        its code snippet.
        """
        super().__init__(model, tokenizer, local_files_only)

    def analyze(self, discoveries):
        """ Analyze a snippet and predict whether it is a leak or not.

        Parameters
        ----------
        discoveries: list of dict
            The discoveries
        """
        snippets = [d['snippet'] for d in discoveries if d['state'] != 'false_positive']
        data = self.preprocess_data(snippets)
        outputs = self.model.predict(data)
        logits = outputs['logits']
        predictions = tf.argmax(logits, 1)
        n_false_positives = 0
        for d, p in zip(discoveries, predictions):
            if p == 0:
                d['state'] = 'false_positive'
                n_false_positives += 1
        return discoveries, n_false_positives

    def preprocess_data(self, snippets):
        encodings = self.tokenizer(snippets, truncation=True, padding=True)
        features = {x: encodings[x] for x in self.tokenizer.model_input_names}
        dataset = tf.data.Dataset.from_tensor_slices((features)).batch(8)
        return dataset
