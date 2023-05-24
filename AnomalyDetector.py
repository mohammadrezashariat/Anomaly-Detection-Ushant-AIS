import os
from abc import ABC, abstractmethod
from sklearn.mixture import GaussianMixture
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import layers, losses
from keras.models import load_model
import joblib

class AnomalyDetector(ABC):
    """Abstract base class for anomaly detection models"""

    @abstractmethod
    def load_scaler(self):
        """Load the scaler"""
        pass
    
    @abstractmethod
    def save_model(self):
        """Save the trained model to a file"""
        pass

    @abstractmethod
    def determine_threshold(self):
        """Determine the anomaly threshold based on the training data"""
        pass

    @abstractmethod
    def build_model(self):
        """Build the anomaly detection model"""
        pass

    @abstractmethod
    def train_model(self):
        """Train the anomaly detection model"""
        pass

    @abstractmethod
    def load_model(self):
        """Load the GMM model"""
        pass

    @abstractmethod
    def detect_anomalies(self):
        """Detect anomalies in the given data"""
        pass


class GMM(AnomalyDetector):
    """Anomaly detection model using Gaussian Mixture Models (GMM)"""

    def __init__(self, dataset_name):
        self.threshold = None
        self.model = None
        self.model_name = 'GMM_location.pkl' if dataset_name == 'location' else 'GMM_velocity.pkl'
        self.scaler_name = 'location_scaler.pkl' if dataset_name == 'location' else 'velocity_scaler.pkl'

    def load_scaler(self):
        """Load the scaler"""
        try:
            self.scaler = joblib.load(os.path.join(os.getcwd(), self.scaler_name))
            print("Scaler loaded successfully.")
        # Model not found
        except FileNotFoundError:
            print("Scaler file not found.")
        # Loading error
        except Exception as e:
            print("An error occurred while loading the scaler:", str(e))

    def save_model(self):
        """
        Save the trained GMM model to a file.

        Args:
            model_path (str): Path to save the model.

        Returns:
            None
        """
        # Save the GMM model
        joblib.dump(self.model, os.path.join(os.getcwd(), self.model_name))

    def determine_threshold(self, X_train):
        """
        Determine the anomaly threshold based on the training data.

        Args:
            X_train (array-like): Training data.

        Returns:
            None
        """  
        # calculates the log-likelihood of the given samples
        # log-likelihood represents the probability of the samples being generated by the GMM.
        scores = self.model.score_samples(X_train)

        # Set a threshold for anomaly detection
        self.threshold = np.mean(scores) + np.std(scores)

    def build_model(self, n_components=1):
        """
        Build the GMM model.

        Args:
            n_components (int): number of Gaussian components or clusters that will be used to model the data.

        Returns:
            None
        """
        self.model = GaussianMixture(n_components)

    def train_model(self, X_train):
        """
        Train the GMM model.

        Args:
            None

        Returns:
            None
        """
        print("Training model...")

        # train model
        self.model.fit(X_train)

        # save model
        self.save_model()

        # create threshold
        self.determine_threshold(X_train)
        print(f"GMM threshold: {self.threshold}")

    def load_model(self):
        """Load the GMM model"""
        # Load GMM Model
        try:
            self.model = joblib.load(os.path.join(os.getcwd(), self.model_name))
            print("GMM model loaded successfully.")
        # Model not found
        except FileNotFoundError:
            print("GMM model file not found.")
        # Loading error
        except Exception as e:
            print("An error occurred while loading the GMM model:", str(e))

    def detect_anomalies(self, X):
        """
        Detect anomalies using the trained GMM model.

        Args:
            X (array-like): Input data.

        Returns:
            array-like: Anomaly scores.
        """
        # Load scaler
        self.load_scaler()

        # normalize data
        X = self.scaler.fit_transform(X)

        if self.model is None:
            print("Model not trained. Trying to load the model...")
            self.load_model()
        else:
            pass
        
        # predict Log_lokihood
        scores = self.model.score_samples(X)

        # make prediction for new data
        for index, score in enumerate(scores):
            if score > self.threshold:
                print(f"{X[index]} Data point at index {index} is Normal")
            else:
                print(f"{X[index]} Data point at index {index} is Abnormal !!!")


class DeepLearning(AnomalyDetector):
    """Anomaly detection model using Deep Learning"""

    def __init__(self, dataset_name):
        self.threshold = None
        self.model = None
        self.model_name = 'DL_location_model.h5' if dataset_name == 'location' else 'DL_velocity_model.h5'
        self.scaler_name = 'location_scaler.pkl' if dataset_name == 'location' else 'velocity_scaler.pkl'

    def load_scaler(self):
        """Load the scaler"""
        try:
            self.scaler = joblib.load(os.path.join(os.getcwd(), self.scaler_name))
            print("Scaler loaded successfully.")
        # Model not found
        except FileNotFoundError:
            print("Scaler file not found.")
        # Loading error
        except Exception as e:
            print("An error occurred while loading the scaler:", str(e))

    def save_model(self):
        """
        Save the trained Deep learning model to a file.

        Args:
            model_path (str): Path to save the model.

        Returns:
            None
        """
        # Save the model
        self.model.save(os.path.join(os.getcwd(), self.model_name))

    def determine_threshold(self, X_train):
        """
        Determine the anomaly threshold based on the training data.

        Args:
            X_train (array-like): Training data.

        Returns:
            None
        """
        # Generate reconstructions of the input data using the trained model
        reconstructions = self.model.predict(X_train)

        # Calculate the mean squared error between the input data and its reconstructions
        errors = (tf.keras.losses.mae(X_train, reconstructions)).numpy()

        # Calculate the anomaly threshold based on the mean and standard deviation of the errors
        self.threshold = np.mean(errors) + np.std(errors)

    def build_model(self, input_dim):
        """
        Build the Deep Learning model.

        Args:
            input_dim (tuple): Shape of the input data.

        Returns:
            None
        """
        self.model = tf.keras.Sequential([
                            layers.Dense(32, activation='relu', input_shape=(input_dim,)),
                            layers.Dense(16, activation='relu'),
                            layers.Dense(8, activation='relu'),
                            layers.Dense(16, activation='relu'),
                            layers.Dense(32, activation='relu'),
                            layers.Dense(input_dim, activation='sigmoid')
                        ])

    def train_model(self, X_train, X_test, epochs=10, batch_size=512, optimizer='adam', loss='mae'):
        """
        Train the Deep Learning model.

        Args:
            X_train (array-like): Training data.
            X_test (array-like): Test data.
            epochs (int): Number of training epochs.
            batch_size (int): Training batch size.
            optimizer (str): Training optimizer.
            loss (str): Loss function.

        Returns:
            None
        """
        # compile model
        self.model.compile(optimizer=optimizer, loss=loss)

        # train model
        print("Training model...")
        history = self.model.fit(X_train, X_train, 
                                 epochs=epochs, 
                                 batch_size=batch_size, 
                                 validation_data=(X_test, X_test))

        # save model
        self.save_model()

         # create threshold
        self.determine_threshold(X_train)
        print(f"Deep learning threshold: {self.threshold}")
        return history

    def load_model(self):
        """Load the model"""

        try:
            self.model = load_model(os.path.join(os.getcwd(), self.model_name))
            print("Deep Learning model loaded successfully.")

        # Model not found
        except FileNotFoundError:
            print("Deep Learning model file not found.")

        # Loading error
        except Exception as e:
            print("An error occurred while loading the Deep Learning model:", str(e))

    def detect_anomalies(self, X):
        """
        Detect anomalies using the trained Deep Learning model.

        Args:
            X (array-like): Input data.

        Returns:
            array-like: Anomaly scores.
        """
        # Load scaler
        self.load_scaler()

        # normalize data
        X = self.scaler.fit_transform(X)

        if self.model is None:
            print("Model not trained. Trying to load the model...")
            self.load_model()
        else:
            pass

        reconstructions = self.model.predict(X)
        errors = tf.keras.losses.mean_squared_error(X, reconstructions)

        for index, error in enumerate(errors):
            if error > self.threshold:
                print(f"Data point at index {index} is Abnormal")
            else:
                print(f"Data point at index {index} is Normal")


############################ Factory Design Pattern ############################
"""
After defining the abstract base class AnomalyDetector and implementing the 
concrete classes GMM and DeepLearning that inherit from it, the next step 
would be to create an Anomaly Detector Factory class. The factory class will be 
responsible for creating instances of the appropriate anomaly detector based on 
the provided configuration or parameters.
"""

class AnomalyDetectorFactory:
    @staticmethod
    def anomaly_detector(detector_type, dataset_name):
        """
        Create an instance of the appropriate anomaly detector based on the detector_type.

        Args:
            detector_type (str): Type of anomaly detector.

        Returns:
            AnomalyDetector: Instance of the anomaly detector.

        Raises:
            ValueError: If an invalid anomaly detector type is provided.
        """
        # Create an instance of GMM anomaly detector
        if detector_type == 'classic':
            return GMM(dataset_name)  
        
        # Create an instance of Deep Learning anomaly detector
        elif detector_type == 'deep_learning':
            return DeepLearning(dataset_name)  

        # Raise an error for invalid detector type
        else:
            raise ValueError(f"Invalid anomaly detector type: {detector_type}")  