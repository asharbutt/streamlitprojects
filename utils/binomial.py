import numpy as np

class european_binomial:

    def __init__(self, steps, vol, spot, strike, t,option_type, r):
        self.steps = steps+1 # We start off at 0,0 and then have x additional steps from that
        self.initial_spot = spot
        self.time_step = t / steps
        self.strike = strike
        self.asset_matrix = np.zeros((self.steps,self.steps))
        self.option_matrix = np.zeros((self.steps,self.steps))
        if option_type=='call': self.option_flag = 1
        else: self.option_flag = -1
        self.up = np.exp(vol*np.sqrt(self.time_step))
        self.down = pow(self.up,-1)
        self.probability = (np.exp(r*self.time_step)-self.down)/(self.up - self.down)
        self.discount_factor = np.exp(-r*self.time_step)

    def run_tree(self):
        # Compute the asset matrix first:
        self.asset_matrix[0,0] = self.initial_spot
        print(self.probability)

        for j in range(1, self.steps):
            for i in range(0,self.steps):
                if i == 0:
                        self.asset_matrix[i,j] = self.asset_matrix[i,j-1]*self.up
                else:
                    self.asset_matrix[i,j] = self.asset_matrix[i-1,j-1]*self.down

        print("Asset Matrix: ")
        print(self.asset_matrix)

        # Now we calculate the option value, starting off from the end and working backwards:
        self.option_matrix[:,-1] = np.maximum(self.option_flag*(self.asset_matrix[:,-1]-self.strike),0)

        for j in range(self.steps-2, 0, -1):
            for i in range(0, self.steps-1):
                if i > j:
                    break
                self.option_matrix[i,j] = self.discount_factor * (self.option_matrix[i,j+1] * self.probability + self.option_matrix[i+1,j+1] * (1 - self.probability))

        self.option_matrix[0, 0] = self.discount_factor * (self.option_matrix[0,  1] * self.probability + self.option_matrix[1, 1] * (1 - self.probability))
        return self.option_matrix[0, 0]
