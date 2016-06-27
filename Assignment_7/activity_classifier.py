import csv
import numpy as np
from sklearn import svm
import itertools as it

"""
global identifier variables
"""

GESTURE_3 = "GESTURE_3"
GESTURE_2 = 'GESTURE_2'
GESTURE_1 = 'GESTURE_1'
NOTHING = 'NOTHING'


class TrainingsDataReader:
    @staticmethod
    def get_trainings_data(file):
        values = []

        with open(file, "r", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')

            i = 0
            ges_index = 0
            for row in reader:
                if i == 0:
                    i = 1
                    continue

                x, y, z = row[1:4]

                if int(row[0]) != ges_index:
                    values.append([])
                    ges_index += 1

                values[ges_index - 1].append([float(x), float(y), float(z)])

        return values


class Classifier:
    """
    class responsible for classifying activities
    """

    def __init__(self, file_path=None, train_data=None, activity=None):
        """
        constructor

        :param file_path: a potential path to a input csv file
        :param train_data: a potential array of accelerometer values
        :param activity: a potential name of an activity

        :return: void
        """

        if file_path is None and train_data is None:
            print("Classifier has no trainings data!\nNeeds csv file or array!")
            exit(0)
        else:
            self.data_gesture_1 = None
            self.data_gesture_2 = None
            self.data_gesture_3 = None

            self.data_gesture_1_class = []
            self.data_gesture_2_class = []
            self.data_gesture_3_class = []

            self.classifier = svm.SVC()
            self.train(file_path, train_data, activity)

    def __classify_gesture_1_(self, gesture_data):
        """
        classifies the shake activity

        :param gesture_data: the data which needs to be checked for the
               shaking activity

        :return: a boolean depicting whether gesture_1 occurred or did not occur
        """

        ges1, ges2, ges3 = self.__get_activity_occurrences_(gesture_data)

        return ges1 > ges2 and ges1 > ges3

    def __classify_gesture_2_(self, gesture_data):
        """
        classifies the whip activity

        :param gesture_data: the data which needs to be checked for the
               whipping activity

        :return: a boolean depicting whether gesture_2 occurred or did not occur
        """

        ges1, ges2, ges3 = self.__get_activity_occurrences_(gesture_data)

        return ges2 > ges1 and ges2 > ges3

    def __classify_gesture_3_(self, gesture_data):
        """
        classifies the wiggle activity

        :param gesture_data: the data which needs to be checked for the
               wiggling activity

        :return: a boolean depicting whether gesture_3 occurred or did not occur
        """

        ges1, ges2, ges3 = self.__get_activity_occurrences_(gesture_data)

        return ges3 > ges1 and ges3 > ges2

    def __get_activity_occurrences_(self, gesture_data):
        """
        returns the amount of occurrences of each possible activity in its
                prediction

        :param gesture_data: the data from which the occurrences are extracted

        :return: the occurrences for gesture_1, gesture_2
                 and gesture_3 predictions
        """

        prediction = self.__prediction_(gesture_data)

        if prediction is None:
            return 0, 0, 0

        ges1 = 0
        ges2 = 0
        ges3 = 0

        for i in prediction:
            if i == 1:
                ges1 += 1

            if i == 2:
                ges2 += 1

            if i == 3:
                ges3 += 1

        return ges1, ges2, ges3

    def __prediction_(self, gesture_data):
        """
        predicts the activity for each given sample

        :param gesture_data: the data of wiimote motion to be tested against
                             the trained classifier

        :return: a list of predicted activities or None if not enough samples
                 have been collected
        """

        sum_vals = []

        for i in range(0, len(gesture_data)):
            sum_vals.append([(gesture_data[i][0] +
                             gesture_data[i][1] +
                             gesture_data[i][2] -
                             3 * 512) / 3])

        if len(sum_vals) < 30:
            return None

        data = self.__perform_fft_(sum_vals)

        return self.classifier.predict(data)

    def __train_from_file_(self, file):
        """
        retrieves trainings data from a given csv file and trains each activity

        :param file: the file path to the csv file

        :return: void
        """

        trainings_data = TrainingsDataReader.get_trainings_data(file)

        self.__train_activity_(trainings_data[0], GESTURE_1, False)
        self.__train_activity_(trainings_data[1], GESTURE_2, False)
        self.__train_activity_(trainings_data[2], GESTURE_3)

    def __fit_data_to_svm_(self):
        """
        fits data to support vector machine

        :return: void
        """

        self.data_gesture_1_class.clear()
        self.data_gesture_2_class.clear()
        self.data_gesture_3_class.clear()

        data = []

        for item in it.chain(self.data_gesture_1, self.data_gesture_2,
                             self.data_gesture_3):
            data.append([item])

        [self.data_gesture_1_class.append(1)
         for i in range(0, len(self.data_gesture_1))]

        [self.data_gesture_2_class.append(2)
         for i in range(0, len(self.data_gesture_2))]

        [self.data_gesture_3_class.append(3)
         for i in range(0, len(self.data_gesture_3))]

        data_classes = self.data_gesture_1_class + self.data_gesture_2_class + \
            self.data_gesture_3_class

        self.classifier.fit(data, data_classes)

    def __perform_fft_(self, data):
        """
        performs fourier transformation on given data

        :param data: the data to be transformed

        :return: the fourier transformed data
        """
        return np.abs(np.fft.fft(data) / len(data))[1:int(len(data)/2)]

    def __train_activity_(self, data, activity, needs_fit=True):
        """
        trains a given activity

        :param data: the new trainings data for the activity
        :param activity: the identifier of the activity
        :param needs_fit: an optional boolean depicting the necessity for data
               fitting to the support vector machine

        :return: void
        """

        sum_vals = []

        for k in range(0, len(data)):
            sum_vals.append((data[k][0] + data[k][1] + data[k][2] -
                             3 * 512) / 3)

        if activity == GESTURE_1:
            self.data_gesture_1 = self.__perform_fft_(sum_vals)
        elif activity == GESTURE_2:
            self.data_gesture_2 = self.__perform_fft_(sum_vals)
        elif activity == GESTURE_3:
            self.data_gesture_3 = self.__perform_fft_(sum_vals)

        if needs_fit:
            self.__fit_data_to_svm_()

    def train(self, file_path, train_data, activity):
        """
        trains the classifier based on a csv file or separate activities based
        on given trainings data and the activity's name

        :param file_path: a path to a csv file
        :param train_data: a list of accelerometer values which are used for
                           training
        :param activity: the name of the activity

        :return: void
        """

        if file_path is not None and train_data is None:
            self.__train_from_file_(file_path)
        elif file_path is None and train_data is not None and \
                activity is not None:
            self.__train_activity_(train_data, activity)

        return self

    def classify(self, gesture_data):
        """
        classifies an action based on the given gesture data

        :param gesture_data: the data to be classified

        :return: the identifier of the classified activity
        """

        if self.__classify_gesture_1_(gesture_data):
            return GESTURE_1
        elif self.__classify_gesture_2_(gesture_data):
            return GESTURE_2
        elif self.__classify_gesture_3_(gesture_data):
            return GESTURE_3

        return NOTHING
