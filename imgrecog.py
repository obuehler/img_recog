__author__ = 'buehleo01'
# Largely based on the tutorial found here: http://www.pyimagesearch.com/2014/09/22/getting-started-deep-learning-python
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
from sklearn import datasets, preprocessing
from nolearn.dbn import DBN
import numpy as np
import matplotlib.pyplot as plt
import Image
import pickle

def MNISTify(img):
    """Converts image located at impath to greyscale, resizes, flattens, pads, and normalizes it to match MNIST.
    Assumes text is dark-on-light.

    See http://ufldl.stanford.edu/wiki/index.php/Data_Preprocessing for improvement ideas.
    """
    if isinstance(img, str):  # Open if we were passed a file
        img = Image.open(img)
    img = img.convert('L').resize((20, 20), Image.ANTIALIAS)
    imgpmap = img.load()
    paddedimg = Image.new('L', (28,28), 0)
    padpmap = paddedimg.load()

    # Center (20,20) character image in black (28,28) image
    x = 0
    while x < 20:
        y = 0
        while y < 20:
            imgpixel = imgpmap[x,y]
            padpmap[x+4,y+4] = 0 if imgpixel > 200 else 1-(imgpixel/255)  # Invert colors and normalize while we're here
            y += 1
        x += 1

    img_np = np.asarray(paddedimg)

#    norm_img_np = img_np  # Normalize, DBN only understands 0.0-1.0
    topredict = np.array([np.atleast_2d(img_np).flatten()])
    return topredict

def MNISTify1(impath):  # ~20% Accurate
    # Convert to greyscale, resize, flatten and normalize to match MNIST
    img = Image.open(impath).convert('1').resize((20, 20), Image.ANTIALIAS)
    bw = img.point(lambda x: 0 if x<140 else 255, '1')
    img_np = np.asarray(bw).flatten()
    img_np = np.pad(img_np, 192, mode='constant', constant_values=0)
    norm_img_np = img_np/255  # Normalize, DBN only understands 0.0-1.0
    topredict = np.atleast_2d(norm_img_np)
    return topredict

def make_DBN():
    """Creates A Deep Belief network for recognizing handwritten digits and pickles it
    so we can use it persistently without rebuilding it from scratch every run"""
    dataset = datasets.fetch_mldata("MNIST Original")  # mnist original, uci 20070111 letter, datasets uci letter

    # Split our easy dataset so we can use it to train the DBN
    (trainX, testX, trainY, testY) = train_test_split(dataset.data/float(dataset.data.max()),  # DBM only understands 0.0-1.0
                                                      dataset.target.astype("int0"),
                                                      test_size=0.33)

    # Make Deep Belief Network
    dbn = DBN(
        # [nodes in input layer (pixel size of vectorized dataset),
        # nodes in hidden layer(s),
        # nodes in output layer (size of output dataset)]
        [trainX.shape[1], 1000, 300, 10],  # out = 10,
        learn_rates=0.3,
        learn_rate_decays=0.9,
        epochs=10,
        verbose=1
    )
    # Teach DBM to recognize digits
    dbn.fit(trainX, trainY)

    # Predict using our test set
    preds = dbn.predict(testX)
#    print classification_report(testY, preds)


    # Examine random selection from our test set
    for i in np.random.choice(np.arange(0, len(testY)), size=(100,)):
        # Classify actual digit
        pred = dbn.predict(np.atleast_2d(testX[i]))

        # Reshape to 28x28
        image = (testX[i] * 255).reshape((28,28)).astype('uint8')

        # Show image and prediction
        seen = pred[0]
        actual = testY[i]
        if seen != actual:
            print "Actual digit is {0}, saw {1}".format(actual, seen)
    #        plt.imshow(image)
    #        plt.show()

    with open('dbn.pickle', 'wb') as f:
        pickle.dump(dbn, f)

def recognize(image):
    with open('dbn.pickle', 'rb') as f:
        dbn = pickle.load(f)

    topredict = MNISTify(image)
    pred = dbn.predict(topredict)
    return pred



if __name__ == "__main__":
    print 'starting'
    with open('dbn.pickle', 'rb') as f:
        dbn = pickle.load(f)

    # Examine actual image
    files = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    for f in files:
        topredict = MNISTify('C:\Users\\buehleo01\Pictures\\{0}.png'.format(f))
        imagearray = topredict.reshape((28,28))
        print imagearray
        Image.fromarray(imagearray).save(f + '.png')
    #    plt.imshow(topredict)
        pred = dbn.predict(topredict)
        seen = pred[0]
        print "Expected: {0}. I see {1}".format(f,seen)

