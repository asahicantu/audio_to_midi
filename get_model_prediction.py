from keras.models import load_model
from models import pickle_if_not_pickled, reshape_for_dense, split, root_mse
import numpy as np
import matplotlib.pyplot as plt
from normalisation import *
import random
random.seed(21)
#TODO: Figure out how to set random seed as global var for whole project (I believe it gets reset every time random is imported

def get_model_prediction(model, cqt_segment_reshaped, midi_true):
    midi_prediction = model.predict(cqt_segment_reshaped)
    midi_prediction_rounded = np.rint(midi_prediction)
    midi_prediction_unflattened = np.reshape(midi_prediction_rounded, (87, 6))
    midi_true_unflattened = np.reshape(midi_true, (87, 6))
    print(midi_true_unflattened.max)
    #TODO: Explore imshow params
    plt.imshow(midi_prediction_unflattened, cmap='hot', interpolation='nearest')
    plt.show()
    plt.imshow(midi_true_unflattened, cmap='hot', interpolation='nearest')
    plt.show()
    # in the midi_prediction as is, the nums in the array are not probabilities (exactly) more
    # like an indication of whether or not the value should be a 0 or 1 (ie .52 is probably a 1,
    # .01 is probably a 0)

def main():
    model = load_model('model_checkpoints/weights-improvement-50-0.1813_val_loss.192.hdf5', custom_objects={'root_mse': root_mse})
    #TODO: Make load model input an arg
    cqt_segments, midi_segments = pickle_if_not_pickled()
    cqt_segments_reshaped, midi_segments_reshaped = reshape_for_dense(cqt_segments, midi_segments)
    cqt_train, cqt_valid, cqt_test, midi_train, midi_valid, midi_test = split(
        cqt_segments_reshaped, midi_segments_reshaped)
    array_shaped_for_scaler, num_samples, height, width = shape_for_scaler(cqt_train)
    scaler = create_scaler(array_shaped_for_scaler)
    cqt_train_standardized = feature_standardize_array(array_shaped_for_scaler, scaler, num_samples, height, width)
    cqt_valid_shaped_for_scaler, num_valid_samples, height, width = shape_for_scaler(cqt_valid)
    cqt_valid_standardized = feature_standardize_array(cqt_valid_shaped_for_scaler, scaler, num_valid_samples, height,
                                                       width)
    cqt_test_shaped_for_scaler, num_test_samples, height, width = shape_for_scaler(cqt_test)
    cqt_test_standardized = feature_standardize_array(cqt_test_shaped_for_scaler, scaler, len(cqt_test), height, width)
    num_validation_samples = len(cqt_valid_standardized)
    random_index = np.random.randint(num_validation_samples)
    example_cqt_segment = cqt_valid_standardized[random_index]
    midi_true = midi_valid[random_index]
    num_examples = 1
    input_height, input_width = example_cqt_segment.shape
    example_cqt_segment_reshaped = example_cqt_segment.reshape(num_examples, input_height, input_width)
    get_model_prediction(model, example_cqt_segment_reshaped, midi_true)

if __name__ == '__main__':
    main()