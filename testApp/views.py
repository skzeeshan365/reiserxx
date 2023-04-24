from datetime import datetime
import pandas as pd
import re
import joblib
from django.shortcuts import render

# Load the pre-trained model
multi_model = joblib.load(r'C:\Users\zeeshan\PycharmProjects\djangoProject1\testApp\multi.joblib')


def predict(request):
    if request.method == 'POST':
        # Get the user input from the form
        message = request.POST.get('message')
        timestamp = datetime.now()

        # Preprocess the input data
        # Replace any URLs with a special token
        message = re.sub(r'http\S+', 'URL', message)

        # Replace any numbers with a special token
        message = re.sub(r'\d+', 'NUM', message)

        # Convert all text to lowercase
        message = message.lower()

        # Create a pandas DataFrame with the preprocessed data
        input_data = pd.DataFrame({'message': [message], 'timestamp': [timestamp]})

        # Compute length of message
        input_data['message_length'] = input_data['message'].apply(len)

        # Compute time elapsed between current message and previous message
        input_data['time_elapsed'] = (
                    input_data['timestamp'] - input_data['timestamp'].shift(1)).dt.total_seconds().fillna(0)

        # Label multitasking behavior
        input_data['multitasking'] = ((input_data['time_elapsed'] < 5) & (input_data['sender'] != input_data['sender'].shift(1))).astype(int)

        # Reorder columns to match the training data
        input_data = input_data[['message', 'message_length', 'time_elapsed', 'multitasking']]

        # Use the loaded model to make a prediction
        prediction = multi_model.predict(input_data)

        # Render the prediction result to the user
        return render(request, 'prediction.html', {'prediction': prediction})
    else:
        return render(request, 'form.html')
