import numpy as np
import pdb

"""
This code was based off of code from cs231n at Stanford University, and modified for ece239as at UCLA.
"""
class SVM(object):
    
    def __init__(self, dims=[10, 3073]):
        self.init_weights(dims=dims)

    def init_weights(self, dims):
        """
        Initializes the weight matrix of the SVM.  Note that it has shape (C, D)
        where C is the number of classes and D is the feature size.
        """
        self.W = np.random.normal(size=dims)

    def loss(self, X, y):
        """
        Calculates the SVM loss.
      
        Inputs have dimension D, there are C classes, and we operate on minibatches
        of N examples.
      
        Inputs:
        - X: A numpy array of shape (N, D) containing a minibatch of data.
        - y: A numpy array of shape (N,) containing training labels; y[i] = c means
          that X[i] has label c, where 0 <= c < C.
      
        Returns a tuple of:
        - loss as single float
        """
  
        # compute the loss and the gradient
        num_classes = self.W.shape[0]
        num_train = X.shape[0]
        loss = 0.0

        for i in np.arange(num_train): #sum from 1 to m
            scores = np.dot(self.W, X[i]) #this is aj from lecture notes
            correct_score = scores[y[i]] #this is ay from leture notes
            for j in np.arange(num_classes): #this is the inner sum over the number of classes
                if j == y[i]: #check j!=y[i] as this is not inlcuded in the sum as per lecture notes
                    continue
                margin = 1 + scores[j] - correct_score #rightside arugment in max function
                if margin > 0: #this means there is some loss else the max would return 0. 
                    loss += margin
                  
        loss /= num_train #divide by m as per loss function in lecture notes. 
                    
        
        # ================================================================ #
        # YOUR CODE HERE:
        #   Calculate the normalized SVM loss, and store it as 'loss'.
        #   (That is, calculate the sum of the losses of all the training 
        #   set margins, and then normalize the loss by the number of 
        #   training examples.)
        # ================================================================ 
        
        # ================================================================ #
        # END YOUR CODE HERE
        # ================================================================ #
    
        return loss
      
    def loss_and_grad(self, X, y):
        """
        Same as self.loss(X, y), except that it also returns the gradient.
    
        Output: grad -- a matrix of the same dimensions as W containing 
            the gradient of the loss with respect to W.
        """
      
        # compute the loss and the gradient
        num_classes = self.W.shape[0]
        num_train = X.shape[0]
        loss = 0.0
        grad = np.zeros_like(self.W)
    
        for i in np.arange(num_train):
            scores = np.dot(self.W, X[i])
            ay = scores[y[i]]
            for j in np.arange(num_classes):
                if j == y[i]:
                    continue
                margin = 1 + scores[j] - ay
                if margin > 0:
                    loss += margin
                    grad[j,:] += X[i] #if zj > 0, then the subgradient is X[i] for that value of j.
                    grad[y[i], :] += -X[i] #similarly if zj>0, then subgradient with respect to wy is X[i] for that j. 
                
                        
                        
        # ================================================================ #
        # YOUR CODE HERE:
        #   Calculate the SVM loss and the gradient.  Store the gradient in
        #   the variable grad.
        # ================================================================ 
    
        # ================================================================ #
        # END YOUR CODE HERE
        # ================================================================ #
    
        loss /= num_train
        grad /= num_train
    
        return loss, grad
    
    def grad_check_sparse(self, X, y, your_grad, num_checks=10, h=1e-5):
        """
        sample a few random elements and only return numerical
        in these dimensions.
        """
      
        for i in np.arange(num_checks):
            ix = tuple([np.random.randint(m) for m in self.W.shape])

        oldval = self.W[ix]
        self.W[ix] = oldval + h # increment by h
        fxph = self.loss(X, y)
        self.W[ix] = oldval - h # decrement by h
        fxmh = self.loss(X,y) # evaluate f(x - h)
        self.W[ix] = oldval # reset
  
        grad_numerical = (fxph - fxmh) / (2 * h)
        grad_analytic = your_grad[ix]
        rel_error = abs(grad_numerical - grad_analytic) / (abs(grad_numerical) + abs(grad_analytic))
        print('numerical: %f analytic: %f, relative error: %e' % (grad_numerical, grad_analytic, rel_error))

    def fast_loss_and_grad(self, X, y):
        """
        A vectorized implementation of loss_and_grad. It shares the same
        inputs and ouptuts as loss_and_grad.
        """
        loss = 0.0
        grad = np.zeros(self.W.shape) # initialize the gradient as zero
  
        # ================================================================ #
        # YOUR CODE HERE:
        #   Calculate the SVM loss WITHOUT any for loops.
        # ================================================================ #
        num_train = X.shape[0]
        #Array of shape (D, C) containing scores
        scores = np.dot(X, self.W.T)
        #read correct scores in a vector of height N
        correct_score = scores[list(range(num_train)), y]
        correct_score = correct_score.reshape(num_train, -1)
        # subtract correct scores from score matrix and add margin
        scores += 1 - correct_score
        # make sure correct scores themselves don't contribute to loss function
        scores[list(range(num_train)), y] = 0
        #construct loss function
        loss = np.sum(np.fmax(scores, 0)) / num_train
        
        # ================================================================ #
        # END YOUR CODE HERE
        # ================================================================ #


        # ================================================================ #
        # YOUR CODE HERE:
        #   Calculate the SVM grad WITHOUT any for loops.
        # ================================================================ #
        
        X_mask = np.zeros(scores.shape)
        X_mask[scores > 0] = 1
        X_mask[np.arange(num_train), y] = -np.sum(X_mask, axis = 1)
        grad = X.T.dot(X_mask).T
        grad /= num_train
        
        # ================================================================ #
        # END YOUR CODE HERE
        # ================================================================ #

        return loss, grad
    
    def train(self, X, y, learning_rate=1e-3, num_iters=100,
            batch_size=200, verbose=False):
        """
        Train this linear classifier using stochastic gradient descent.
    
        Inputs:
        - X: A numpy array of shape (N, D) containing training data; there are N
          training samples each of dimension D.
        - y: A numpy array of shape (N,) containing training labels; y[i] = c
          means that X[i] has label 0 <= c < C for C classes.
        - learning_rate: (float) learning rate for optimization.
        - num_iters: (integer) number of steps to take when optimizing
        - batch_size: (integer) number of training examples to use at each step.
        - verbose: (boolean) If true, print progress during optimization.

        Outputs:
        A list containing the value of the loss function at each training iteration.
        """
        
        num_train, dim = X.shape
        num_classes = np.max(y) + 1 # assume y takes values 0...K-1 where K is number of classes
    
        self.init_weights(dims=[np.max(y) + 1, X.shape[1]])	# initializes the weights of self.W
    
        # Run stochastic gradient descent to optimize W
        loss_history = []

        for it in np.arange(num_iters):

           # ================================================================ #
           # YOUR CODE HERE:
           #   Sample batch_size elements from the training data for use in 
           #   gradient descent.  After sampling,
           #     - X_batch should have shape: (dim, batch_size)
           #     - y_batch should have shape: (batch_size,)
           #   The indices should be randomly generated to reduce correlations
           #   in the dataset.  Use np.random.choice.  It's okay to sample with
           #   replacement.
           # ================================================================ #
            indices = np.random.choice(num_train, batch_size, replace = True)
            X_batch = X[indices,:]
            y_batch = y[indices]
           # ================================================================ #
           # END YOUR CODE HERE
           # ================================================================ #

           # evaluate loss and gradient
            loss, grad = self.fast_loss_and_grad(X_batch, y_batch)
            loss_history.append(loss)

          # ================================================================ #
          # YOUR CODE HERE:
          #   Update the parameters, self.W, with a gradient step 
          # ================================================================ #
            self.W = self.W - learning_rate*grad
          # ================================================================ #
          # END YOUR CODE HERE
          # ================================================================ #

            if verbose and it % 100 == 0:
                print('iteration {} / {}: loss {}'.format(it, num_iters, loss))

        return loss_history

    def predict(self, X):
        """
        Inputs:
        - X: N x D array of training data. Each row is a D-dimensional point.

        Returns:
        - y_pred: Predicted labels for the data in X. y_pred is a 1-dimensional
          array of length N, and each element is an integer giving the predicted
          class.
        """
        y_pred = np.zeros(X.shape[0])


        # ================================================================ #
        # YOUR CODE HERE:
        #   Predict the labels given the training data with the parameter self.W.
        # ================================================================ #
        scores = np.dot(self.W, X.T)
        y_pred = np.argmax(scores, axis = 0)
        # ================================================================ #
        # END YOUR CODE HERE
        # ================================================================ #

        return y_pred

